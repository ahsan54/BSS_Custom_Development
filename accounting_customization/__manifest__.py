{
    'name': 'Accounting Customization',  # Module name
    'author': 'Ahsan',  # author name
    'description': "",  # desc about app
    'version': '1.0',  # specify version of app after odoo
    'summary': '',  # give little info about app
    'sequence': 1,  # set the position in all apps
    'category': '',  # will displayed in info
    'website': 'https://www.google.com',  # will displayed in info
    'depends': ['base', 'account', 'mail'],  # those modules , on which our app depends , inheriot them here
    'installable': True,
    'application': True,
    'data': [
        'security/groups.xml',
        'views/accounting_custom_view.xml'

    ]
}
