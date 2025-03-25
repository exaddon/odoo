# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    swiss_law_ids = fields.One2many('employee.swiss.law',inverse_name='company_id',string="Swiss Law")
    total_gap_hours = fields.Float(string="Gap Between two working days")
