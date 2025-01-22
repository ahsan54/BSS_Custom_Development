{
    'name': 'Accounting Settings Inherited',  # Module name
    'author': 'Ahsin Ismail',  # Author name
    'maintainer': 'M.Rizwan',  # Author name
    'description': "This is BSS Accounting Config Module",  # Description about the app
    'version': '17.0.1.0',  # Correct version format for Odoo 17
    'sequence': 2,  # Position in the apps menu
    'category': 'BSS',  # Category displayed in info
    'website': 'https://www.bssuniversal.com',  # Website displayed in info
    'depends': ['base', 'account', 'account_accountant'],  # Dependencies
    'installable': True,
    'application': True,
    'data': [
        'views/accounting_settings_inherited.xml'
    ],

}
