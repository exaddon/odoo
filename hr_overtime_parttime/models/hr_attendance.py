from odoo import models, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.mapped('employee_id')._recompute_total_overtime()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(k in vals for k in ('check_in', 'check_out', 'employee_id')):
            self.mapped('employee_id')._recompute_total_overtime()
        return res

    def unlink(self):
        employees = self.mapped('employee_id')
        res = super().unlink()
        employees._recompute_total_overtime()
        return res
