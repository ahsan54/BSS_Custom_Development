# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Portal Dashboard",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Extra Tools",
    "summary": "lead information dashboard, opportunity detail dashboard, sales detail dashboard, rfq detail dashboard, request for quote dashboard, purchase detail dashboard module, invoice detail dashboard app Odoo",
    "description": """A dashboard is a view of geographic information that helps you monitor sale, purchase, invoice, project, lead, bills activities. Dashboards are designed to display multiple visualizations that work together on a single screen. Do you want to show a dashboard to your portal users? Do you want to show a well-formatted dashboard to your customer/vendor on my account screen? Do you want to show information on the lead, opportunity, quotation, sales, RFQ, purchase, invoices, bills, task, etc in graphical view? So here it is. we have made a materialize dashboard design for my account page. currently in odoo 'my account' have not well-formatted dashboard and is not well designed. we have modified and made that very beautiful and attractive.""",
    "version": "16.0.1",
    "depends": [
        "portal", 'hr_payroll','ent_ohrms_loan', 'hr_employee_customization','hr_holidays', 'sale', 'website', 'approvals', 'helpdesk', 'hr_expense','hr_attendance', 'hr_job_custom'
    ],
    "application": True,
    "data": [
        "views/portal_templates.xml",
        "views/res_config_settings_views.xml",
        'views/Bss_portal_view.xml',
        'views/portal_my_attendance.xml',
        'views/portal_my_req_salary_slip.xml',
        'views/portal_my_req_loan.xml',
        'views/portal_my_req_for_expense.xml',
        'views/portal_my_req_leave.xml',
        'views/portal_helpdesk.xml',
        'views/request_tax_certificate.xml',
        ## Huzaifa
        'views/portal_my_attendance_detail.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sh_portal_dashboard/static/src/css/portal.css',
            'sh_portal_dashboard/static/src/css/chartist.css',
            'sh_portal_dashboard/static/src/css/chartist-plugin-tooltip.css',
            'sh_portal_dashboard/static/src/css/mobiscroll.javascript.min.css',
            'sh_portal_dashboard/static/src/lib/jquery.cookie.js',
            'sh_portal_dashboard/static/src/lib/chartist.js',
            'sh_portal_dashboard/static/src/lib/chartist-plugin-tooltip.js',
            'sh_portal_dashboard/static/src/lib/chartist-plugin-axistitle.js',
            'sh_portal_dashboard/static/src/js/portal.js',
            'sh_portal_dashboard/static/src/js/mobiscroll.javascript.min.js',
        ],
    },
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/eXQeOF9BjMk",
    "license": "OPL-1",
    "auto_install": False,
    "installable": True,
    "price": 70,
    "currency": "EUR"
}
