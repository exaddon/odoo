# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CRMLeadBizople(models.Model):
    _inherit = "crm.lead"

    join_exaddon_lead = fields.Boolean('Join Exaddon Newsletter')
