from odoo import models, fields, api
from datetime import datetime, time
import pytz


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    total_overtime = fields.Float(
        string="Total Overtime",
        compute="_compute_total_overtime",
        store=True,
        compute_sudo=True,
    )

    def _recompute_total_overtime(self):
        self.invalidate_recordset(['total_overtime'])
        self._compute_total_overtime()

    @api.depends(
        'attendance_ids.worked_hours',
        'resource_calendar_id',
        'contract_id.date_start',
    )
    def _compute_total_overtime(self):
        Attendance = self.env['hr.attendance']

        for emp in self:
            if not emp.contract_id or not emp.contract_id.date_start:
                emp.total_overtime = 0.0
                continue

            tz = pytz.timezone(emp.resource_calendar_id.tz or 'UTC')

            start = datetime.combine(emp.contract_id.date_start, time.min)
            start = tz.localize(start).astimezone(pytz.utc).replace(tzinfo=None)
            end = datetime.utcnow()

            attendances = Attendance.search([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', start),
                ('check_out', '<=', end),
            ])
            worked = sum(att.worked_hours for att in attendances)

            intervals = emp.resource_calendar_id._work_intervals_batch(
                start,
                end,
                resources=emp.resource_id,
            )[emp.resource_id.id]

            expected = sum(
                (i[1] - i[0]).total_seconds() / 3600
                for i in intervals
            )

            emp.total_overtime = worked - expected
