from odoo import models, fields, api, exceptions
from collections import defaultdict
from datetime import timedelta

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    def write(self, vals):
        res = super().write(vals)
        if 'check_out' in vals:
            # Recalculate overtime when check_out is updated
            for attendance in self.filtered('employee_id'):
                attendance._update_overtime_for_employee(attendance.employee_id)
        return res

    def _update_overtime_for_employee(self, employee):
        """Recalculate overtime per day for a single employee."""
        HrAttendanceOvertime = self.env['hr.attendance.overtime']

        # Get all attendances for the employee
        attendances = self.search([('employee_id', '=', employee.id), ('check_in', '!=', False), ('check_out', '!=', False)])
        daily_hours = defaultdict(float)

        # Group worked hours by day
        for att in attendances:
            day = att.check_in.date()
            daily_hours[day] += att.worked_hours or 0.0

        # Calculate expected hours per day from employee's calendar
        calendar = employee.resource_calendar_id or employee.company_id.resource_calendar_id
        if not calendar:
            return  # no calendar to compute expected hours

        # Compute expected daily hours (simplifying: same hours every day)
        expected_hours_per_day = calendar.hours_per_day if hasattr(calendar, 'hours_per_day') else 8.0

        # Update or create overtime records
        for day, worked in daily_hours.items():
            extra_hours = worked - expected_hours_per_day
            overtime_record = HrAttendanceOvertime.sudo().search([
                ('employee_id', '=', employee.id),
                ('date', '=', day),
                ('adjustment', '=', False)
            ], limit=1)

            if extra_hours != 0:
                if overtime_record:
                    overtime_record.sudo().write({'duration': extra_hours})
                else:
                    HrAttendanceOvertime.sudo().create({
                        'employee_id': employee.id,
                        'date': day,
                        'duration': extra_hours
                    })
            elif overtime_record:
                overtime_record.sudo().unlink()
