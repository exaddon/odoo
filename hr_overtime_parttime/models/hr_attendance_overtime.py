from odoo import models, fields, api
from odoo.exceptions import UserError

class HrAttendanceOvertime(models.Model):
    _inherit = 'hr.attendance.overtime'

    @api.depends('employee_id', 'date', 'worked_hours')
    def _compute_duration(self):
        """Override overtime computation to respect part-time and planned hours"""
        for rec in self:
            if not rec.employee_id:
                rec.duration = 0.0
                continue

            calendar = rec.employee_id.resource_calendar_id
            if not calendar:
                rec.duration = 0.0
                continue

            # Compute expected hours for this specific day
            expected_hours = calendar.get_work_hours_count(
                start_dt=rec.date,
                end_dt=rec.date + fields.Date.timedelta(days=1),
                resource_id=rec.employee_id.id
            )

            # Overtime = worked hours - expected hours
            rec.duration = max(rec.worked_hours - expected_hours, 0.0)

    def recompute_all_overtime(self):
        """Recompute duration for all existing overtime records"""
        for rec in self.search([]):
            rec._compute_duration()
        return True
