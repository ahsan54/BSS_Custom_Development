from odoo import http, fields
from odoo.http import request
from datetime import datetime, date, time, timezone, timedelta
from dateutil.relativedelta import relativedelta
from dateutil import rrule
from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_sale.controllers.main import TableCompute
from openerp.tools.translate import _
from odoo.tools import date_utils
import operator
from collections import OrderedDict
from itertools import groupby
from odoo.exceptions import UserError
import logging
import binascii
from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
# from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.mail import _message_post_helper
# from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.osv import expression
import datetime
import pytz
import logging
import base64
import math

import calendar

from operator import itemgetter

from markupsafe import Markup

from odoo.tools.translate import _
from odoo.tools import groupby as groupbyelem
from odoo.addons.portal.controllers import portal
from odoo.addons.portal.controllers.portal import pager as portal_pager
from odoo.osv.expression import OR, AND

_logger = logging.getLogger(__name__)


# KARIMDAD START
class CustomController(CustomerPortal):

    @http.route(['/my/orders'], type='http', auth="user", website=True, csrf=False)
    def portal_my_orders(self, **kwargs):
        _logger.info('TESTING portal redirect')
        return request.not_found()
        # return request.redirect('/my/home')

    @http.route(['/my/invoices'], type='http', auth="user", website=True, csrf=False)
    def portal_my_invoices(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        _logger.info('TESTING portal redirect')
        return request.not_found()

    @http.route(['/my/quotes'], type='http', auth="user", website=True, csrf=False)
    def portal_my_quotes(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        _logger.info('TESTING portal redirect')
        return request.not_found()

    @http.route(['/my/rfq'], type='http', auth="user", website=True, csrf=False)
    def portal_my_requests_for_quotation(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None,
                                         **kw):
        _logger.info('TESTING portal redirect')
        return request.not_found()
        # KARIMDAD END

    # IZHAN START

    # def filter_tickets(self):
    #     user_u = request.env.user.id

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, filterby='all', search=None,
                            groupby='none', search_in='content', **kw):
        values = self._prepare_portal_layout_values()
        domain = self._prepare_helpdesk_tickets_domain()

        current_user_id = request.env.user.id

        # Add a default filter to only show tickets belonging to the current user
        domain += [('user_id', '=', current_user_id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
            'reference': {'label': _('Reference'), 'order': 'id'},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc'},
        }
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'assigned': {'label': _('Assigned'), 'domain': [('user_id', '!=', False)]},
            'unassigned': {'label': _('Unassigned'), 'domain': [('user_id', '=', False)]},
            'open': {'label': _('Open'), 'domain': [('close_date', '=', False)]},
            'closed': {'label': _('Closed'), 'domain': [('close_date', '!=', False)]},
            'last_message_sup': {'label': _('Last message is from support')},
            'last_message_cust': {'label': _('Last message is from customer')},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>'))},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'id': {'input': 'id', 'label': _('Search in Reference')},
            'status': {'input': 'status', 'label': _('Search in Stage')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage_id', 'label': _('Stage')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        if filterby in ['last_message_sup', 'last_message_cust']:
            discussion_subtype_id = request.env.ref('mail.mt_comment').id
            messages = request.env['mail.message'].sudo().search_read(
                [('model', '=', 'helpdesk.ticket'), ('subtype_id', '=', discussion_subtype_id)],
                fields=['res_id', 'author_id'], order='date desc')
            last_author_dict = {}
            for message in messages:
                if message['res_id'] not in last_author_dict:
                    last_author_dict[message['res_id']] = message['author_id'][0]

            ticket_author_list = request.env['helpdesk.ticket'].sudo().search_read(fields=['id', 'partner_id'])
            ticket_author_dict = dict(
                [(ticket_author['id'], ticket_author['partner_id'][0] if ticket_author['partner_id'] else False) for
                 ticket_author in ticket_author_list])

            last_message_cust = []
            last_message_sup = []
            ticket_ids = set(last_author_dict.keys()) & set(ticket_author_dict.keys())
            for ticket_id in ticket_ids:
                if last_author_dict[ticket_id] == ticket_author_dict[ticket_id]:
                    last_message_cust.append(ticket_id)
                else:
                    last_message_sup.append(ticket_id)

            if filterby == 'last_message_cust':
                domain = AND([domain, [('id', 'in', last_message_cust)]])
            else:
                domain = AND([domain, [('id', 'in', last_message_sup)]])

        else:
            domain = AND([domain, searchbar_filters[filterby]['domain']])

        if date_begin and date_end:
            domain = AND([domain, [('create_date', '>', date_begin), ('create_date', '<=', date_end)]])

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                discussion_subtype_id = request.env.ref('mail.mt_comment').id
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search),
                                                    ('message_ids.subtype_id', '=', discussion_subtype_id)]])
            if search_in in ('status', 'all'):
                search_domain = OR([search_domain, [('stage_id', 'ilike', search)]])
            domain = AND([domain, search_domain])

        # pager
        tickets_count = request.env['helpdesk.ticket'].sudo().search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'search_in': search_in,
                      'search': search, 'groupby': groupby, 'filterby': filterby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )

        tickets = request.env['helpdesk.ticket'].sudo().search(domain, order=order, limit=self._items_per_page,
                                                               offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].sudo().concat(*g) for k, g in
                               groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        my_tickets = request.env['helpdesk.ticket'].sudo().search([('partner_id', '=', request.env.user.partner_id.id)])
        # if my_tickets:
        # raise UserError(my_tickets)

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'my_tickets': my_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_filters': searchbar_filters,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
            'filterby': filterby,
        })

        return request.render("helpdesk.portal_helpdesk_ticket", values)

    # IZHAN END

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        employee = request.env.user.employee_ids

        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("sh_portal_dashboard.sh_portal_dashboard_portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


# class BssPortal(http.Controller):

# @http.route(['/my/attendance/detail'], type='http', auth="user", website=True)
# def portal_my_attendance_detail(self, **kw):
#     if request.httprequest.method == 'POST':

#         from_date = kw.get('from_date')
#         to_date = kw.get('to_date')

#         if not from_date or not to_date:
#             raise UserError("Date field should not be empty")

#         return request.render("sh_portal_dashboard.portal_my_attendance_detail")


#         return request.render("sh_portal_dashboard.portal_my_attendance_detail")


class BssPortal(http.Controller):

    ## Huzaifa
    @http.route(['/my/attendance/detail'], type='http', auth="user", website=True, csrf=False)
    def portal_my_attendance_detail(self, search=None, search_in=None, **kw):
        return request.render("sh_portal_dashboard.portal_my_attendance_detail")
        # attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id)], order='id desc' )
        # check_in = []
        # check_out = []
        # for att in attendance:
        #     user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
        #     check_in.append(pytz.utc.localize(att.check_in).astimezone(user_tz).time())
        #     if att.check_out:
        #         check_out.append(pytz.utc.localize(att.check_out).astimezone(user_tz).time())
        #     # make worked hours in 2 digit format
        #     if att.worked_hours:
        #         att.worked_hours = "{0:.2f}".format(att.worked_hours)

        # values = {
        #     'attendances': attendance,
        #     'check_in': check_in,
        #     'check_out': check_out,
        #     }

        # instance_attendance = request.env['hr.attendance'].sudo().search([], order='id desc' )

        # domain=[('employee_id', '=', request.env.user.employee_ids.id)
        # ]
        # if search and search_in:
        #     domain.append(('name', 'ilike', search))

        # instance_attendance_count = instance_attendance.search_count(domain)

        # pager = request.website.pager(
        #     url="/my/attendance",
        #     url_args={'search': search, 'search_in': 'all'},
        #     total=instance_attendance_count,
        #     page=page,
        #     step=10
        # )

        # confirmed_attendance = instance_attendance.search(domain, limit=10, offset=pager['offset'])

        # searchbar_inputs = {
        #     'all': {'input': 'all', 'label': _('Search in All')},
        #     # 'externalId': {'input': 'external_id', 'label': _('Search in  External ID')},
        # }
        # values.update({
        #     'attendances': confirmed_attendance,
        #     'page_name': 'attendance',
        #     'default_url': '/my/attendance',
        #     'pager': pager,
        #     'search_in': 'all',
        #     'searchbar_inputs': searchbar_inputs,

        # })

        # return request.render("sh_portal_dashboard.portal_my_attendance_detail")

    @http.route(['/my/attendance', '/my/attendance/page/<int:page>'], type='http', auth="user", website=True,
                csrf=False)
    def portal_my_attendance(self, page=1, search=None, search_in=None, from_date=None, to_date=None, **kw):
        ## Huzaifa
        # if page == 2: 
        #     raise UserError([page,from_date])

        # if page==1:
        #     from_date = kw.get('from_date') # Error: from_date = None
        #     to_date = kw.get('to_date')

        # else: 
        #     raise UserError([from_date, type(from_date)]) 

        if not from_date or not to_date:
            raise UserError("Date field(s) cannot be empty!")

        current_datetime = datetime.datetime.now()

        # Strip out the time component if it exists
        from_date = from_date.split()[0] if ' ' in from_date else from_date
        to_date = to_date.split()[0] if ' ' in to_date else to_date

        try:
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d')
        except ValueError:
            raise UserError("Incorrect from_date format. Expected YYYY-MM-DD.")

        try:
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            raise UserError("Incorrect to_date format. Expected YYYY-MM-DD.")

        difference = current_datetime - from_date_obj
        days_difference = difference.days

        if days_difference > 45:
            raise UserError("Date before 45th day cannot be selected")

        _logger.info("from_date: %s", from_date)
        _logger.info("to_date: %s", to_date)

        ### Ali

        from_date = str(from_date)
        to_date = str(to_date)

        from_date_obj = datetime.datetime.strptime(from_date, "%Y-%m-%d")
        to_date_obj = datetime.datetime.strptime(to_date, "%Y-%m-%d")

        from_date_with_time = datetime.datetime.combine(from_date_obj.date(), time.min)
        to_date_with_time = datetime.datetime.combine(to_date_obj.date(), time.max)

        # from_date_obj = from_date_with_time.datetime.datetime.strftime("%Y-%m-%d %H:%M:%S")
        # to_date_obj = to_date_with_time.datetime.datetime.strftime("%Y-%m-%d %H:%M:%S")

        # domain.append(('check_in.date','<=',from_date_obj.date()))
        # domain.append(('check_in.date','>=',to_date_obj.date()))
        # raise UserError([from_date_obj.date(),to_date_obj.date()])

        attendance = request.env['hr.attendance'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id),
                                                                 ('check_in', '>=', from_date_obj),
                                                                 ('check_in', '<=', to_date_obj)], order='id desc')
        # raise UserError([attendance,from_date_obj,to_date_obj])

        check_in = []
        check_out = []
        for att in attendance:
            user_tz = pytz.timezone('Asia/Karachi')
            temp1 = pytz.utc.localize(att.check_in).astimezone(user_tz).time()
            check_in.append(datetime.datetime.combine(att.check_in.date(), temp1))  # Combine date and time)
            if att.check_out:
                temp2 = pytz.utc.localize(att.check_out).astimezone(user_tz).time()
                check_out.append(datetime.datetime.combine(att.check_out.date(), temp2))  # Combine date and time)
                # check_out.append(att.check_out)
            # make worked hours in 2 digit format
            if att.worked_hours:
                att.worked_hours = "{0:.2f}".format(att.worked_hours)

        # check_in = [time + timedelta(hours=5) for time in check_in]
        # check_out = [time + timedelta(hours=5) for time in check_out]

        values = {
            'attendances': attendance,
            'check_in': check_in,
            'check_out': check_out,
        }

        instance_attendance = request.env['hr.attendance'].sudo().search([], order='id desc')

        domain = [('employee_id', '=', request.env.user.employee_ids.id)
                  ]
        domain.append(('check_in', '>=', from_date_obj))
        domain.append(('check_in', '<=', to_date_obj))

        if search and search_in:
            domain.append(('name', 'ilike', search))

        instance_attendance_count = instance_attendance.search_count(domain)
        leave_status_dict = {
            'half_day': 'Half-Day',
            'late': 'Late',
            'ok': 'Ok',
            'absent': 'Absent',
            'early': 'Early',
            'early_out': 'Early Out'
        }
        pager = request.website.pager(
            url="/my/attendance",
            url_args={'search': search, 'search_in': 'all', "from_date": from_date, "to_date": to_date},
            total=instance_attendance_count,
            page=page,
            step=10
        )

        confirmed_attendance = instance_attendance.search(domain, limit=10, offset=pager['offset'])
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            # 'externalId': {'input': 'external_id', 'label': _('Search in  External ID')},
        }
        values.update({
            'attendances': confirmed_attendance,
            'status_dict': leave_status_dict,
            'page_name': 'attendance',
            'default_url': '/my/attendance',
            'pager': pager,
            'search_in': 'all',
            'searchbar_inputs': searchbar_inputs,
            'from_date': from_date,
            'to_date': to_date,

        })

        _logger.info(
            "Page: " + str(pager['offset']) + " Offset: " + str(page) + " Dictionary: " + str(confirmed_attendance))

        # raise UserError(str(confirmed_attendance))

        return request.render("sh_portal_dashboard.portal_my_attendance", values)

    @http.route('/my/checkin_checkout', type='http', auth="user", website=True)
    def portal_my_checkin_checkout(self, **kw):
        check_req_wfh = request.env['wfh_request'].sudo().search(
            [('employee_name', '=', request.env.user.employee_ids.id), ('state', '=', 'approve')], order='id desc',
            limit=1)
        if check_req_wfh:
            # if already check in then check out button will be visible other wise check in button will be visible
            checkin = False
            checkout = False
            attendance = request.env['hr.attendance'].sudo().search(
                [('employee_id', '=', request.env.user.employee_ids.id), ('check_out', '=', False)], order='id desc',
                limit=1)
            if attendance:
                checkin = True
                checked_in_time = f"Check In Time {attendance.check_in}"
            else:
                checked_in_time = False
                checkout = True
            return request.render("sh_portal_dashboard.portal_my_checkin_checkout",
                                  {'checked_in': checkin, 'checkout': checkout, 'checked_in_time': checked_in_time})

        ## Huzaifa
        return request.redirect('/my/attendance/detail')
        # return request.redirect('/my/attendance')

    @http.route('/my/attendance/checkin', type='http', auth="user", website=True)
    def portal_my_checkin(self, **kw):
        check_in = datetime.datetime.now()
        # user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
        # check_in = pytz.utc.localize(check_in).astimezone(user_tz)
        attendance = request.env['hr.attendance'].sudo().create({'employee_id': request.env.user.employee_ids.id,
                                                                 'check_in': check_in.strftime("%Y-%m-%d %H:%M:%S")})
        return request.redirect('/my/checkin_checkout')

    @http.route('/my/attendance/checkout', type='http', auth="user", website=True)
    def portal_my_checkout(self, **kw):
        attendance = request.env['hr.attendance'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('check_out', '=', False)], order='id desc',
            limit=1)
        if attendance:
            check_out = datetime.datetime.now()
            # user_tz = pytz.timezone(request.env.context.get('tz') or request.env.user.tz or 'UTC')
            # check_out = pytz.utc.localize(check_out).astimezone(user_tz).time()
            attendance.check_out = check_out.strftime("%Y-%m-%d %H:%M:%S")
        return request.redirect('/my/attendance')

    @http.route('/my/req_leave', type='http', auth="user", website=True)
    def portal_my_req_leave(self, **kw):
        ### KARIMDAD START ###
        # employee_request = request.env['hr.leave'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id),('state','not in',['validate','refuse'])], order='id desc' )
        employee_request = request.env['hr.leave'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id)], order='id desc')
        hr_employee_details = request.env['hr.employee'].sudo().search(
            [('user_id', '=', request.env.user.employee_ids.id)])
        hr_leave_type = request.env['hr.leave.type'].sudo().search([('id', '!=', 0)])
        wfh_requests = request.env['wfh_request'].sudo().search(
            [('employee_name.id', '=', request.env.user.employee_ids.id)], order='create_date desc')
        approval_status = {
            'draft': 'New',
            'submit_for_approval': 'Submit for Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
        }
        # raise UserError(wfh_requests)
        # raise UserError(valid_holiday_types[0].id)
        # valid_holiday_types = []
        # for rec in hr_leave_allocation:
        #     valid_holiday_types.append(rec.holiday_status_id)

        # Maaz start
        leaves_dict = {}
        hr_leave_allocations = request.env['hr.leave.allocation'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', '=', 'validate')])
        for allocation in hr_leave_allocations:
            leaves = request.env['hr.leave'].sudo().search([('employee_id', '=', request.env.user.employee_ids.id),
                                                            ('holiday_status_id', '=', allocation.holiday_status_id.id),
                                                            ('state', '=', 'validate')])
            if allocation.holiday_status_id.name in leaves_dict.keys():
                leaves_dict[allocation.holiday_status_id.name][
                    'allocated'] += allocation.number_of_days_display if allocation.number_of_days_display >= 1 else 0
            else:
                leaves_dict[allocation.holiday_status_id.name] = {}
                leaves_dict[allocation.holiday_status_id.name][
                    'allocated'] = allocation.number_of_days_display if allocation.number_of_days_display >= 1 else 0
                leaves_dict[allocation.holiday_status_id.name]['used'] = 0

                for leave in leaves:
                    leaves_dict[allocation.holiday_status_id.name]['used'] += leave.number_of_days_display

        return request.render("sh_portal_dashboard.portal_my_req_leave",
                              {'employee_request': employee_request,
                               'hr_employee_details': hr_employee_details,
                               'hr_leave_type': hr_leave_type,
                               'leaves_dict': leaves_dict,
                               'wfh_requests': wfh_requests,
                               'approval_status': approval_status})

        # Maaz end

        ### KARIMDAD END ###

    @http.route('/my/leave/request', type='http', auth="user", website=True, csrf=False)
    def portal_my_leave_request(self, **kw):
        current_employee = request.env.user.employee_ids
        current_date = datetime.datetime.now().date().strftime("%B %d, %Y")

        if not current_employee:
            raise UserError("No employee record is linked to this user. Please contact the HR department.")

        # Fetch allocated leave types for the current employee
        hr_leave_allocations = request.env['hr.leave.allocation'].sudo().search([
            ('employee_id', '=', current_employee.id)
        ])
        allocated_leave_types = hr_leave_allocations.mapped('holiday_status_id')

        # Add unpaid leave if it's globally available
        unpaid_leave_type = request.env['hr.leave.type'].sudo().search([('name', 'ilike', 'Unpaid')], limit=1)
        if unpaid_leave_type:
            allocated_leave_types |= unpaid_leave_type

        # Handle POST requests for leave submissions
        if request.httprequest.method == 'POST':
            leave_type_id = kw.get('leave_type')
            if not leave_type_id:
                raise UserError('Please choose a Leave Type for this request!')

            leave_type = request.env['hr.leave.type'].sudo().browse(int(leave_type_id))
            if leave_type not in allocated_leave_types:
                raise UserError("You are not allocated this leave type. Please choose a valid leave type.")

            half_day = kw.get('half_day') == 'on'  # Convert checkbox value to boolean
            reason = kw.get('notes')

            if half_day:
                half_day_date_key = kw.get('half_day_date')
                if not half_day_date_key:
                    raise UserError("Please provide a date for the half-day leave.")

                # Parse and set the half-day date
                half_day_date = datetime.datetime.strptime(half_day_date_key, '%Y-%m-%d').date()
                date_from = datetime.datetime.combine(half_day_date, time(hour=9, minute=0)) - timedelta(hours=5)

                # Set the duration to 0.5 for half-day
                number_of_days = 0.5

                # Create the leave request for half-day
                leave_request = request.env['hr.leave'].sudo().create({
                    'employee_id': current_employee.id,
                    'holiday_status_id': leave_type.id,
                    'request_date_from': half_day_date,
                    'request_date_to': half_day_date,  # End date (same as start for half-day)
                    'date_from': date_from,  # Datetime start
                    'date_to': date_from,  # Datetime end (same as start)
                    'name': reason,
                    'number_of_days': number_of_days,
                    'request_unit_half': True,  # Indicates it's a half-day leave
                })

            else:
                # Parse and validate full-day dates
                date_from_key = kw.get('date_from')
                date_to_key = kw.get('date_to')
                if not date_from_key or not date_to_key:
                    raise UserError('Please select valid start and end dates')

                date_from_obj = datetime.datetime.strptime(date_from_key, '%Y-%m-%d').date()
                date_to_obj = datetime.datetime.strptime(date_to_key, '%Y-%m-%d').date()

                # Assuming the workday is from 9 AM to 5 PM for a full day
                time_from = time(hour=9, minute=0)
                time_to = time(hour=17, minute=0)

                # Calculate full-day leave times
                date_from = datetime.datetime.combine(date_from_obj, time_from) - timedelta(hours=5)
                date_to = datetime.datetime.combine(date_to_obj, time_to) - timedelta(hours=5)

                # Calculate the number of days based on the difference in dates
                number_of_days = (date_to_obj - date_from_obj).days + 1  # Inclusive of start and end date

                # Create the leave request for full-day
                leave_request = request.env['hr.leave'].sudo().create({
                    'employee_id': current_employee.id,
                    'holiday_status_id': leave_type.id,
                    'request_date_from': date_from,
                    'date_from': date_from,
                    'request_date_to': date_to,
                    'date_to': date_to,
                    'name': reason,
                    'number_of_days': number_of_days,
                })

            # Redirect to the leave request confirmation page
            return request.redirect('/my/req_leave')

        return request.render("sh_portal_dashboard.portal_my_leave_request", {
            'current_employee': current_employee.name,
            'current_date': current_date,
            'leave_types': allocated_leave_types,
        })

    # @http.route('/my/leave/request', type='http', auth="user", website=True, csrf=False)
    # def portal_my_leave_request(self, **kw):
    #     current_employee = request.env.user.employee_ids.name
    #     current_date = datetime.datetime.now().date().strftime("%B %d, %Y")
    #     hr_leave_allocation = request.env['hr.leave.allocation'].sudo().search(
    #         [('employee_id', '=', request.env.user.employee_ids.id)])
    #     unpaid_leave_id = request.env['hr.leave.type'].sudo().search([('name', 'like', 'Unpaid')])
    #
    #     valid_holiday_types = []
    #     valid_holiday_types.append(unpaid_leave_id)
    #     for rec in hr_leave_allocation:
    #         if rec.holiday_status_id not in valid_holiday_types:
    #             valid_holiday_types.append(rec.holiday_status_id)
    #
    #     if request.httprequest.method == 'POST':
    #         employee_id = request.env.user.name
    #         emp_id = request.env.user.id
    #
    #         if kw.get('leave_type'):
    #             leave_type = request.env['hr.leave.type'].sudo().search([('id', '=', int(kw.get('leave_type')))])
    #         else:
    #             raise UserError('Please choose a Leave Type for this request!')
    #         date_to_key = kw.get('date_to')
    #         date_from_key = kw.get('date_from')
    #
    #         reason = kw.get('notes')
    #
    #         year, month, day = (int(i) for i in str(date_from_key).split('-'))
    #         dayNumber = calendar.weekday(year, month, day)
    #
    #         current_employee = request.env['hr.employee'].sudo().search([('user_id', '=', emp_id)])
    #         # emp_id = request.env['hr.employee'].sudo().search([('name','=',employee_id)])
    #         # raise UserError(str([current_employee.name, emp_id]))
    #
    #         time_from = None
    #         time_to = None
    #         time_to_obj = time_from_obj = None
    #         for line in current_employee.resource_calendar_id.attendance_ids:
    #             # raise UserError(line)
    #             if int(line.dayofweek) not in [5, 6]:
    #                 time_to = line.hour_to
    #                 time_from = line.hour_from
    #
    #                 time_to_obj = time(hour=int(time_to), minute=0, second=0)
    #                 time_from_obj = time(hour=int(time_from), minute=0, second=0)
    #                 break
    #
    #         date_from_obj = datetime.datetime.strptime(date_from_key, '%Y-%m-%d').date()
    #         date_to_obj = datetime.datetime.strptime(date_to_key, '%Y-%m-%d').date()
    #
    #         date_from = datetime.datetime.combine(date_from_obj, time_from_obj) - timedelta(hours=5)
    #         date_to = datetime.datetime.combine(date_to_obj, time_to_obj) - timedelta(hours=5)
    #         print(f'current_employee: {current_employee}')
    #         print(f'holiday_status_id: {leave_type}')
    #         print(f'request_date_from: {date_from}')
    #         print(f'request_date_to: {date_to}')
    #         print(f'name: {reason}')
    #         leave_request = request.env['hr.leave'].sudo().create(
    #             {'employee_id': current_employee.id, 'holiday_status_id': leave_type.id, 'request_date_from': date_from,
    #              'date_from': date_from, 'request_date_to': date_to, 'date_to': date_to, 'name': reason})
    #
    #         Attachment = request.env['ir.attachment'].sudo()
    #         file = kw.get('att')
    #         if file:
    #             attachment_id = Attachment.create({
    #                 'name': file.filename,
    #                 'type': 'binary',
    #                 'datas': base64.encodebytes(file.read()),
    #                 'res_model': leave_request._name,
    #                 'res_id': leave_request.id
    #             })
    #
    #             # Use sudo() to update the leave request with the attachment
    #             leave_request.sudo().write({
    #                 'number_of_days': math.ceil(leave_request.number_of_days),
    #                 'attachment_ids': [(4, attachment_id.id)],
    #             })
    #         else:
    #             # If no attachment, still update the leave request safely
    #             leave_request.sudo().write({
    #                 'number_of_days': math.ceil(leave_request.number_of_days),
    #             })
    #         # raise UserError(str(leave_request.read()))
    #         return request.redirect('/my/req_leave')
    #     return request.render("sh_portal_dashboard.portal_my_leave_request",
    #                           {'current_employee': current_employee, 'current_date': current_date,
    #                            'valid_holiday_types': valid_holiday_types})

    @http.route('/my/wfh/request', type='http', auth="user", website=True, csrf=False)
    def portal_my_wfh_request(self, **kw):
        current_employee = request.env.user.employee_ids.name
        # as reason is selection field now get all the reason from the selection field
        if request.httprequest.method == 'POST':
            employee_id = request.env.user.employee_ids.id
            date_from = kw.get('date_from')
            date_to = kw.get('date_to')
            reason = kw.get('reason')
            leave_request = request.env['wfh_request'].sudo().create(
                {'employee_name': employee_id, 'from_date': date_from, 'to_date': date_to, 'reason': reason})
            return request.redirect('/my/req_leave')
        return request.render("sh_portal_dashboard.portal_my_wfh_request", {'current_employee': current_employee})

    @http.route('/my/loan/approved', type='http', auth="user", website=True)
    def portal_my_approved_req_leave(self, **kw):
        # get all loan request of current employee having approved state
        loan_request = request.env['hr.loan'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', '=', 'approve')], order='id desc')
        if loan_request.installment > 0:
            payment_per_month = loan_request.total_amount / loan_request.installment
            remaining_installment = loan_request.installment - (loan_request.total_paid_amount / payment_per_month)
        else:
            remaining_installment = 0
        return request.render("sh_portal_dashboard.portal_my_req_loan_approved",
                              {'loan_request': loan_request, 'remaining_installment': remaining_installment})

    @http.route('/my/req_loan', type='http', auth="user", website=True)
    def portal_my_req_loan(self, **kw):
        # get all loan request of current employee
        loan_request = request.env['hr.loan'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', '!=', 'approve')], order='id desc')
        return request.render("sh_portal_dashboard.portal_my_req_loan", {'loan_request': loan_request})

    @http.route('/my/loan/request', type='http', auth="user", website=True, csrf=False)
    def portal_my_loan_request(self, **post):
        current_employee = request.env.user.employee_ids.name
        current_date = datetime.datetime.now().date().strftime("%B %d, %Y")
        if request.httprequest.method == 'POST':
            employee_id = request.env.user.employee_ids.id
            loan_amount = post.get('loan_amount')
            no_of_installment = post.get('no_of_installment')
            req_type = post.get('req_type')
            loan_request = request.env['hr.loan'].sudo().create(
                {'employee_id': employee_id, 'loan_amount': loan_amount, 'installment': no_of_installment,
                 'req_type': req_type})
            return request.redirect('/my/req_loan')
        return request.render("sh_portal_dashboard.portal_my_loan_request",
                              {'current_employee': current_employee, 'current_date': current_date})




    @http.route('/my/req_salary_slip', type='http', auth="user", website=True)
    def portal_my_req_salary_slip(self):
        employee_name = request.env.user.employee_ids.name
        payslips = request.env['hr.payslip'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id),
             ('date_from', '<=', datetime.date.today())], order='date_from desc', limit=3)
        return request.render("sh_portal_dashboard.portal_my_req_salary_slip",
                              {'employee_name': employee_name, 'payslips': payslips})

    @http.route('/my/tax_certificate/<int:pay_id>', type='http', auth="user", website=True)
    def request_tax_certificate(self, pay_id, **kw):
        # Get the specific payslip
        payslip = request.env['hr.payslip'].sudo().browse(pay_id)
        if payslip:
            # Update the req_tax_certificate field to True
            payslip.sudo().write({'req_tax_certificate': True})

            # Find or create the category for this approval request
            category = request.env['approval.category'].sudo().search([('name', '=', 'Tax Certificate Approvals')],
                                                                      limit=1)
            if not category:
                category = request.env['approval.category'].sudo().create({'name': 'Tax Certificate Approvals'})

            # Create the approval request with the required category_id
            approval_request = request.env['approval.request'].sudo().create({
                'name': 'Send the Tax Certificate of the attached payslip to the relevant employee via email.',
                'request_owner_id': request.env.user.id,
                'category_id': category.id,
                'request_status': 'pending',
                'payslip_id': payslip.id
            })

            # Alternatively, call action_confirm() to handle status transitions
            approval_request.action_confirm()

            # # Schedule an activity for the created approval request
            # approval_request.activity_schedule(
            #     activity_type_id=request.env.ref('mail.mail_activity_data_todo').id,
            #     summary="Approval Required..!",
            #     user_id=26,  # Assign the activity to a specific user (e.g., User ID 26)
            #     note="Please review and approve this Tax Certificate request.",
            #     date_deadline=fields.Date.today(),
            # )

        # Redirect back to the salary slip page
        return request.redirect('/my/req_salary_slip')

    # @http.route('/my/tax_certificate', type='http', auth="user", website=True)
    # def portal_my_req_tax_certificate(self, **kw):
    #     # Find or create the category for this approval request
    #     category = request.env['approval.category'].search([('name', '=', 'Tax Certificate Approvals')], limit=1)
    #     if not category:
    #         # Optional: Create a new category if not found
    #         category = request.env['approval.category'].create({
    #             'name': 'Tax Certificate Approvals',
    #         })
    #
    #     # Create the approval request with the required category_id
    #     approval_request = request.env['approval.request'].create({
    #         'name': 'Tax Certificate Approval',  # Name of the approval request
    #         'request_owner_id': request.env.user.id,  # Assign to the current portal user
    #         'category_id': category.id,  # Required field: Category ID
    #     })
    #
    #     # Schedule an activity for the created approval request
    #     approval_request.activity_schedule(
    #         activity_type_id=request.env.ref('mail.mail_activity_data_todo').id,
    #         summary="Approval Required..!",
    #         user_id=26,  # Assign the activity to a specific user (e.g., User ID 2)
    #         note="Please review and approve this Tax Certificate request.",
    #         date_deadline=fields.Date.today(),
    #     )
    #
    #     # Render the portal view
    #     return request.render("sh_portal_dashboard.portal_my_req_salary_slip")
    # @http.route('/my/tax_certificate', type='http', auth="user", website=True)
    # def portal_my_req_tax_certificate(self, **kw):
    #     # Get the partner linked to user ID 26
    #     user = request.env['res.users'].browse(2)
    #     partner = user.partner_id
    #
    #     if partner:
    #         partner.activity_schedule(
    #             activity_type_id=request.env.ref('mail.mail_activity_data_todo').id,
    #             summary="Approval Required..!",
    #             user_id=2,  # Assign the activity to user ID 26
    #             note="Please review and approve this Tax Certificate request.",
    #             date_deadline=fields.Date.today(),
    #         )
    #
    #     # Render the portal view
    #     return request.render("sh_portal_dashboard.portal_my_req_salary_slip")

    def submit_for_approval_payslip(self, payslip, slip_reason):
        approval_category_id = request.env['approval.category'].sudo().search([('name', '=', 'Salary Slip Approval')],
                                                                              limit=1)

        admin = request.env['res.users'].sudo().search(
            [('groups_id', 'in', request.env.ref('base.group_erp_manager').id)], limit=1)
        approvers = [(0, 0, {'user_id': admin.id})]

        approval = request.env['approval.request'].sudo().create({
            'name': f"Salary Slip Portal Approval {payslip.name}",
            'request_owner_id': request.env.user.employee_ids.user_id.id,
            'category_id': 61 or approval_category_id.id,
            'print_payslip_id': payslip.id,
            'payslip_id': payslip.id,
            'request_type': 'salary_slip_portal_approval',
            'reason': slip_reason,
        })
        # request.env.cr.commit()

        payslip.print_request_ids = [(4, approval.id, 0)]
        # approval.request_ids=[(4, approval.id, 0)]
        approval.action_confirm()




    @http.route('/my/req_salary_slip/<int:pay_id>', type='http', auth="user", website=True, csrf=False)
    def portal_my_req_salary_slip_for_approve(self, pay_id, **kw):
        employee_name = request.env.user.employee_ids.name
        slip_reason = kw.get('slip_reason')  # Get the slip_reason value from the request
        print(f'slip_reason: {slip_reason}')
        payslips = request.env['hr.payslip'].sudo().search([
            ('employee_id', '=', request.env.user.employee_ids.id),
            ('state', 'in', ['done', 'paid']), ('date_from', '<=', datetime.date.today())
        ], order='date_from desc', limit=3)

        if pay_id:
            # If 'pay_id' is provided in the URL, update the corresponding payslip record
            payslip = request.env['hr.payslip'].sudo().browse(pay_id)
            if payslip:
                self.submit_for_approval_payslip(payslip, slip_reason)
                payslip.sudo().write({'is_request_salary_slip': True, 'status_request_slip': 'Pending'})

        return request.redirect('/my/req_salary_slip')

    @http.route('/my/salary_slip_print/<int:pay_id>', type='http', auth="user", website=True)
    def portal_my_salary_slip_print(self, pay_id, **kw):

        if pay_id:
            payslip = request.env['hr.payslip'].sudo().browse(pay_id)
            pdf = request.env['ir.actions.report'].sudo()._render_qweb_pdf('custom_reports.custom_payslip_report_id',
                                                                           [pay_id])[0]
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf)),
                ('Content-Disposition', f'attachment; filename={payslip.display_name}.pdf')
            ]
            return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route('/my/req_for_exp', type='http', auth="user", website=True)
    def portal_my_req_expense(self, **kw):
        expense_request = request.env['hr.expense'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', 'not in', ['approved', 'done'])],
            order='id desc')
        return request.render("sh_portal_dashboard.portal_my_req_for_expense", {'expense_request': expense_request})



    @http.route('/my/expense/approved', type='http', auth="user", website=True)
    def portal_my_req_approved_exp(self, **kw):
        expense_request = request.env['hr.expense'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', 'in', ['approved', 'done'])],
            order='id desc')
        return request.render("sh_portal_dashboard.portal_my_approved_req_for_expense",
                              {'expense_request': expense_request})

    @http.route('/my/expense/request', type='http', auth="user", website=True, csrf=False)
    def portal_my_expense_request(self, **post):
        current_employee = request.env.user.employee_ids.name
        current_date = datetime.datetime.now().date().strftime("%B %d, %Y")
        # as the field product_id in hr.expense i need to show on my form view so i need all the list of product from hr.expense place it in varieble categories and pass it to the form view
        categories = request.env['product.product'].sudo().search([('can_be_expensed', '=', True)])
        if request.httprequest.method == 'POST':
            employee_id = request.env.user.employee_ids.id

            total_amount = post.get('total_amount')
            # if amount is empty raise Error
            if total_amount == "":
                raise UserError("Please Enter Total Amount")
            description = post.get('description')
            if description == "":
                raise UserError("Description not set")
            category = post.get('Category')
            if category is None:
                raise UserError("No Category Selected")
            # expense_id = request.env.user.expense_id

            # code for sending attachment goes here
            Attachment = request.env['ir.attachment']
            # partner_id = request.env.user.partner_id

            file = post.get('att')
            # raise UserError(str([file.filename]))

            expense_request = request.env['hr.expense'].sudo().create(
                {'employee_id': employee_id, 'total_amount': total_amount, 'name': description, 'product_id': category,
                 'product_uom_id': 7})
            attachment_id = Attachment.sudo().create({
                'name': file.filename,
                'type': 'binary',
                'datas': base64.encodebytes(file.read()),
                'res_model': expense_request._name,
                'res_id': expense_request.id
            })
            expense_request.sudo().write({
                'attachment_ids': [(4, attachment_id.id)],
            })

            return request.redirect('/my/req_for_exp')
        return request.render("sh_portal_dashboard.portal_my_expense_request",
                              {'current_employee': current_employee, 'current_date': current_date,
                               'categories': categories})

    # M.Arsalan
    @http.route('/my/req_Appraisal', type='http', auth="user", website=True)
    def portal_my_req_Appraisal(self, **kw):
        expense_request = request.env['hr.expense'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', 'not in', ['approved', 'done'])],
            order='id desc')
        return request.render("sh_portal_dashboard.portal_my_req_Appraisal", {'expense_request': expense_request})

    # Syed Owais Noor
    @http.route('/my/req_loan_and_advance', type='http', auth="user", website=True)
    def portal_my_req_Loan(self, **kw):
        loan_request = request.env['hr.loan'].sudo().search(
            [('employee_id', '=', request.env.user.employee_ids.id), ('state', 'not in', ['approved'])],
            order='id desc')
        loan_states = {
            'draft': 'Draft',
            'waiting_approval_1': 'Submitted',
            'waiting_approval_2': 'Waiting Approval',
            'approve': 'Approved',
            'refuse': 'Refused',
            'cancel': 'Canceled'

        }
        return request.render("sh_portal_dashboard.portal_my_req_loan_and_advance",
                              {'loan_request': loan_request, 'loan_states': loan_states})



    # BSS Team Development

    @http.route('/my/loan_details/<int:loan_id>', type='http', auth="user", website=True, csrf=False)
    def portal_loan_details(self, loan_id, **post):
        current_user = request.env.user
        loan = request.env['hr.loan'].sudo().search([
            ('id', '=', loan_id),
            ('employee_id.user_id', '=', current_user.id)
        ], limit=1)

        if not loan:
            return request.render(
                "website.page_404")

        # Prepare data for the template
        loan_data = {
            'description': loan.name,
            'loan_lines': [
                {
                    'date': line.date,
                    'amount': line.amount,
                    'paid': line.paid,
                }
                for line in loan.loan_lines
            ],
        }

        return request.render("sh_portal_dashboard.loan_detail_template", {'loan_data': loan_data})