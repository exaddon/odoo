# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class HrAttendanceOvertime(models.Model):
    _name = "hr.attendance.overtime"
    _description = "Attendance Overtime"
    _rec_name = 'employee_id'
    _order = 'date desc'

    def _default_employee(self):
        return self.env.user.employee_id

    employee_id = fields.Many2one(
        'hr.employee', string="Employee", default=_default_employee,
        required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='employee_id.company_id', store=True)
    date = fields.Date(string='Day')
    duration = fields.Float(string='Extra Hours', default=0.0, required=True)
    duration_real = fields.Float(
        string='Extra Hours (Real)', default=0.0,
        help="Extra-hours including thresholds")
    adjustment = fields.Boolean(default=False)

    def init(self):
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS hr_attendance_overtime_unique_employee_per_day
            ON %s (employee_id, date)
            WHERE adjustment is false
        """ % (self._table))

    @api.model
    def recompute_all_overtime(self):
        """
        Recompute all historical overtime using standard Odoo logic.
        This updates duration and duration_real for all employees.
        """
        attendance_model = self.env['hr.attendance']
        employees = self.env['hr.employee'].search([])

        for emp in employees:
            # get all attendance records for this employee
            attendances = attendance_model.search([('employee_id', '=', emp.id)])
            if not attendances:
                continue

            # build the {employee: set((datetime, date))} dict as _update_overtime expects
            attendance_dates = {emp: set()}
            for att in attendances:
                day_start, day_date = att._get_day_start_and_day(emp, att.check_in)
                attendance_dates[emp].add((day_start, day_date))
                if att.check_out:
                    day_start_out, day_date_out = att._get_day_start_and_day(emp, att.check_out)
                    attendance_dates[emp].add((day_start_out, day_date_out))

            # call standard Odoo method to recompute overtime
            attendances._update_overtime(attendance_dates)

        return True
