# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api,_
from datetime import timedelta,datetime, time
from collections import defaultdict
import logging
_logger = logging.getLogger(__name__)
 

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    attendance_non_compliant = fields.Boolean(string="Disable Break Time Check")         

    @api.model
    def action_daily_attendance_check(self):
        now = fields.Datetime.now()
        today_start = fields.Datetime.to_datetime(fields.Date.today())                                 
        today_end = today_start.replace(hour=23, minute=59, second=59)
        company = self.env.company        
        working_hours_break_pairs = {
            rec.working_hours: rec.break_time for rec in company.swiss_law_ids
        }    
 
        employees = self.env['hr.employee'].search([('attendance_non_compliant', '=', False)])

        for emp in employees:
            _logger.info("Checking Employee: %s", emp.name)
            company = emp.company_id
            total_gap_hours = timedelta(hours=company.total_gap_hours if company.total_gap_hours else 11)

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', emp.id),
                ('check_in', '>=', today_start),
                ('check_in', '<=', today_end),
            ], order="check_in asc")

            # Rest between two days
            yesterday_start = today_start - timedelta(days=1)
            yesterday_end = yesterday_start.replace(hour=23, minute=59, second=59)

            last_yesterday_attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', emp.id),
                ('check_out', '>=', yesterday_start),
                ('check_out', '<=', yesterday_end),
            ], order="check_out desc", limit=1)


            if attendances and last_yesterday_attendance:
                first_today_checkin = attendances[0].check_in
                last_yesterday_checkout = last_yesterday_attendance.check_out

                if last_yesterday_checkout and first_today_checkin:
                    rest_time = first_today_checkin - last_yesterday_checkout

                    if rest_time < total_gap_hours:
                        self._send_message(emp, 
                            "Dear Employee, you have irregularities in your attendance records, please correct those to comply to swiss law."
                        )
    
            # Continuous Work Without Check-Out
            if attendances and attendances[-1].check_out is False:
                continuous_work = (now - attendances[-1].check_in).total_seconds() / 3600  # Convert to float in hours
                for i in working_hours_break_pairs:
                    if continuous_work > i:
                        self._send_message(emp, 
                            "Dear Employee, you have irregularities in your attendance records, please correct those to comply to swiss law."
                        )
                
            # check multiple checkin checkout and breaks with swiss law
            if attendances:
                total_working_time = timedelta(0)
                first_checkin = attendances[0].check_in
                last_checkout = attendances[-1].check_out if attendances[-1].check_out else now

                if first_checkin and last_checkout:
                    duration = last_checkout - first_checkin
                    total_duration = duration.total_seconds() / 3600
                
                for att in attendances:
                    check_in = att.check_in
                    check_out = att.check_out if att.check_out else now
                    working_time = check_out - check_in
                    total_working_time += working_time

                total_working_hours = total_working_time.total_seconds() / 3600
                work_gap = total_duration - total_working_hours

                is_invalid = []
                
                for k, v in working_hours_break_pairs.items():
                    if total_working_hours >= k and work_gap < v:
                        is_invalid.append(True)
                if any(is_invalid):
                    self._send_message(emp, "Dear Employee, you have irregularities in your attendance records, please correct those to comply to swiss law.")

    
    def _send_message(self, emp, message):
        if emp.user_id and emp.user_id.partner_id:
            odoobot_user = self.env.ref("base.user_root")
            channel_odoo_swiss_info = self.env["discuss.channel"].with_user(odoobot_user.id).channel_get([emp.user_id.partner_id.id])
            channel_odoo_swiss_law = self.env["discuss.channel"].browse(channel_odoo_swiss_info["id"])

            channel_odoo_swiss_law.with_user(odoobot_user.id).message_post(
                body=message,
                partner_ids=[emp.user_id.partner_id.id],
                subtype_xmlid="mail.mt_comment",
                message_type="comment",
            )
            _logger.info("Message sent to %s: %s", emp.name, message)

    @api.model
    def action_weekly_attendance_check(self):
        now = fields.Datetime.now()
        today = fields.Date.today()
        start_of_week = fields.Date.to_date("2025-04-01")
        end_of_week = fields.Date.today()

        company = self.env.company        
        working_hours_break_pairs = {
            rec.working_hours: rec.break_time for rec in company.swiss_law_ids
        }
        
        employees = self.env['hr.employee'].search([('attendance_non_compliant', '=', False)])
        non_compliant_employees = {}

        start_date = datetime(2025, 4, 1)
        end_date = datetime.now()

        weeks = []

        current_week = []

        current_date = start_date
        while current_date <= end_date:
            current_week.append(current_date)
            
            if len(current_week) == 7 or current_date == end_date:
                weeks.append(current_week)
                current_week = []
            
            current_date += timedelta(days=1)
        
        for emp in employees:
            _logger.info("Checking Employee: %s", emp.name)
            company = emp.company_id
            total_gap_hours = timedelta(hours=company.total_gap_hours if company.total_gap_hours else 11)
            
            for i, week in enumerate(weeks, 1):
                print(f"Week {i}:", week)
                for date in week:
                    day_start = date.replace(hour=0, minute=0, second=0)
                    day_end = date.replace(hour=23, minute=59, second=59)
                    
                    attendances = self.env['hr.attendance'].search([
                        ('employee_id', '=', emp.id),
                        ('check_in', '>=', day_start),
                        ('check_in', '<=', day_end),
                    ], order="check_in asc")
                    
                    yesterday_start = day_start - timedelta(days=1)
                    yesterday_end = fields.Datetime.to_datetime(yesterday_start) + timedelta(hours=23, minutes=59, seconds=59)
                    last_yesterday_attendance = self.env['hr.attendance'].search([
                        ('employee_id', '=', emp.id),
                        ('check_out', '>=', yesterday_start),
                        ('check_out', '<=', yesterday_end),
                    ], order="check_out desc", limit=1)
                    
                    # Check rest time between two working days
                    if attendances and last_yesterday_attendance:
                        first_today_checkin = attendances[0].check_in
                        last_yesterday_checkout = last_yesterday_attendance.check_out
                        if last_yesterday_checkout and first_today_checkin:
                            rest_time = first_today_checkin - last_yesterday_checkout
                            if rest_time < total_gap_hours:
                                non_compliant_employees.setdefault(emp, []).append(f"Insufficient rest on {day_start}")
                    
                    # Check if break time is sufficient
                    if attendances:
                        total_working_time = timedelta(0)
                        first_checkin = attendances[0].check_in
                        last_checkout = attendances[-1].check_out if attendances[-1].check_out else now
                        total_duration = (last_checkout - first_checkin).total_seconds() / 3600
                        
                        for att in attendances:
                            check_in = att.check_in
                            check_out = att.check_out if att.check_out else now
                            total_working_time += check_out - check_in
                        
                        total_working_hours = total_working_time.total_seconds() / 3600
                        work_gap = total_duration - total_working_hours
                        
                        for work_hours, break_time in working_hours_break_pairs.items():
                            if total_working_hours >= work_hours and work_gap < break_time:
                                non_compliant_employees.setdefault(emp, []).append(f"Insufficient break time on {day_start}")
        
        for emp, violations in non_compliant_employees.items():
            self.send_emp_email(emp, violations)

        manager_wise_violations = {}

        for emp, violations in non_compliant_employees.items():
            manager = emp.parent_id  
            if manager:
                manager_wise_violations.setdefault(manager, []).append((emp, violations))

        for manager, emp_violations in manager_wise_violations.items():
            self.send_manager_email(manager, emp_violations)

    def send_emp_email(self, emp, violations):
        email_values = {
            'email_to': emp.work_email,
        }
        swiss_law_records = emp.company_id.swiss_law_ids
        context = {
            'swiss_law_list': [
                (
                    f"{int(law.working_hours):02}:{int((law.working_hours % 1) * 60):02} ",
                    f"{int(law.break_time):02}:{int((law.break_time % 1) * 60):02} "
                )
                for law in swiss_law_records
            ],
            'min_rest_hours': f"{int(emp.company_id.total_gap_hours):02}:{int((emp.company_id.total_gap_hours % 1) * 60):02}"
        }
        template_ref = self.env.ref('biz_employee_attendance_validation.email_template_weekly_attendance')
        template_ref.with_context(**context).send_mail(emp.id, force_send=True, raise_exception=True, email_values=email_values)

    def send_manager_email(self, manager, emp_violations):
        if not manager or not manager.work_email:
            return
        email_values = {
            'email_to': manager.work_email,
        }        
        emp_names = list(set(emp.name for emp, _ in emp_violations))
        template_ref = self.env.ref('biz_employee_attendance_validation.email_template_manager_weekly_attendance')
        context = {
            'employee_names': emp_names,
        }
        template_ref.with_context(**context).send_mail(manager.id, force_send=True, raise_exception=True,email_values=email_values)

        


        