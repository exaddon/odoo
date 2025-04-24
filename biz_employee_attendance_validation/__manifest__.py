# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.


{
    'name': "Employee's Attendance Validation" ,
    'category': 'Human Resources/Attendances',
    'version': '17.0.0.0',
    'sequence':1,
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': "Employee's Attendance Validation",
    'description': """Employee's Attendance Validation""",
    'depends': ['hr_contract','hr_attendance','mail','hr_holidays'],

    'data': [
        "security/ir.model.access.csv",
        'views/hr_employee_views.xml',
        'views/swiss_law_views.xml',
        'data/ir_cron.xml',
        'views/res_company.xml',
        'data/irregular_attendance_mail.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
}
