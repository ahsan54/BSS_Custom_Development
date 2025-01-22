# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import http, fields
from odoo.http import request
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil import rrule
import logging
_logger = logging.getLogger(__name__)

# Maps only the 6 first bits of the base64 data, accurate enough
# for our purpose and faster than decoding the full blob first
FILETYPE_BASE64_MAGICWORD = {
    b'/': 'jpg',
    b'R': 'gif',
    b'i': 'png',
    b'P': 'svg+xml',
}


class Charts(http.Controller):

    def image_data_uri(self, base64_source):
        """This returns data URL scheme according RFC 2397
        (https://tools.ietf.org/html/rfc2397) for all kind of supported images
        (PNG, GIF, JPG and SVG), defaulting on PNG type if not mimetype detected.
        """
        return 'data:image/%s;base64,%s' % (
            FILETYPE_BASE64_MAGICWORD.get(base64_source[:1], 'png'),
            base64_source.decode(),
        )



    @http.route(['/sh_portal_dashboard/get_sale_chart'], type='json', auth="user", methods=['POST'])
    def get_sale_chart(self, sh_filter_chart_type=False, **kw):
        """ Generate a chart x-axis labels list and y-axis series list
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'x_axis_labels_list': [],
            'y_axis_series_list': [],
            'is_show_sale_chart': False,
            "heading": "",
        }

        is_installed_sale = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'sale'), ('state', '=', 'installed')]).id
        if is_installed_sale and request.env.company.sh_portal_dashboard_is_show_sale_chart:

            values.update({
                'is_show_sale_chart': True,
            })
            partner = request.env.user.partner_id
            sale_order_obj = request.env['sale.order']

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain
                sale_orders = sale_order_obj.search(domain)
                amount_totaL = 0
                if sale_orders:
                    for order in sale_orders:
                        amount_totaL += order.amount_total
                values.update({
                    'x_axis_labels_list': ['Today'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Today's Sale Analysis",
                })

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

                sale_orders = sale_order_obj.search(domain)
                amount_totaL = 0
                if sale_orders:
                    for order in sale_orders:
                        amount_totaL += order.amount_total
                values.update({
                    'x_axis_labels_list': ['Yesterday'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Yesterday's Sale Analysis",
                })

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                #iterate each day of week and search sale order
                amount_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=week_date_start, until=week_date_end):
                    each_day_of_week_domain = []
                    each_day_of_week_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', dt.date()),
                        ('date_order', '<=', dt.date())
                    ]

                    each_day_of_week_domain += date_domain
                    sale_orders = sale_order_obj.search(
                        each_day_of_week_domain)

                    amount_totaL = 0
                    if sale_orders:
                        for order in sale_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)

                values.update({
                    'x_axis_labels_list': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    'y_axis_series_list': amount_list,
                    "heading": "Sale Analysis of the week",
                })

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month
                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                #iterate each day of month and search sale order
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=month_date_start, until=month_date_end):
                    each_day_of_month_domain = []
                    each_day_of_month_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', dt.date()),
                        ('date_order', '<=', dt.date())
                    ]

                    each_day_of_month_domain += date_domain
                    sale_orders = sale_order_obj.search(
                        each_day_of_month_domain)

                    amount_totaL = 0
                    if sale_orders:
                        for order in sale_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().day)

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Sale Analysis of the month",
                })

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                #iterate each day of year and search sale order
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.MONTHLY, dtstart=year_date_start, until=year_date_end):
                    first_date_of_month = dt.date()
                    last_date_of_month = dt.date() + relativedelta(day=1, months=+1, days=-1)

                    each_month_of_year_domain = []
                    each_month_of_year_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', first_date_of_month),
                        ('date_order', '<=', last_date_of_month)
                    ]

                    each_month_of_year_domain += date_domain
                    sale_orders = sale_order_obj.search(
                        each_month_of_year_domain)

                    amount_totaL = 0
                    if sale_orders:
                        for order in sale_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().strftime("%b"))

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Sale Analysis of the year",
                })

        return values

    @http.route(['/sh_portal_dashboard/get_invoice_chart'], type='json', auth="user", methods=['POST'])
    def get_invoice_chart(self, sh_filter_chart_type=False, **kw):
        """ Generate a chart x-axis labels list and y-axis series list
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'x_axis_labels_list': [],
            'y_axis_series_list': [],
            'is_show_invoice_chart': False,
            "heading": "",
        }

        is_installed_account = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'account'), ('state', '=', 'installed')]).id
        if is_installed_account and request.env.company.sh_portal_dashboard_is_show_invoice_chart:
            values.update({
                'is_show_invoice_chart': True
            })

            account_invoice_obj = request.env['account.move']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
