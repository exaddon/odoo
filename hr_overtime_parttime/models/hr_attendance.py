# -*- coding: utf-8 -*-
# Part of custom Odoo module for HR Overtime
# See LICENSE file for full copyright and licensing details.

import pytz
from collections import defaultdict
from datetime import datetime, timedelta
from operator import itemgetter

from odoo import models, fields, api, exceptions, _
from odoo.addons.resource.models.utils import Intervals
from odoo.http import request
from odoo.tools import format_duration, format_time

def get_google_maps_url(latitude, longitude):
    return f"https://maps.google.com?q={latitude},{longitude}"

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    overtime_hours = fields.Float(string="Overtime Hours", compute="_compute_overtime_hours", store=True)

    @api.depends('worked_hours')
    def _compute_overtime_hours(self):
        """Compute overtime hours per attendance using hr.attendance.overtime records."""
        AttendanceOvertime = self.env['hr.attendance.overtime']

        for att in self:
            ot_record = AttendanceOvertime.search([
                ('employee_id', '=', att.employee_id.id),
                ('date', '=', att.check_in.date() if att.check_in else None),
                ('adjustment', '=', False)
            ], limit=1)
            if ot_record:
                att.overtime_hours = att.worked_hours - ot_record.duration
            else:
                att.overtime_hours = 0.0

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_employee_total_overtime()
        return records

    def write(self, vals):
        res = super().write(vals)
        if any(f in vals for f in ['check_in', 'check_out', 'employee_id']):
            self._update_employee_total_overtime()
        return res

    def _update_employee_total_overtime(self):
        """Trigger recalculation of total overtime for affected employees."""
        employees = self.mapped('employee_id')
        employees._compute_total_overtime()
