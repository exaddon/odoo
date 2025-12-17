from odoo import models, fields, api
from odoo.osv.expression import AND, OR
from odoo.tools.float_utils import float_is_zero
from collections import defaultdict

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    overtime_hours = fields.Float(string="Over Time", compute='_compute_overtime_hours', store=True)

    @api.depends('worked_hours', 'employee_id')
    def _compute_overtime_hours(self):
        # Update overtime_hours based on hr.attendance.overtime
        for attendance in self:
            overtime_records = self.env['hr.attendance.overtime'].search([
                ('employee_id', '=', attendance.employee_id.id),
                ('date', '=', attendance.check_in.date())
            ])
            total_overtime = sum(o.duration for o in overtime_records)
            attendance.overtime_hours = total_overtime

    def _update_overtime(self):
        """Recalculate all overtime records for this employee."""
        employee_attendance_dates = defaultdict(set)
        for att in self:
            if att.check_in:
                employee_attendance_dates[att.employee_id].add(att.check_in.date())

        for emp, dates in employee_attendance_dates.items():
            for day in dates:
                attendances = self.env['hr.attendance'].search([
                    ('employee_id', '=', emp.id),
                    ('check_in', '>=', day),
                    ('check_in', '<', day + fields.timedelta(days=1))
                ])
                total_hours = sum(att.worked_hours or 0 for att in attendances)
                overtime_record = self.env['hr.attendance.overtime'].search([
                    ('employee_id', '=', emp.id),
                    ('date', '=', day),
                    ('adjustment', '=', False)
                ])
                if overtime_record:
                    overtime_record.write({'duration': total_hours})
                else:
                    if total_hours > 0:
                        self.env['hr.attendance.overtime'].create({
                            'employee_id': emp.id,
                            'date': day,
                            'duration': total_hours,
                            'duration_real': total_hours
                        })

    def create(self, vals_list):
        res = super().create(vals_list)
        res._update_overtime()
        return res

    def write(self, vals):
        res = super().write(vals)
        self._update_overtime()
        return res

    def unlink(self):
        res = super().unlink()
        self._update_overtime()
        return res
