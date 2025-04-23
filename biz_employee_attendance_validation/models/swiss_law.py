# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api
import logging
_logger = logging.getLogger(__name__)
 

class EmployeeSwissLaw(models.Model):
    _name = 'employee.swiss.law'
    _description = 'Employee Swiss Law'

    working_hours = fields.Float(string="Working Hours")
    break_time = fields.Float(string="Break Duration (Minutes)")
    company_id = fields.Many2one('res.company',string="company")

    
                

    
