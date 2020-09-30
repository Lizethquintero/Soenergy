# -*- coding: utf-8 -*-
{
    'name': "Account extended",

    'summary': "Account extended",

    'description': "Account extended",

    'author': "Todoo SAS",
    'contributors': ['Pablo Arcos pa@todoo.co'],
    'website': "http://www.todoo.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.1',

    # any module necessary for this one to work correctly
    'depends': ['account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_fiscal_position_view.xml',
        # 'views/account_move_view.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
