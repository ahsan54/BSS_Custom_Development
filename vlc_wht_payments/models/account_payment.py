from odoo.exceptions import UserError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    is_wht = fields.Boolean(string='Is Withholding Tax', tracking=True)

    tax_id = fields.Many2one(comodel_name='account.tax', string='Withholding Tax', tracking=True,
                             domain=[('is_wht', '=', True)])
    tax_ids = fields.Many2many('account.tax', compute='_compute_tax_ids')
    tax_account_id = fields.Many2one(comodel_name='account.account', string='Withholding Tax Account',
                                     compute='compute_tax_account', tracking=True)
    tax_rate = fields.Float(string='Withholding Tax Rate', related='tax_id.amount', tracking=True)

    amount_outstanding = fields.Float(string='Amount Paid', tracking=True)
    tax_amount = fields.Float(string='Withholding Tax Amount', tracking=True, compute='_compute_tax_amount')

    new_amount = fields.Float(string='New Amount', compute='_compute_new_amount')

    wht_move_id = fields.Many2one(comodel_name='account.move', string='Withholding Tax Entry',
                                  compute='compute_wht_move_id', tracking=True)
    wht_journal_id = fields.Many2one(comodel_name='account.journal',
                                     readonly=False, string="Withholding Journal")

    @api.depends('tax_id')
    def _compute_tax_ids(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                rec.tax_ids = self.env['account.tax'].search([('is_wht', '=', True), ('type_tax_use', '=', 'purchase')]).ids
            elif rec.payment_type == 'inbound':
                rec.tax_ids = self.env['account.tax'].search([('is_wht', '=', True), ('type_tax_use', '=', 'sale')]).ids
            else:
                rec.tax_ids = None

    def compute_wht_move_id(self):
        for rec in self:
            wht_move = self.env['account.move'].search([('wht_payment_id', '=', rec.id)])
            rec.wht_move_id = wht_move.id

    @api.depends('tax_id')
    def compute_tax_account(self):
        for record in self:
            if record.tax_id:
                for rec in record.tax_id.invoice_repartition_line_ids:
                    if rec.account_id:
                        record.tax_account_id = rec.account_id.id
            else:
                record.tax_account_id = False

    @api.depends('amount_outstanding', 'tax_id')
    def _compute_tax_amount(self):
        total = 0
        for record in self:
            if record.amount_outstanding and record.tax_id:
                total = (record.tax_rate / 100) * record.amount_outstanding
                record.tax_amount = total
            else:
                record.tax_amount = 0

    @api.depends('amount_outstanding', 'tax_id')
    def _compute_new_amount(self):
        total = 0
        for record in self:
            if record.amount_outstanding and record.tax_id:
                total = (record.amount_outstanding - record.tax_amount)
                record.new_amount = total
                record.amount = total
            else:
                record.new_amount = 0

    @api.onchange('payment_type')
    def change_payment_type(self):
        if self.payment_type == 'inbound':
            self.is_wht = False

    @api.onchange('is_wht')
    def change_is_wht(self):
        if self.is_wht == False:
            self.tax_id = False
            self.amount_outstanding = 0
            self.amount = 0

    # @api.model
    # def create(self, vals):
    #     record = super(AccountPaymentInh, self).create(vals)
    #     if record.is_wht:
    #         if record.payment_type == 'outbound':
    #             record.create_vendor_entry()
    #         elif record.payment_type == 'inbound':
    #             record.create_customer_entry()
    #     return record
    def action_post(self):
        res = super().action_post()
        for record in self:
            if record.is_wht:
                if record.payment_type == 'outbound':
                    record.create_vendor_entry()
                elif record.payment_type == 'inbound':
                    record.create_customer_entry()
        return res

    def action_cancel(self):
        if self.is_wht:
            if self.payment_type == 'outbound' and self.wht_move_id:
                self.wht_move_id.button_cancel()
        res = super(AccountPaymentInh, self).action_cancel()
        return res

    def create_vendor_entry(self):
        # config = self.env['ir.config_parameter'].sudo()
        # wht_journal_id = int(config.get_param('vlc_wht_payments.wht_journal_id'))
        # if not wht_journal_id:
        #     raise UserError(_('Please Select Withholding Journal In Account Settings'))
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        move_dict = {
            'ref': 'Withheld Tax',
            'journal_id': self.journal_id.id,
            'wht_payment_id': self.id,
            'date': self.date,
        }
        debit_line = (0, 0, {
            'name': 'Withheld Tax',
            'debit': abs(self.tax_amount),
            'credit': 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.partner_id.property_account_payable_id.id,
            'analytic_distribution': self.analytic_distribution,
        })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
        credit_line = (0, 0, {
            'name': f'{self.name}-Withheld Tax',
            'debit': 0.0,
            'credit': abs(self.tax_amount),
            'partner_id': self.partner_id.id,
            'account_id': self.tax_account_id.id,
            'analytic_distribution': self.analytic_distribution,
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.action_post()

    def create_customer_entry(self):
        # config = self.env['ir.config_parameter'].sudo()
        # wht_journal_id = int(config.get_param('vlc_wht_payments.wht_journal_id'))
        # if not wht_journal_id:
        #     raise UserError(_('Please Select Withholding Journal In Account Settings'))
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        move_dict = {
            'ref': f'{self.name}-Withheld Tax',
            'journal_id': self.journal_id.id,
            'wht_payment_id': self.id,
            'date': self.date,
        }
        debit_line = (0, 0, {
            'name': 'Withheld Tax',
            'debit': 0.0,
            'credit': abs(self.tax_amount),
            'partner_id': self.partner_id.id,
            'account_id': self.partner_id.property_account_receivable_id.id,
            'analytic_distribution': self.analytic_distribution,
        })
        line_ids.append(debit_line)
        debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
        credit_line = (0, 0, {
            'name': 'Withheld Tax',
            'debit': abs(self.tax_amount),
            'credit': 0.0,
            'partner_id': self.partner_id.id,
            'account_id': self.tax_account_id.id,
            'analytic_distribution': self.analytic_distribution,
        })
        line_ids.append(credit_line)
        credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        move.action_post()


class AccountRegisterPayment(models.TransientModel):
    _name = "account.payment.register"
    _inherit = ["account.payment.register", "analytic.mixin"]

    is_wht = fields.Boolean(string='Is Withholding Tax', tracking=True)

    tax_id = fields.Many2one(comodel_name='account.tax', string='Withholding Tax', tracking=True,
                             domain=[('is_wht', '=', True)])
    tax_ids = fields.Many2many('account.tax', compute='_compute_tax_ids')
    tax_account_id = fields.Many2one(comodel_name='account.account', string='Withholding Tax Account',
                                     compute='compute_tax_account', tracking=True)
    tax_rate = fields.Float(string='Withholding Tax Rate', related='tax_id.amount', tracking=True)

    amount_outstanding = fields.Float(string='Amount Paid', tracking=True)
    tax_amount = fields.Float(string='Withholding Tax Amount', tracking=True, compute='_compute_tax_amount')

    new_amount = fields.Float(string='New Amount', compute='_compute_new_amount')
    wht_journal_id = fields.Many2one(comodel_name='account.journal',
                                     readonly=False, string="Withholding Journal")

    @api.depends('tax_id')
    def _compute_tax_ids(self):
        for rec in self:
            if rec.payment_type == 'outbound':
                rec.tax_ids = self.env['account.tax'].search([('is_wht', '=', True), ('type_tax_use', '=', 'purchase')]).ids
            elif rec.payment_type == 'inbound':
                rec.tax_ids = self.env['account.tax'].search([('is_wht', '=', True), ('type_tax_use', '=', 'sale')]).ids
            else:
                rec.tax_ids = None

    def compute_wht_move_id(self):
        for rec in self:
            wht_move = self.env['account.move'].search([('wht_payment_id', '=', rec.id)])
            rec.wht_move_id = wht_move.id

    @api.depends('tax_id')
    def compute_tax_account(self):
        for record in self:
            if record.tax_id:
                for rec in record.tax_id.invoice_repartition_line_ids:
                    if rec.account_id:
                        record.tax_account_id = rec.account_id.id
            else:
                record.tax_account_id = False


    @api.depends('amount_outstanding', 'tax_id')
    def _compute_tax_amount(self):
        total = 0
        for record in self:
            if record.amount_outstanding and record.tax_id:
                total = (record.tax_rate / 100) * record.amount_outstanding
                record.tax_amount = total
            else:
                record.tax_amount = 0

    @api.depends('amount_outstanding', 'tax_id')
    def _compute_new_amount(self):
        total = 0
        active_id = self.env['account.move'].browse(self._context.get('active_id'))
        for record in self:
            if record.amount_outstanding and record.tax_id and record.is_wht:
                total = (record.amount_outstanding - record.tax_amount)
                record.new_amount = total
                record.amount = total
            else:
                record.new_amount = 0

    @api.onchange('payment_type')
    def change_payment_type(self):
        if self.payment_type == 'inbound':
            self.is_wht = False

    @api.onchange('is_wht')
    def change_is_wht(self):
        if self.is_wht == False:
            self.tax_id = False
            self.amount_outstanding = 0
            # self.amount = 0

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['is_wht'] = self.is_wht
        res['tax_id'] = self.tax_id.id
        res['tax_account_id'] = self.tax_account_id.id
        res['amount_outstanding'] = self.amount_outstanding
        res['tax_amount'] = self.tax_amount
        res['new_amount'] = self.new_amount
        # res['wht_journal_id'] = self.wht_journal_id.id
        return res
