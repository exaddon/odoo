# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, exceptions, _
from datetime import timedelta
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)
 

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model_create_multi
    def create(self, vals):
        for vals in vals:  
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            if vals.get('check_in') and self._is_employee_on_leave(employee):
                raise exceptions.ValidationError(_("You cannot check in while on leave."))
        return super(HrAttendance, self).create(vals)  


    def write(self, vals):
        for record in self:
            if 'check_in' in vals or 'check_out' in vals:
                if self._is_employee_on_leave(record.employee_id):
                    raise exceptions.ValidationError(_("You cannot check in while on leave."))
        return super(HrAttendance, self).write(vals)

    def _is_employee_on_leave(self, employee):
        today = fields.Date.today()
        leave = self.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('request_date_from', '<=', today),
            ('request_date_to', '>=', today)
        ], limit=1)
        return bool(leave)