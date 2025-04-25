# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)
 

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            check_in = vals.get('check_in')
            employee_id = vals.get('employee_id')
            if check_in and employee_id:
                check_in_date = fields.Date.to_date(check_in)
                employee = self.env['hr.employee'].browse(employee_id)
                if self._is_employee_on_leave(employee, check_in_date):
                    raise ValidationError(_("You cannot check in while on leave."))
        return super(HrAttendance, self).create(vals_list)

    def write(self, vals):
        for record in self:
            check_in = vals.get('check_in') or record.check_in
            if check_in:
                check_in_date = fields.Date.to_date(check_in)
                if self._is_employee_on_leave(record.employee_id, check_in_date):
                    raise ValidationError(_("You cannot check in while on leave."))
        return super(HrAttendance, self).write(vals)

    def _is_employee_on_leave(self, employee, date):
        leave = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', date),
            ('date_to', '>=', date)
        ], limit=1)
        return bool(leave)