# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    'name': 'Bizople Purchase Exaddon',
    'category': 'Inventory/Purchase',
    'version': '14.0.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Bizople Purchase Exaddon',
    'description': """Bizople Purchase Exaddon""",
    'depends': [
        'purchase',
        'purchase_stock',
        'product',
    ],

    'data': [
        'views/product_variant_view_inherit.xml',
        'views/stock_quant_view_inherit.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
