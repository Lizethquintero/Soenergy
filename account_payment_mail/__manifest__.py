# -*- coding: utf-8 -*-
{
    'name': "Account Payment Mail",

    'summary': "Account Payment Mail",

    'description': "Account Payment Mail",

    'author': "Todoo SAS",
    'contributors': ['Carlos Guio fg@todoo.co'],
    'website': "http://www.todoo.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tools',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['account','portal'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_report.xml',
        'views/account_payment_view.xml',
        'data/mail_data.xml',
        'views/templates.xml',
    ],
}
