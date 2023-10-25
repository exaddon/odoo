# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.
{
    # Theme information
    'name': 'Bizople CRM Exaddon',
    'category': 'Website',
    'version': '14.0.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Bizople CRM Exaddon',
    'description': """Bizople CRM Exaddon""",
    'depends': [
        'website',
        'website_crm',
    ],

    'data': [
        'views/snippets/s_exaddons_form.xml',
        'views/snippets/s_exaddons_form_download.xml',
        'views/exaddons_inherit.xml',
        'views/crm_lead_view_inherit.xml',
    ],

    'images': [
        
    ],


    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OPL-1',
}
