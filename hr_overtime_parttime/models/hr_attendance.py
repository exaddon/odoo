# -*- coding: utf-8 -*-
# Part of custom Odoo module for HR Overtime
# See LICENSE file for full copyright and licensing details.

import pytz
from collections import defaultdict
from datetime import datetime, timedelta
from pytz import timezone

from odoo.http import request
from odoo import models, fields, api, exceptions, _
from odoo.addons.resource.models.utils import Intervals


def get_google_maps_url(latitude, longitude):
    return "https://maps.google.com?q=%s,%s" % (latitude, longitude)


class HrAttendance(models.Model):
    _inherit = "hr.attendance"  # <--- Extend existing model
    _description = "Attendance Overtime Extension"

    # New fields
    overtime_hours = fields.Float(string="Over Time", compute='_compute_overtime_hours', store=True)
    in_latitude = fields.Float(string="Latitude", digits=(10, 7), readonly=True)
    in_longitude = fields.Float(string="Longitude", digits=(10, 7), readonly=True)
    in_country_name = fields.Char(string="Country", help="Based on IP Address", readonly=True)
    in_city = fields.Char(string="City", readonly=True)
    in_ip_address = fields.Char(string="IP Address", readonly=True)
    in_browser = fields.Char(string="Browser", readonly=True)
    in_mode = fields.Selection([('kiosk', "Kiosk"), ('systray', "Systray"), ('manual', "Manual")], default='manual', readonly=True)
    out_latitude = fields.Float(digits=(10, 7), readonly=True)
    out_longitude = fields.Float(digits=(10, 7), readonly=True)
    out_country_name = fields.Char(help="Based on IP Address", readonly=True)
    out_city = fields.Char(readonly=True)
    out_ip_address = fields.Char(readonly=True)
    out_browser = fields.Char(readonly=True)
    out_mode = fields.Selection([('kiosk', "Kiosk"), ('systray', "Systray"), ('manual', "Manual")], default='manual', readonly=True)

    @api.depends('worked_hours')
    def _compute_overtime_hours(self):
        """Compute the overtime hours for each attendance based on hr.attendance.overtime"""
        att_progress_values = dict()
        negative_overtime_attendances = defaultdict(lambda: False)
        if self.employee_id:
            self.env['hr.attendance'].flush_model(['worked_hours'])
            self.env['hr.attendance.overtime'].flush_model(['duration'])
            self.env.cr.execute('''
                WITH employee_time_zones AS (
                    SELECT employee.id AS employee_id,
                           calendar.tz AS timezone
                      FROM hr_employee employee
                INNER JOIN resource_calendar calendar
                        ON calendar.id = employee.resource_calendar_id
                )
                SELECT att.id AS att_id,
                       att.worked_hours AS att_wh,
                       ot.id AS ot_id,
                       ot.duration AS ot_d,
                       ot.date AS od,
                       att.check_in AS ad
                  FROM hr_attendance att
            INNER JOIN employee_time_zones etz
                    ON att.employee_id = etz.employee_id
                   LEFT JOIN hr_attendance_overtime ot
                    ON date_trunc('day',
                                  CAST(att.check_in
                                           AT TIME ZONE 'utc'
                                           AT TIME ZONE etz.timezone
                                  as date)) = date_trunc('day', ot.date)
                   AND att.employee_id = ot.employee_id
                   AND (ot.adjustment IS false OR ot.adjustment IS NULL)
              ORDER BY att.check_in DESC
            ''')
            rows = self.env.cr.dictfetchall()
            grouped_dict = dict()
            for row in rows:
                if row['ot_id'] and row['att_wh']:
                    if row['ot_id'] not in grouped_dict:
                        grouped_dict[row['ot_id']] = {'attendances': [(row['att_id'], row['att_wh'])], 'overtime_duration': row['ot_d']}
                    else:
                        grouped_dict[row['ot_id']]['attendances'].append((row['att_id'], row['att_wh']))

            for overtime in grouped_dict:
                overtime_reservoir = grouped_dict[overtime]['overtime_duration']
                if overtime_reservoir > 0:
                    for attendance in grouped_dict[overtime]['attendances']:
                        if overtime_reservoir > 0:
                            sub_time = attendance[1] - overtime_reservoir
                            if sub_time < 0:
                                att_progress_values[attendance[0]] = 0
                                overtime_reservoir -= attendance[1]
                            else:
                                att_progress_values[attendance[0]] = float(((attendance[1] - overtime_reservoir) / attendance[1]) * 100)
                                overtime_reservoir = 0
                        else:
                            att_progress_values[attendance[0]] = 100
                elif overtime_reservoir < 0 and grouped_dict[overtime]['attendances']:
                    att_id = grouped_dict[overtime]['attendances'][0][0]
                    att_progress_values[att_id] = overtime_reservoir
                    negative_overtime_attendances[att_id] = True
        for attendance in self:
            if negative_overtime_attendances[attendance.id]:
                attendance.overtime_hours = att_progress_values.get(attendance.id, 0)
            else:
                attendance.overtime_hours = attendance.worked_hours * ((100 - att_progress_values.get(attendance.id, 100)) / 100)

    def _get_attendances_dates(self):
        """Helper to gather employee attendance dates for overtime recalculation"""
        from datetime import datetime
        from collections import defaultdict
        attendances_emp = defaultdict(set)
        for attendance in self.filtered(lambda a: a.employee_id.company_id.hr_attendance_overtime and a.check_in):
            check_in_day_start = attendance.check_in.replace(hour=0, minute=0, second=0, microsecond=0)
            attendances_emp[attendance.employee_id].add((check_in_day_start, check_in_day_start.date()))
            if attendance.check_out:
                check_out_day_start = attendance.check_out.replace(hour=0, minute=0, second=0, microsecond=0)
                attendances_emp[attendance.employee_id].add((check_out_day_start, check_out_day_start.date()))
        return attendances_emp

    def _update_overtime(self, employee_attendance_dates=None):
        """Recalculate overtime for given employee attendance dates"""
        if employee_attendance_dates is None:
            employee_attendance_dates = self._get_attendances_dates()

        overtime_to_unlink = self.env['hr.attendance.overtime']
        overtime_vals_list = []

        for emp, attendance_dates in employee_attendance_dates.items():
            for day_data in attendance_dates:
                day = day_data[0]
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '>=', day),
                    ('check_in', '<', day + timedelta(days=1))
                ])
                total_hours = sum(att.worked_hours or 0 for att in attendances)

                overtime = self.env['hr.attendance.overtime'].sudo().search([
                    ('employee_id', '=', emp.id),
                    ('date', '=', day_data[1]),
                    ('adjustment', '=', False),
                ])
                if total_hours > 0:
                    if not overtime:
                        overtime_vals_list.append({
                            'employee_id': emp.id,
                            'date': day_data[1],
                            'duration': total_hours,
                        })
                    else:
                        overtime.sudo().write({'duration': total_hours})
                elif overtime:
                    overtime_to_unlink |= overtime

        self.env['hr.attendance.overtime'].sudo().create(overtime_vals_list)
        overtime_to_unlink.sudo().unlink()
