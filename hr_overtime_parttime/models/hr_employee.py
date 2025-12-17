from odoo import models, fields, api
from odoo.tools.float_utils import float_round

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    overtime_ids = fields.One2many('hr.attendance.overtime', 'employee_id')
    total_overtime = fields.Float(compute='_compute_total_overtime', compute_sudo=True)

    @api.depends('overtime_ids.duration')
    def _compute_total_overtime(self):
        for employee in self:
            employee.total_overtime = float_round(sum(employee.overtime_ids.mapped('duration')), 2)
