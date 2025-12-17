from odoo import models, fields

class HrAttendanceOvertime(models.Model):
    _name = "hr.attendance.overtime"
    _description = "Attendance Overtime"
    _rec_name = 'employee_id'
    _order = 'date desc'

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade', index=True)
    company_id = fields.Many2one(related='employee_id.company_id')
    date = fields.Date(string='Day', required=True)
    duration = fields.Float(string='Extra Hours', default=0.0, required=True)
    adjustment = fields.Boolean(default=False)

    def init(self):
        # Ensure only one overtime record per employee per day (except adjustments)
        self.env.cr.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS hr_attendance_overtime_unique_employee_per_day
            ON %s (employee_id, date)
            WHERE adjustment IS FALSE
        """ % (self._table))
