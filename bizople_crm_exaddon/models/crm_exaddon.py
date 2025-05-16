# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

import random

from odoo import api, fields, models, _
from odoo.exceptions import AccessDenied, AccessError, UserError
from odoo.tools import html_escape


class CRMLeadBizople(models.Model):
    _inherit = "crm.lead"

    join_exaddon_lead = fields.Boolean('Join Exaddon Newsletter')