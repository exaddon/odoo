# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class ProductVariantrBiz(models.Model):
    _inherit = "product.product"

    is_consumable_item = fields.Boolean(string="Consumable Item")