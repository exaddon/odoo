# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class StockquantBiz(models.Model):
    _inherit = "stock.quant"

    is_consumable_item = fields.Boolean(related="product_id.is_consumable_item", string="Consumable Item")