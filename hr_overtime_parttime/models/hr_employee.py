# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, time
import pytz
from odoo.tools.float_utils import float_round

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    overtime_ids = fields.One2many('hr.attendance.overtime', 'employee_id', string="Overtime Records")
    total_overtime = fields.Float(string="Total Overtime", compute="_compute_total_overtime", store=True, compute_sudo=True)

    @api.depends('attendance_ids.worked_hours', 'resource_calendar_id', 'contract_id.date_start')
    def _compute_total_overtime(self):
        Attendance = self.env['hr.attendance']

        for emp in self:
            if not emp.contract_id or not emp.contract_id.date_start:
                emp.total_overtime = 0.0
                continue

            tz = pytz.timezone(emp.resource_calendar_id.tz or 'UTC')

            start = datetime.combine(emp.contract_id.date_start, time.min)
            start = tz.localize(start)
            end = datetime.utcnow()
            end = pytz.utc.localize(end).astimezone(tz)

            attendances = Attendance.search([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', start.astimezone(pytz.utc)),
                ('check_out', '<=', end.astimezone(pytz.utc)),
            ])
            worked_hours = sum(att.worked_hours or 0 for att in attendances)

            intervals = emp.resource_calendar_id._work_intervals_batch(
                start, end, resources=emp.resource_id
            ).get(emp.resource_id.id, [])

            expected_hours = sum((i[1] - i[0]).total_seconds() / 3600.0 for i in intervals)
            emp.total_overtime = float_round(worked_hours - expected_hours, 2)
