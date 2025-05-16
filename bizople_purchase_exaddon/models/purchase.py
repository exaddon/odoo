# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, _

class PurchaseOrderBiz(models.Model):
    _inherit = "purchase.order"

    def write(self, values):
        res = super(PurchaseOrderBiz,self).write(values)
        print("res=======================",res)
        if values.get('order_line'):
            lines = values.get('order_line')
            print("lines===================",lines)
            for line in lines:
                print("line===============================",line)
                po_line_id = line[1]
                print("po_line_id=================",po_line_id)
                if line[2] != False and line[2].get('name'):
                    name_changed = line[2].get('name')
                    print("name_changed===================",name_changed)
                    stock_obj = self.env['stock.move'].search([('purchase_line_id', '=', po_line_id),('state', 'not in', ('done', 'cancel'))])
                    print("stock_obj=====================",stock_obj)
                    if stock_obj:
                        stock_obj.write({'description_picking': name_changed})
        return res
    

class PurchaseOrderLineBiz(models.Model):
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        move_line_ids = super(PurchaseOrderLineBiz, self)._create_stock_moves(picking)
        print("move_line_ids=====================",move_line_ids)
        for move_line in move_line_ids:
            print("move_line================",move_line)
            for purchase_line in self:
                print("purchase_line===================",purchase_line)
                if move_line.purchase_line_id.id == purchase_line.id:
                    print("move_line.purchase_line_id.id=============================",move_line.purchase_line_id.id)
                    move_line.write({'description_picking': purchase_line.name})
        return move_line_ids