#                 ('state', 'not in', ['draft', 'cancel']),
                ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt'))
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(date.today())),
                    ('invoice_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain
                invoices = account_invoice_obj.search(domain)
                amount_totaL = 0
                if invoices:
                    for invoice in invoices:
                        amount_totaL += invoice.amount_total
                values.update({
                    'x_axis_labels_list': ['Today'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Today's Invoice Analysis",
                })

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('invoice_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

                invoices = account_invoice_obj.search(domain)
                amount_totaL = 0
                if invoices:
                    for invoice in invoices:
                        amount_totaL += invoice.amount_total
                values.update({
                    'x_axis_labels_list': ['Yesterday'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Yesterday's Invoice Analysis",
                })

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                #iterate each day of week and search invoice
                amount_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=week_date_start, until=week_date_end):
                    each_day_of_week_domain = []
                    each_day_of_week_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', dt.date()),
                        ('invoice_date', '<=', dt.date())
                    ]

                    each_day_of_week_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_day_of_week_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)

                values.update({
                    'x_axis_labels_list': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    'y_axis_series_list': amount_list,
                    "heading": "Invoice Analysis of the week",
                })

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                #iterate each day of month and search invoice
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=month_date_start, until=month_date_end):
                    each_day_of_month_domain = []
                    each_day_of_month_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', dt.date()),
                        ('invoice_date', '<=', dt.date())
                    ]

                    each_day_of_month_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_day_of_month_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().day)

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Invoice Analysis of the month",
                })

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                #iterate each day of year and search invoice
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.MONTHLY, dtstart=year_date_start, until=year_date_end):
                    first_date_of_month = dt.date()
                    last_date_of_month = dt.date() + relativedelta(day=1, months=+1, days=-1)

                    each_month_of_year_domain = []
                    each_month_of_year_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', first_date_of_month),
                        ('invoice_date', '<=', last_date_of_month)
                    ]

                    each_month_of_year_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_month_of_year_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().strftime("%b"))

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Invoice Analysis of the year",
                })

        return values

    @http.route(['/sh_portal_dashboard/get_purchase_chart'], type='json', auth="user", methods=['POST'])
    def get_purchase_chart(self, sh_filter_chart_type=False, **kw):
        """ Generate a chart x-axis labels list and y-axis series list
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'x_axis_labels_list': [],
            'y_axis_series_list': [],
            'is_show_purchase_chart': False,
        }

        is_installed_purchase = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'purchase'), ('state', '=', 'installed')]).id
        if is_installed_purchase and request.env.company.sh_portal_dashboard_is_show_purchase_chart:
            values.update({
                'is_show_purchase_chart': True
            })

            purchase_order_obj = request.env['purchase.order']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['purchase', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain
                purchase_orders = purchase_order_obj.search(domain)
                amount_totaL = 0
                if purchase_orders:
                    for order in purchase_orders:
                        amount_totaL += order.amount_total
                values.update({
                    'x_axis_labels_list': ['Today'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Today's Purchase Analysis",
                })

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

                purchase_orders = purchase_order_obj.search(domain)
                amount_totaL = 0
                if purchase_orders:
                    for order in purchase_orders:
                        amount_totaL += order.amount_total
                values.update({
                    'x_axis_labels_list': ['Yesterday'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Yesterday's Purchase Analysis",
                })

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                #iterate each day of week and search purchase order
                amount_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=week_date_start, until=week_date_end):
                    each_day_of_week_domain = []
                    each_day_of_week_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', dt.date()),
                        ('date_order', '<=', dt.date())
                    ]

                    each_day_of_week_domain += date_domain
                    purchase_orders = purchase_order_obj.search(
                        each_day_of_week_domain)

                    amount_totaL = 0
                    if purchase_orders:
                        for order in purchase_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)

                values.update({
                    'x_axis_labels_list': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    'y_axis_series_list': amount_list,
                    "heading": "Purchase Analysis of the week",
                })

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                #iterate each day of month and search purchase order
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=month_date_start, until=month_date_end):
                    each_day_of_month_domain = []
                    each_day_of_month_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', dt.date()),
                        ('date_order', '<=', dt.date())
                    ]

                    each_day_of_month_domain += date_domain
                    purchase_orders = purchase_order_obj.search(
                        each_day_of_month_domain)

                    amount_totaL = 0
                    if purchase_orders:
                        for order in purchase_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().day)

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Purchase Analysis of the month",
                })

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                #iterate each day of year and search purchase
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.MONTHLY, dtstart=year_date_start, until=year_date_end):
                    first_date_of_month = dt.date()
                    last_date_of_month = dt.date() + relativedelta(day=1, months=+1, days=-1)

                    each_month_of_year_domain = []
                    each_month_of_year_domain = domain.copy()
                    date_domain = [
                        ('date_order', '>=', first_date_of_month),
                        ('date_order', '<=', last_date_of_month)
                    ]

                    each_month_of_year_domain += date_domain
                    purchase_orders = purchase_order_obj.search(
                        each_month_of_year_domain)

                    amount_totaL = 0
                    if purchase_orders:
                        for order in purchase_orders:
                            amount_totaL += order.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().strftime("%b"))

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Purchase Analysis of the year",
                })

        return values

    @http.route(['/sh_portal_dashboard/set_bill_charts'], type='json', auth="user", methods=['POST'])
    def set_bill_charts(self, sh_filter_chart_type=False, **kw):
        """ Generate a chart x-axis labels list and y-axis series list
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'x_axis_labels_list': [],
            'y_axis_series_list': [],
            'is_show_bill_chart': False,
            "heading": " ",
        }

        is_installed_account = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'account'), ('state', '=', 'installed')]).id
        if is_installed_account and request.env.company.sh_portal_dashboard_is_show_bill_chart:
            values.update({
                'is_show_bill_chart': True
            })

            account_invoice_obj = request.env['account.move']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
