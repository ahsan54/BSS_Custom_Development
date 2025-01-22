from odoo import models, fields, api, _

class Request_Salary_Slip(models.Model):
    _inherit = 'hr.payslip'

    is_request_salary_slip = fields.Boolean(string="Request Salary Slip", default=False)
    is_approved = fields.Boolean(string="Approved", default=False)
    # status_request_slip = fields.Selection([('Pending', 'Pending'), ('Approved', 'Approved')],default='None', string="Status")
    # def action_approve(self):
    #     self.is_approved = True
    #     self.status_request_slip = 'Approved'
#         self.is_request_salary_slip = False

class Loan_Advance_Request(models.Model):
    _inherit = 'hr.loan'

    req_type = fields.Selection([('loan', 'Loan'), ('advance', 'Advance')], string="Request Type")


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_id = fields.Char(string="Employee ID")

class Expense(models.Model):
    _inherit = 'hr.expense'

    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')

class TaxCertificateRequest(models.Model):
    _inherit = 'hr.payslip'

    req_tax_certificate = fields.Boolean(string="Request Tax Certificate", default=False)