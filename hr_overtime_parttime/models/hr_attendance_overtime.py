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
        help="Extra-hours including the threshold duration")
    adjustment = fields.Boolean(default=False)

    def init(self):
        # Allows only 1 overtime record per employee per day unless it's an adjustment
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS hr_attendance_overtime_unique_employee_per_day
            ON %s (employee_id, date)
            WHERE adjustment is false
        """ % (self._table))

    @api.model
    def recompute_all_overtime(self):
        """
        Safely recompute duration and duration_real for all existing overtime records
        by calling the standard _update_overtime method on hr.attendance records.
        """
        all_attendances = self.env['hr.attendance'].search([])
        for attendance in all_attendances:
            attendance._update_overtime()
        return True