#                 ('state', 'not in', ['draft', 'cancel']),
                ('move_type', 'in', ('in_invoice', 'in_refund', 'in_receipt'))
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(date.today())),
                    ('invoice_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain
                invoices = account_invoice_obj.search(domain)
                amount_totaL = 0
                if invoices:
                    for invoice in invoices:
                        amount_totaL += invoice.amount_total
                values.update({
                    'x_axis_labels_list': ['Today'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Today's Bill Analysis",
                })

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('invoice_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

                invoices = account_invoice_obj.search(domain)
                amount_totaL = 0
                if invoices:
                    for invoice in invoices:
                        amount_totaL += invoice.amount_total
                values.update({
                    'x_axis_labels_list': ['Yesterday'],
                    'y_axis_series_list': [amount_totaL],
                    "heading": "Yesterday's Bill Analysis",
                })

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                #iterate each day of week and search invoice
                amount_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=week_date_start, until=week_date_end):
                    each_day_of_week_domain = []
                    each_day_of_week_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', dt.date()),
                        ('invoice_date', '<=', dt.date())
                    ]

                    each_day_of_week_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_day_of_week_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)

                values.update({
                    'x_axis_labels_list': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                    'y_axis_series_list': amount_list,
                    "heading": "Bill Analysis of the week",
                })

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                #iterate each day of month and search invoice
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.DAILY, dtstart=month_date_start, until=month_date_end):
                    each_day_of_month_domain = []
                    each_day_of_month_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', dt.date()),
                        ('invoice_date', '<=', dt.date())
                    ]

                    each_day_of_month_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_day_of_month_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().day)

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Bill Analysis of the month",
                })

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                #iterate each day of year and search invoice
                amount_list = []
                label_list = []
                for dt in rrule.rrule(rrule.MONTHLY, dtstart=year_date_start, until=year_date_end):
                    first_date_of_month = dt.date()
                    last_date_of_month = dt.date() + relativedelta(day=1, months=+1, days=-1)

                    each_month_of_year_domain = []
                    each_month_of_year_domain = domain.copy()
                    date_domain = [
                        ('invoice_date', '>=', first_date_of_month),
                        ('invoice_date', '<=', last_date_of_month)
                    ]

                    each_month_of_year_domain += date_domain
                    invoices = account_invoice_obj.search(
                        each_month_of_year_domain)

                    amount_totaL = 0
                    if invoices:
                        for invoice in invoices:
                            amount_totaL += invoice.amount_total
                    amount_list.append(amount_totaL)
                    label_list.append(dt.date().strftime("%b"))

                values.update({
                    'x_axis_labels_list': label_list,
                    'y_axis_series_list': amount_list,
                    "heading": "Bill Analysis of the year",
                })

        return values

    @http.route(['/sh_portal_dashboard/get_product_wise_sale_data'], type='json', auth="user", methods=['POST'])
    def get_product_wise_sale_data(self, sh_filter_chart_type=False, **kw):
        """ Generate product wise sale data.
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'products': [],
            'is_show_product_wise_sale_data': False,
            'x_axis_labels_list': [],
            "y_axis_series_list_amount": [],
            "y_axis_series_list_qty": [],
            "heading": "",
        }

        heading = ""
        is_installed_sale = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'sale'), ('state', '=', 'installed')]).id
        if is_installed_sale and request.env.company.sh_portal_dashboard_is_show_sale_chart:

            values.update({
                'is_show_product_wise_sale_data': True
            })
            partner = request.env.user.partner_id
            sale_order_line_obj = request.env['sale.order.line']

            domain = [
                ('order_id.message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('order_id.state', 'in', ['sale', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                heading = "Today's Top 10 Products Sold"
                today_domain = [
                    ('order_id.date_order', '>=',
                     fields.Date.to_string(date.today())),
                    ('order_id.date_order', '<=',
                     fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                heading = "Yesterday's Top 10 Products Sold"
                yesterday_domain = [
                    ('order_id.date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('order_id.date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                heading = "Top 10 products sold of the week"
                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('order_id.date_order', '>=', week_date_start),
                    ('order_id.date_order', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                heading = "Top 10 products sold of the month"
                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('order_id.date_order', '>=', month_date_start),
                    ('order_id.date_order', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                heading = "Top 10 products sold of the year"
                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('order_id.date_order', '>=', year_date_start),
                    ('order_id.date_order', '<=', year_date_end)
                ]

                domain += current_year_domain

            products_dic = {}
            products_list = []

            order_lines = sale_order_line_obj.search(
                domain, order="price_subtotal desc", limit=10)
            if order_lines:
                for line in order_lines:
                    if line.product_id.sudo():
                        if products_dic.get(line.product_id.sudo().id, False):
                            single_product_dic = products_dic.get(
                                line.product_id.sudo().id)
                            amount = line.price_subtotal + \
                                single_product_dic.get('amount')
                            qty = line.product_uom_qty + \
                                single_product_dic.get('qty')
                            products_dic.update({
                                line.product_id.sudo().id: {'product': line.product_id.sudo(
                                ).name, 'qty': qty, 'amount': amount, 'img': line.product_id.sudo().image_128}
                            })
                        else:
                            products_dic.update({
                                line.product_id.sudo().id: {'product': line.product_id.sudo(
                                ).name, 'qty': line.product_uom_qty, 'amount': line.price_subtotal, 'img': line.product_id.sudo().image_128}
                            })

            chart_product_list = []
            chart_amount_list = []
            chart_qty_list = []
            if products_dic:
                sorted_product_tuple_list = sorted(
                    products_dic.items(), key=lambda kv: kv[1].get('amount'), reverse=True)
                for tuple_item in sorted_product_tuple_list:

                    pro_dic = tuple_item[1]

                    icon_image = ""
                    if pro_dic.get("img", False):
                        icon_image = self.image_data_uri(pro_dic.get("img"))
                    else:
                        icon_image = "/web/image/product.product/%s/image/40x40" % (
                            tuple_item[0])

                    product_img = """
                           <img src="%s" alt="%s" style="padding: 0px; margin: 0px; height: auto; width: 40px;"/>                
                    """ % (icon_image, products_dic.get("product", ""))

                    pro_dic.update({"product_img": product_img})

                    products_list.append(pro_dic)
                    #for bar chart data
                    chart_product_list.append(tuple_item[1].get("product", ""))
                    chart_amount_list.append(tuple_item[1].get("amount", 0))
                    chart_qty_list.append(tuple_item[1].get("qty", 0))

            values.update({
                'products': products_list,
                "x_axis_labels_list": chart_product_list,
                "y_axis_series_list_amount": chart_amount_list,
                "y_axis_series_list_qty": chart_qty_list,
                "heading": heading,
            })

        return values

    @http.route(['/sh_portal_dashboard/get_product_wise_purchase_data'], type='json', auth="user", methods=['POST'])
    def get_product_wise_purchase_data(self, sh_filter_chart_type=False, **kw):
        """ Generate product wise purchase data.
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'products': [],
            'is_show_product_wise_purchase_data': False,
            'x_axis_labels_list': [],
            "y_axis_series_list_amount": [],
            "y_axis_series_list_qty": [],
            "heading": " ",
        }

        heading = ""
        is_installed_purchase = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'purchase'), ('state', '=', 'installed')]).id
        if is_installed_purchase and request.env.company.sh_portal_dashboard_is_show_purchase_chart:

            values.update({
                'is_show_product_wise_purchase_data': True
            })

            purchase_order_line_obj = request.env['purchase.order.line']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['purchase', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                heading = "Today's Top 10 Products Purchased"
                today_domain = [
                    ('order_id.date_order', '>=',
                     fields.Date.to_string(date.today())),
                    ('order_id.date_order', '<=',
                     fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                heading = "Yesterday's Top 10 Products Purchased"
                yesterday_domain = [
                    ('order_id.date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('order_id.date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                heading = "Top 10 products purchased of the week"
                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('order_id.date_order', '>=', week_date_start),
                    ('order_id.date_order', '<=', week_date_end)
                ]
                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month
                heading = "Top 10 products purchased of the month"
                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('order_id.date_order', '>=', month_date_start),
                    ('order_id.date_order', '<=', month_date_end)
                ]
                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                heading = "Top 10 products purchased of the year"
                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('order_id.date_order', '>=', year_date_start),
                    ('order_id.date_order', '<=', year_date_end)
                ]
                domain += current_year_domain

            #iterate each day of year and search sale order
            products_dic = {}
            products_list = []

            order_lines = purchase_order_line_obj.search(
                domain, limit=10, order="price_subtotal desc")
            if order_lines:
                for line in order_lines:
                    if line.product_id.sudo():
                        if products_dic.get(line.product_id.sudo().id, False):

                            single_product_dic = products_dic.get(
                                line.product_id.sudo().id)
                            amount = line.price_subtotal + \
                                single_product_dic.get('amount')
                            qty = line.qty_received + \
                                single_product_dic.get('qty')
                            products_dic.update({
                                line.product_id.sudo().id: {'product': line.product_id.sudo(
                                ).name, 'qty': qty, 'amount': amount, 'img': line.product_id.sudo().image_128}
                            })
                        else:
                            products_dic.update({
                                line.product_id.sudo().id: {'product': line.product_id.sudo(
                                ).name, 'qty': line.qty_received, 'amount': line.price_subtotal, 'img': line.product_id.sudo().image_128}
                            })

            chart_product_list = []
            chart_amount_list = []
            chart_qty_list = []
            if products_dic:
                sorted_product_tuple_list = sorted(
                    products_dic.items(), key=lambda kv: kv[1].get('amount'), reverse=True)
                for tuple_item in sorted_product_tuple_list:

                    pro_dic = tuple_item[1]

                    icon_image = ""
                    if pro_dic.get("img", False):
                        icon_image = self.image_data_uri(pro_dic.get("img"))
                    else:
                        icon_image = "/web/image/product.product/%s/image/40x40" % (
                            tuple_item[0])

                    product_img = """
                           <img src="%s" alt="%s" style="padding: 0px; margin: 0px; height: auto; width: 40px;"/>                
                    """ % (icon_image, products_dic.get("product", ""))

                    pro_dic.update({"product_img": product_img})

                    products_list.append(pro_dic)
                    #for bar chart data
                    chart_product_list.append(tuple_item[1].get("product", ""))
                    chart_amount_list.append(tuple_item[1].get("amount", 0))
                    chart_qty_list.append(tuple_item[1].get("qty", 0))

            values.update({
                'products': products_list,
                "x_axis_labels_list": chart_product_list,
                "y_axis_series_list_amount": chart_amount_list,
                "y_axis_series_list_qty": chart_qty_list,
                "heading": heading,
            })

        return values

    @http.route(['/sh_portal_dashboard/get_project_task_data'], type='json', auth="user", methods=['POST'])
    def get_project_task_data(self, sh_filter_chart_type=False, **kw):
        """ Generate project task data.
            :param url : sh_filter_chart_type whether portal user want to show chart by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'tasks': [],
            'is_show_project_chart_data': False,
        }

        is_installed_project = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'project'), ('state', '=', 'installed')]).id
        if is_installed_project and request.env.company.sh_portal_dashboard_is_show_project_task_chart:

            values.update({
                'is_show_project_chart_data': True
            })


            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('create_date', '>=', fields.Date.to_string(date.today())),
                    ('create_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain = domain + today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('create_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('create_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain = domain + yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('create_date', '>=', week_date_start),
                    ('create_date', '<=', week_date_end)
                ]

                domain = domain + current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('create_date', '>=', month_date_start),
                    ('create_date', '<=', month_date_end)
                ]

                domain = domain + current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('create_date', '>=', year_date_start),
                    ('create_date', '<=', year_date_end)
                ]

                domain = domain + current_year_domain

            project_task_obj = request.env['project.task']
            task_list = []

            tasks = project_task_obj.search(domain)
            if tasks:
                for task in tasks:
                    task_url = """
                        <a href="/my/task/%s"><span> %s </span></a>
                        
                        """ % (task.id, task.name)

                    project_url = """
                        <a href="/my/project/%s"><span> %s </span></a>
                        
                        """ % (task.project_id.id if task.project_id else "#", task.project_id.name if task.project_id else "")
                    # raise UserError(project_url)

                    vals = {
                        "project": project_url,
                        "task": task_url,
                        "task_id": task.id,
                        "deadline": task.date_deadline or '',
                    }
                    task_list.append(vals)
            # _logger.exception(task_list)        
            values.update({
                "tasks": task_list
            })

        return values

    @http.route(['/sh_portal_dashboard/get_last_quote'], type='json', auth="user", methods=['POST'])
    def get_last_quote(self, sh_filter_chart_type=False, **kw):
        """ Generate last quotation table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'quotes': [],
            'is_show_last_quote_table': False,
            'last_quote_title': 'Latest ' + str(request.env.company.sh_portal_dashboard_is_show_last_record_limit) + ' Quotations',
        }

        quote_list = []

        is_installed_sale = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'sale'), ('state', '=', 'installed')]).id
        if is_installed_sale and request.env.company.sh_portal_dashboard_is_show_last_quote_table:

            values.update({
                'is_show_last_quote_table': True
            })

            partner = request.env.user.partner_id
            sale_order_obj = request.env['sale.order']

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sent', 'cancel'])
            ]


            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('date_order', '>=', week_date_start),
                    ('date_order', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('date_order', '>=', month_date_start),
                    ('date_order', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('date_order', '>=', year_date_start),
                    ('date_order', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            sale_orders = sale_order_obj.sudo().search(domain, order="date_order desc",
                                                       limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if sale_orders:
                for order in sale_orders:

                    quot_url = """
                        <a href="%s"><span> %s </span></a>
                        
                        """ % (order.get_portal_url(), order.name)

                    order_dic = {
                        "name": quot_url,
                        "date_order": order.date_order,
                    }
                    quote_list.append(order_dic)

        values.update({
            "quotes": quote_list
        })
        return values

    @http.route(['/sh_portal_dashboard/get_last_sale_order'], type='json', auth="user", methods=['POST'])
    def get_last_sale_order(self, sh_filter_chart_type=False, **kw):
        """ Generate last sale order table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'orders': [],
            'is_show_last_sale_order_table': False,
        }

        order_list = []

        is_installed_sale = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'sale'), ('state', '=', 'installed')]).id
        if is_installed_sale and request.env.company.sh_portal_dashboard_is_show_last_sale_order_table:

            values.update({
                'is_show_last_sale_order_table': True
            })

            partner = request.env.user.partner_id
            sale_order_obj = request.env['sale.order']

            domain = [
                ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sale', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('date_order', '>=', week_date_start),
                    ('date_order', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('date_order', '>=', month_date_start),
                    ('date_order', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('date_order', '>=', year_date_start),
                    ('date_order', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            sale_orders = sale_order_obj.sudo().search(domain, order="date_order desc",
                                                       limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if sale_orders:
                for order in sale_orders:

                    status = """
                                <span class="badge badge-pill bg-info"><i class="fa fa-fw fa-clock-o" aria-label="Ready" title="Ready" role="img"></i><span class="d-none d-md-inline">Ready</span></span>                       
                    
                    """
                    if order.order_line:
                        no_service_product_line = order.order_line.filtered(lambda line: (
                            line.product_id) and (line.product_id.sudo().type != 'service'))
                        if no_service_product_line:
                            product_uom_qty = qty_delivered = 0
                            for line in no_service_product_line:
                                qty_delivered += line.qty_delivered
                                product_uom_qty += line.product_uom_qty
                            if product_uom_qty == qty_delivered:
                                status = """
                                <span class="badge badge-pill bg-success"><i class="fa fa-fw fa-check" aria-label="Fully Delivered" title="Fully Delivered" role="img"></i><span class="d-none d-md-inline"> Fully Delivered</span></span>                      
                                
                                """

                            elif product_uom_qty > qty_delivered and qty_delivered != 0.0:
                                status = """
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-truck" aria-label="Partially Delivered" title="Partially Delivered" role="img"></i><span class="d-none d-md-inline"> Partially Delivered</span></span>       
                                """

                    quot_url = """
                        <a href="%s"><span> %s </span></a>
                        
                        """ % (order.get_portal_url(), order.name)

                    order_dic = {
                        "name": quot_url,
                        "date_order": order.date_order,
                        "status": status,
                    }
                    order_list.append(order_dic)

        values.update({
            "orders": order_list
        })

        return values

    @http.route(['/sh_portal_dashboard/get_last_rfq'], type='json', auth="user", methods=['POST'])
    def get_last_rfq(self, sh_filter_chart_type=False, **kw):
        """ Generate last rfq table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'rfqs': [],
            'is_show_last_rfq_table': False,
        }

        rfq_list = []

        is_installed_purchase = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'purchase'), ('state', '=', 'installed')]).id
        if is_installed_purchase and request.env.company.sh_portal_dashboard_is_show_last_rfq_table:

            values.update({
                'is_show_last_rfq_table': True
            })

            purchase_order_obj = request.env['purchase.order']

            domain = [
#                 ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['sent'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('date_order', '>=', week_date_start),
                    ('date_order', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('date_order', '>=', month_date_start),
                    ('date_order', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('date_order', '>=', year_date_start),
                    ('date_order', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            purchase_orders = purchase_order_obj.sudo().search(domain, order="date_order desc",
                                                               limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if purchase_orders:
                for order in purchase_orders:

                    rfq_url = """
                        <a href="/my/purchase/%s"><span> %s </span></a>
                        
                        """ % (order.id, order.name)

                    order_dic = {
                        "name": rfq_url,
                        "date_order": order.date_order,
                    }
                    rfq_list.append(order_dic)

        values.update({
            "rfqs": rfq_list
        })

        return values

    @http.route(['/sh_portal_dashboard/get_last_purchase_order'], type='json', auth="user", methods=['POST'])
    def get_last_purchase_order(self, sh_filter_chart_type=False, **kw):
        """ Generate last purchase order table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'orders': [],
            'is_show_last_purchase_order_table': False,
        }

        order_list = []

        is_installed_purchase = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'purchase'), ('state', '=', 'installed')]).id
        if is_installed_purchase and request.env.company.sh_portal_dashboard_is_show_last_purchase_order_table:

            values.update({
                'is_show_last_purchase_order_table': True
            })

            purchase_order_obj = request.env['purchase.order']

            domain = [
#                 ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
                ('state', 'in', ['purchase', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('date_order', '>=', fields.Date.to_string(date.today())),
                    ('date_order', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('date_order', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('date_order', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('date_order', '>=', week_date_start),
                    ('date_order', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('date_order', '>=', month_date_start),
                    ('date_order', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('date_order', '>=', year_date_start),
                    ('date_order', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            purchase_orders = purchase_order_obj.sudo().search(domain, order="date_order desc",
                                                               limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if purchase_orders:
                for order in purchase_orders:

                    status = """
                                <span class="badge badge-pill bg-info"><i class="fa fa-fw fa-clock-o" aria-label="Ready" title="Ready" role="img"></i><span class="d-none d-md-inline">Ready</span></span>                       
                    
                    """

                    if order.order_line:
                        no_service_product_line = order.order_line.filtered(
                            lambda line: (line.product_id) and (line.product_id.type != 'service'))
                        if no_service_product_line:
                            product_qty = qty_received = 0
                            for line in no_service_product_line:
                                qty_received += line.qty_received
                                product_qty += line.product_qty
                            if product_qty == qty_received:
                                #                                 status = "Fully Shipped"
                                status = """
                                <span class="badge badge-pill bg-success"><i class="fa fa-fw fa-check" aria-label="Fully Shipped" title="Fully Shipped" role="img"></i><span class="d-none d-md-inline"> Fully Shipped</span></span>                      
                                
                                """

                            elif product_qty > qty_received and qty_received != 0:
                                #                                 status = "Partially Shipped"
                                status = """
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-truck" aria-label="Partially Shipped" title="Partially Shipped" role="img"></i><span class="d-none d-md-inline"> Partially Shipped</span></span>       
                                """

                    order_url = """
                        <a href="/my/purchase/%s"><span> %s </span></a>
                        
                        """ % (order.id, order.name)

                    order_dic = {
                        "name": order_url,
                        "date_order": order.date_order,
                        "status": status,
                    }
                    order_list.append(order_dic)

        values.update({
            "orders": order_list
        })

        return values

    @http.route(['/sh_portal_dashboard/get_last_invoice'], type='json', auth="user", methods=['POST'])
    def get_last_invoice(self, sh_filter_chart_type=False, **kw):
        """ Generate last invoice table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'invoices': [],
            'is_show_last_invoice_table': False,
        }

        invoice_list = []

        is_installed_account = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'account'), ('state', '=', 'installed')]).id
        if is_installed_account and request.env.company.sh_portal_dashboard_is_show_last_invoice_table:

            values.update({
                'is_show_last_invoice_table': True
            })

            account_invoice_obj = request.env['account.move']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
                ('move_type', 'in', ('out_invoice', 'out_refund', 'out_receipt')),
#                 ('type','=','out_invoice')
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(date.today())),
                    ('invoice_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('invoice_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('invoice_date', '>=', week_date_start),
                    ('invoice_date', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('invoice_date', '>=', month_date_start),
                    ('invoice_date', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('invoice_date', '>=', year_date_start),
                    ('invoice_date', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            invoices = account_invoice_obj.sudo().search(domain, order="invoice_date desc",
                                                         limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if invoices:
                for invoice in invoices:

                    status = ""
                    if invoice.payment_state in ['in_payment', 'partial']:
                        status = """
                        
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-clock-o" aria-label="Partial" title="Partial" role="img"></i><span class="d-none d-md-inline">Partial</span></span>    
                                                                                 
                        
                        """
                    elif invoice.payment_state == 'not_paid':
                        status = """
                        
                                <span class="badge badge-pill bg-danger"><i class="fa fa-fw fa-clock-o" aria-label="Not Paid" title="Not Paid" role="img"></i><span class="d-none d-md-inline"> Not Paid</span></span>    
                                                                                 
                        
                        """
                    elif invoice.payment_state in ['paid', 'reversed']:
                        status = """
                        
                                <span class="badge badge-pill bg-success"><i class="fa fa-fw fa-check" aria-label="Paid" title="Paid" role="img"></i><span class="d-none d-md-inline"> Paid</span></span>                  
                        
                        """

                    elif invoice.state == 'cancel':
                        status = """
                        
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-remove" aria-label="Cancelled" title="Cancelled" role="img"></i><span class="d-none d-md-inline"> Cancelled</span></span>                    
                        
                        """

                    invoice_url = """
                        <a href="%s"><span> %s </span></a>
                        
                        """ % (invoice.get_portal_url(), invoice.name if invoice.name else "Draft Invoice")
                    print(invoice_url)

                    invoice_dic = {
                        "name": invoice_url,
                        "invoice_date": invoice.invoice_date,
                        "invoice_date_due": invoice.invoice_date_due,
                        "status": status,
                        "amount_residual": invoice.amount_residual,
                    }
                    invoice_list.append(invoice_dic)
                   

        values.update({
            "invoices": invoice_list
        })

        return values

    @http.route(['/sh_portal_dashboard/get_last_bill'], type='json', auth="user", methods=['POST'])
    def get_last_bill(self, sh_filter_chart_type=False, **kw):
        """ Generate last bill table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'invoices': [],
            'is_show_last_bill_table': False,
        }

        invoice_list = []

        is_installed_account = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'account'), ('state', '=', 'installed')]).id
        if is_installed_account and request.env.company.sh_portal_dashboard_is_show_last_bill_table:

            values.update({
                'is_show_last_bill_table': True
            })

            account_invoice_obj = request.env['account.move']

            domain = [
#                 ('partner_id', 'child_of', [partner.commercial_partner_id.id]),
                ('move_type', 'in', ('in_invoice', 'in_refund', 'in_receipt')),
#                 ('type','=','in_invoice')
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(date.today())),
                    ('invoice_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain += today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('invoice_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('invoice_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('invoice_date', '>=', week_date_start),
                    ('invoice_date', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('invoice_date', '>=', month_date_start),
                    ('invoice_date', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('invoice_date', '>=', year_date_start),
                    ('invoice_date', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            invoices = account_invoice_obj.sudo().search(domain, order="invoice_date desc",
                                                         limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if invoices:
                for invoice in invoices:

                    status = ""
                    if invoice.payment_state in ['in_payment', 'partial']:
                        status = """
                        
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-clock-o" aria-label="Partial" title="Partial" role="img"></i><span class="d-none d-md-inline">Partial</span></span>    
                                                                                 
                        
                        """
                    elif invoice.payment_state == 'not_paid':
                        status = """
                        
                                <span class="badge badge-pill bg-danger"><i class="fa fa-fw fa-clock-o" aria-label="Not Paid" title="Not Paid" role="img"></i><span class="d-none d-md-inline"> Not Paid</span></span>    
                                                                                 
                        
                        """
                    elif invoice.payment_state in ['paid', 'reversed']:
                        status = """
                        
                                <span class="badge badge-pill bg-success"><i class="fa fa-fw fa-check" aria-label="Paid" title="Paid" role="img"></i><span class="d-none d-md-inline"> Paid</span></span>                  
                        
                        """

                    elif invoice.state == 'cancel':
                        status = """
                        
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-remove" aria-label="Cancelled" title="Cancelled" role="img"></i><span class="d-none d-md-inline"> Cancelled</span></span>                    
                        
                        """

                    invoice_url = """
                        <a href="%s"><span> %s </span></a>
                        
                        """ % (invoice.get_portal_url(), invoice.name if invoice.name else "Draft Invoice")

                    invoice_dic = {
                        "name": invoice_url,
                        "invoice_date": invoice.invoice_date,
                        "invoice_date_due": invoice.invoice_date_due,
                        "status": status,
                        "amount_residual": invoice.amount_residual,
                    }
                    invoice_list.append(invoice_dic)

        values.update({
            "invoices": invoice_list
        })

        return values
    @http.route(['/sh_portal_dashboard/get_last_inventory_transfer'], type='json', auth="user", methods=['POST'])
    def get_last_inventory_transfer(self, sh_filter_chart_type=False, **kw):
        """ Generate last inventory transfer table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """

        values = {
            'transfers': [],
            'is_show_last_inventory_transfer_table': False,
        }

        order_list = []

        is_installed_stock = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'stock'), ('state', '=', 'installed')]).id
        if is_installed_stock and request.env.company.sh_portal_dashboard_is_show_last_inventory_transfer_table:

            values.update({
                'is_show_last_inventory_transfer_table': True
            })

            partner = request.env.user.partner_id
            sale_order_obj = request.env['stock.picking']

            domain = [
           
                # ('state', 'in', ['assigned', 'done'])
            ]

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today':
                #filter data by today.
                today_domain = [
                    ('scheduled_date', '>=', fields.Date.to_string(date.today())),
                    ('scheduled_date', '<=', fields.Date.to_string(date.today()))
                ]
                domain = today_domain

            elif sh_filter_chart_type == 'yesterday':
                #filter data by yesterday
                yesterday_domain = [
                    ('scheduled_date', '>=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1))),
                    ('scheduled_date', '<=', fields.Date.to_string(
                        date.today() + relativedelta(days=-1)))
                ]
                domain += yesterday_domain

            elif sh_filter_chart_type == 'current_week':
                #filter data by current week

                week_date_start = date.today() - relativedelta(days=date.today().weekday())
                week_date_end = week_date_start + relativedelta(days=6)

                current_week_domain = [
                    ('scheduled_date', '>=', week_date_start),
                    ('scheduled_date', '<=', week_date_end)
                ]

                domain += current_week_domain

            elif sh_filter_chart_type == 'current_month':
                #filter data by current month

                month_date_start = date.today() + relativedelta(day=1)
                month_date_end = date.today() + relativedelta(day=1, months=+1, days=-1)

                current_month_domain = [
                    ('scheduled_date', '>=', month_date_start),
                    ('scheduled_date', '<=', month_date_end)
                ]

                domain += current_month_domain

            elif sh_filter_chart_type == 'current_year':
                #filter data by current year

                # pick a year from current date
                year = date.today().year
                # create date objects
                year_date_start = date(year, 1, 1)
                year_date_end = date(year, 12, 31)

                current_year_domain = [
                    ('scheduled_date', '>=', year_date_start),
                    ('scheduled_date', '<=', year_date_end)
                ]

                domain += current_year_domain

            #fire searching here
            inventory_transfer = sale_order_obj.sudo().search(domain, order="scheduled_date desc",
                                                       limit=request.env.company.sh_portal_dashboard_is_show_last_record_limit)

            if inventory_transfer:
                for order in inventory_transfer:
                    status = ""

                    if order.state == 'assigned':
                        status = """
                                <span class="badge badge-pill bg-info"><i class="fa fa-fw fa-clock-o" aria-label="Ready" title="Ready" role="img"></i><span class="d-none d-md-inline">Ready</span></span>                       
                    
                    """
                        
                    elif order.state=='done':
                        status = """
                             <span class="badge badge-pill bg-success"><i class="fa fa-fw fa-check" aria-label="Fully Delivered" title="Fully Delivered" role="img"></i><span class="d-none d-md-inline"> Fully Delivered</span></span>                      
                                
                                """

                    elif order.state=='waiting':
                        # picking_type_receipts = 'Receipts'
                         status = """
                        
                                <span class="badge badge-pill bg-warning"><i class="fa fa-fw fa-clock-o" aria-label="Partial" title="Partial" role="img"></i><span class="d-none d-md-inline">Partial</span></span>    
                                                                                 
                        
                        """
               

                    
                    
                    quot_url = """
                        <a href="/my/delieveries/%s"><span> %s </span></a>
                        
                        """ % (order.id if order.id else "#", order.name)
                        
                    order_dic = {
                        "name": quot_url,
                        "date_order": order.scheduled_date,
                        "status": status,
                    }
                    order_list.append(order_dic)

            
        # _logger.exception(order_list)
        values.update({
            "transfers": order_list
        })
        

        return values

    @http.route(['/sh_portal_dashboard/get_products_stock'], type='json', auth="user", methods=['POST'])
    def get_products_stock(self, sh_filter_chart_type=False,products=[], **kw):
        
        """ Generate products stock table.
            :param url : sh_filter_chart_type whether portal user want to show table by today, yesterday, current week, current month, current year etc.
            :returns dict
        """
        # print(products)
        
        values = {
            'products': [],
            'is_show_products_table': False,
        }

        products_list = []

        is_installed_stock = request.env['ir.module.module'].sudo().search(
            [('name', '=', 'stock'), ('state', '=', 'installed')]).id
        if is_installed_stock and request.env.company.sh_portal_dashboard_is_show_products_table:

            values.update({
                'is_show_products_table': True
            })

            # partner = request.env.user.partner_id
            company_lst=[]
            for ids in request.env.user.company_ids:
                company_lst.append(ids.id)
            _logger.exception(company_lst)
            product_list = products.split(", ")
            _logger.exception(product_list)
            product_obj = request.env['product.template'].search([('name',"in",product_list),('company_id',"in",company_lst)])
            _logger.exception(product_obj)
            
            

           

            #if sh_filter_chart_type value = False than assign value today and filter by default today
            if not sh_filter_chart_type:
                sh_filter_chart_type = 'today'

            if sh_filter_chart_type == 'today' or sh_filter_chart_type == 'yesterday' or sh_filter_chart_type == 'current_week' or sh_filter_chart_type == 'current_month' or sh_filter_chart_type == 'current_year':
                domain = []

            inventory_products = product_obj.sudo().search(domain,limit=None)

            if product_obj:
                for product in product_obj:
                    # if product.name in product_list:
                        quot_url = """
                            <a href="/my/products/%s"><span> %s </span></a>
                            
                            """ % (product.id if product.id else "#", product.name)

                        onhand=int(product.qty_available)
                        forcast=int(product.virtual_available)

                        product_dic = {
                            "name": quot_url,
                            "onhand_qty": str(onhand),
                            "forcast_qty": str(forcast),
                        }
                        products_list.append(product_dic)

            
        # _logger.exception(products_list)
        values.update({
            "products": products_list
        })
        

        return values

