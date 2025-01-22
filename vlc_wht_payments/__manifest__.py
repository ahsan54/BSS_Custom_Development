# -*- coding: utf-8 -*-
{
    'name': "Withholding Payment",

    'summary': """
        This Module Deals With Withholding Payments For Multi Company""",

    'description': """
        This Module Deals With Withholding Tax Entry On Payments For Multi Company.
    """,

    'author': "Rizwan Chaudhary and Ahsin",
    'website': "http://www.bssuniversal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '16.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','payment'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
        'views/account_payment_views.xml',
        'views/account_register_payment_views.xml',
        'views/account_tax_views.xml',
        'views/res_config_settings_views.xml',
    ],

}
