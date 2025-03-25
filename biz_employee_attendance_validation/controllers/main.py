# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
from odoo.http import request
from odoo.addons.hr_attendance.controllers.main import HrAttendance
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class HrAttendanceMonitor(HrAttendance):

    @http.route('/hr_attendance/systray_check_in_out', type="json", auth="user")
    def systray_attendance(self, latitude=False, longitude=False):
        employee = request.env.user.employee_id
        today = fields.Date.today()

        # Check if the employee is on full-day leave today
        leave = request.env['hr.leave'].search([
            ('employee_id', '=', employee.id),
            ('state', '=', 'validate'),  
            ('date_from', '<=', today),
            ('date_to', '>=', today),
        ], limit=1)

        if leave and leave.number_of_days >= 1:  
            raise ValidationError(_("You can't check-in as you are on leave."))
        
        else:
            geo_ip_response = self._get_geoip_response(mode='systray',
                                                    latitude=latitude,
                                                    longitude=longitude)
            employee._attendance_action_change(geo_ip_response)
            return self._get_employee_info_response(employee)

        