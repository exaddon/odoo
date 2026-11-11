# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.exceptions import ValidationError


class HrAttendanceMonitor(HrAttendance):

    @http.route('/hr_attendance/systray_check_in_out', type="jsonrpc", auth="user")
    def systray_attendance(self, latitude=False, longitude=False):
        employee = request.env.user.with_company(self._get_active_company(request)).employee_id
        today = fields.Date.today()

        # Block check-in/out from the systray while on a validated full-day leave (same rule as 17.0)
        leave = request.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),
            ('date_from', '<=', today),
            ('date_to', '>=', today),
        ], limit=1)
        if leave and leave.number_of_days >= 1:
            raise ValidationError(_("You can't check-in as you are on leave."))

        return super().systray_attendance(latitude=latitude, longitude=longitude)
