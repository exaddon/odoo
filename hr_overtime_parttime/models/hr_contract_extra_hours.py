# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
from pytz import UTC

class HrContractExtraHours(models.Model):
    _inherit = 'hr.contract'

    extra_hours = fields.Float(
        string='Extra Hours',
        compute='_compute_extra_hours',
        help='Extra hours worked (worked hours minus expected hours)',
    )

    @api.depends('employee_id', 'resource_calendar_id')
    def _compute_extra_hours(self):
        for contract in self:
            if not contract.employee_id or not contract.resource_calendar_id:
                contract.extra_hours = 0.0
                continue

            # compute the period: from contract start until today (or contract end if set)
            date_start = contract.date_start
            date_end = contract.date_end or fields.Date.today()

            # convert to UTC datetime at start and end of day
            start_dt = datetime.combine(date_start, datetime.min.time()).replace(tzinfo=UTC)
            end_dt = datetime.combine(date_end, datetime.max.time()).replace(tzinfo=UTC)

            # get the worked hours from attendance
            worked_hours = sum(contract.employee_id.attendance_ids.filtered(
                lambda att: att.check_in.date() >= date_start and att.check_out.date() <= date_end and att.check_out
            ).mapped(lambda a: (a.check_out - a.check_in).total_seconds() / 3600))

            # get expected hours from calendar
            expected_hours = contract.resource_calendar_id.get_work_hours_count(start_dt, end_dt)

            # extra hours = worked - expected
            contract.extra_hours = round(worked_hours - expected_hours, 2)
