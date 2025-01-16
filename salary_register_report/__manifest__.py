# -*- coding: utf-8 -*-
{
    'name': "Salary Regester Report",

    'summary': """
        Salary Register Report """,

    'description': """
       About Reports
    """,

    'author': "M.Rizwan",
    'website': "http://google.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Reporting',
    'version': '0.1',
    'sequence': -100,
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,

    'depends': ['base', 'hr_payroll', 'report_xlsx'],

    # always loaded
    'data': [
        'report/report.xml',
        'models/salary_register_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
