# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrderBiz(models.Model):
    _inherit = "purchase.order"

    def write(self, vals):
        res = super().write(vals)
        # When a PO line description is edited, copy it to its open stock moves (same rule as 17.0)
        for command in vals.get('order_line') or []:
            if (len(command) >= 3 and command[0] == 1
                    and isinstance(command[2], dict) and command[2].get('name')):
                moves = self.env['stock.move'].search([
                    ('purchase_line_id', '=', command[1]),
                    ('state', 'not in', ('done', 'cancel')),
                ])
                if moves:
                    moves.write({'description_picking': command[2]['name']})
        return res


class PurchaseOrderLineBiz(models.Model):
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        moves = super()._create_stock_moves(picking)
        # Receipts show the PO line description instead of the product description
        for move in moves:
            if move.purchase_line_id and move.purchase_line_id in self:
                move.write({'description_picking': move.purchase_line_id.name})
        return moves
