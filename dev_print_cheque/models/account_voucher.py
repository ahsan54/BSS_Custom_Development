# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle 
#
##############################################################################
from odoo import models, fields, api,_
from odoo import tools
from num2words import num2words
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    payment_method_name = fields.Char(related='payment_method_line_id.name')
    # cheque_formate_id = fields.Many2one('cheque.setting', 'Cheque Formate')
    # text_free = fields.Char('Free Text')
    partner_text = fields.Char('Partner Title')
    is_ac_pay = fields.Boolean('Is A/C Pay')
    custom_partner_title = fields.Boolean('Custom Partner Title')
    journal_type = fields.Selection(
        related='journal_id.type',
        string='Journal Type',
        store=True
    )

    _sql_constraints = [
        ('unique_name', 'UNIQUE(cheque_no)', 'The "Cheque No" must be unique.'),
    ]

    def get_date(self, date):
        date = str(date).split('-')
        return date

    def get_partner_name(self, obj, p_text):
        if p_text and obj.partner_text:
            if p_text == 'prefix':
                return obj.partner_text + ' ' + obj.partner_id.name
            else:
                return obj.partner_id.name + ' ' + obj.partner_text

        return obj.partner_id.name

    def amount_word(self, obj):
        amt_word = num2words(obj.amount)
        return amt_word



    cheque_no = fields.Char(
        string='Cheque No',
        store=True
    )

    def _check_unique_cheque_no(self, cheque_no):
        existing_record = self.search([('cheque_no', '=', cheque_no)], limit=1)
        if existing_record and existing_record.cheque_no != '':
            raise ValidationError(f"The cheque number '{cheque_no}' is already used. Please use a unique number.")

    @api.model
    def create(self, vals):
        if 'cheque_no' in vals and vals['cheque_no']:
            self._check_unique_cheque_no(vals['cheque_no'])
        return super(AccountPayment, self).create(vals)

    def write(self, vals):
        if 'cheque_no' in vals and vals['cheque_no']:
            self._check_unique_cheque_no(vals['cheque_no'])
        return super(AccountPayment, self).write(vals)


    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        for rec in self:
            if rec.journal_id.type == 'bank':
                if rec.journal_id.type == 'bank' and rec.journal_id.bank_category == 'mcb':
                    last_payment_mcb = self.env['account.payment'].search(
                        [('journal_id.type', '=', 'bank'), ('journal_id.bank_category', '=', 'mcb')],
                        order='id desc', limit=1)
                    if last_payment_mcb and last_payment_mcb.cheque_no.isdigit():
                        rec.cheque_no = str(int(last_payment_mcb.cheque_no) + 1).zfill(10)
                    else:
                        rec.cheque_no = '0000000001'
                elif rec.journal_id.type == 'bank' and rec.journal_id.bank_category == 'meezan':
                    last_payment_meezan = self.env['account.payment'].search(
                        [('journal_id.type', '=', 'bank'), ('journal_id.bank_category', '=', 'meezan')],
                        order='id desc', limit=1)
                    if last_payment_meezan and last_payment_meezan.cheque_no.isdigit():
                        rec.cheque_no = str(int(last_payment_meezan.cheque_no) + 1).zfill(10)
                    else:
                        rec.cheque_no = '0000000001'
            else:
                rec.cheque_no = ''




    # Sequence by Onchnage  : Bss Team Development : Ahsan
    # This Picks Tha Last Latest Id and uses its cheque number by incrementing 1 in it , Due to OnChnage: sequence shows up without saving record.

    # cheque_no = fields.Char(
    #     string='Cheque No',
    #     required=False,
    #     store=True,
    # )
    #
    # @api.onchange('journal_id')
    # def Onchange_journal_id(self):
    #     for x in self:
    #         if x.journal_id.type == 'bank':
    #             if x.journal_id.bank_category == 'mcb':
    #                 last_cheque_no_mcb = self.env['account.payment'].search(
    #                     [('journal_id.type', '=', 'bank'), ('journal_id.bank_category', '=', 'mcb')],
    #                     order='id desc', limit=1
    #                 )
    #                 if last_cheque_no_mcb and last_cheque_no_mcb.cheque_no.isdigit():
    #                     x.cheque_no = str(int(last_cheque_no_mcb.cheque_no) + 1).zfill(10)
    #
    #             elif x.journal_id.bank_category == 'meezan':
    #                 last_cheque_no_meezan = self.env['account.payment'].search(
    #                     [('journal_id.type', '=', 'bank'), ('journal_id.bank_category', '=', 'meezan')],
    #                     order='id desc', limit=1
    #                 )
    #                 if last_cheque_no_meezan and last_cheque_no_meezan.cheque_no.isdigit():
    #                     x.cheque_no = str(int(last_cheque_no_meezan.cheque_no) + 1).zfill(10)



#########------------------------ Caution -----------------------------------------------------------------------------#











#-----------> This Updates the sequence with manual number and genrates next sequence on different banks.
# ----------> Runs : On Saving Record : Bss Team Old Development...

    # cheque_no = fields.Char(
    #     string='Cheque No',
    #     default=lambda self: self._default_cheque_no(),
    #     required=True
    # )
    #
    # def _default_cheque_no(self):
    #     """Get the next sequence number to pre-fill the cheque number field based on journal's bank category."""
    #     journal = self.journal_id
    #     if journal.type == 'bank':
    #         if journal.bank_category == 'mcb':
    #             return self.env['ir.sequence'].next_by_code('tijaarat.voucher.cheque') or _('New')
    #         elif journal.bank_category == 'meezan':
    #             return self.env['ir.sequence'].next_by_code('meezan.bank.sequence') or _('New')
    #     return _('New')
    #
    #
    # def _update_sequence_based_on_manual_check_number(self, manual_check_no):
    #     """Update the sequence based on the manually entered cheque number."""
    #     try:
    #         manual_check_no_int = int(manual_check_no)
    #         journal = self.journal_id
    #         sequence_code = None
    #
    #         if journal.type == 'bank':
    #             if journal.bank_category == 'mcb':
    #                 sequence_code = 'tijaarat.voucher.cheque'
    #             elif journal.bank_category == 'meezan':
    #                 sequence_code = 'meezan.bank.sequence'
    #
    #         if sequence_code:
    #             sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
    #             if sequence:
    #                 # Update the sequence to start from the manually entered check number
    #                 sequence.sudo().write({'number_next': manual_check_no_int + 1})
    #     except ValueError:
    #         # Raise a user-friendly error if the input is not numeric
    #         raise ValidationError(_("The manual cheque number must be an integer."))
    #
    # @api.model
    # def create(self, vals):
    #     # Pre-fill cheque_no with the next sequence number if not provided
    #     if vals.get('cheque_no', _('New')) == _('New'):
    #         journal = self.env['account.journal'].browse(vals.get('journal_id'))
    #         if journal.type == 'bank':
    #             if journal.bank_category == 'mcb':
    #                 vals['cheque_no'] = self.env['ir.sequence'].next_by_code('tijaarat.voucher.cheque') or _('New')
    #             elif journal.bank_category == 'meezan':
    #                 vals['cheque_no'] = self.env['ir.sequence'].next_by_code('meezan.bank.sequence') or _('New')
    #     else:
    #         # Update the sequence if a manual cheque number is provided
    #         self._update_sequence_based_on_manual_check_number(vals['cheque_no'])
    #     return super().create(vals)
    #
    # def write(self, vals):
    #     res = super().write(vals)
    #     if 'cheque_no' in vals:
    #         self._update_sequence_based_on_manual_check_number(vals['cheque_no'])
    #     return res










class AccountJournal_Bank_Category(models.Model):
    _inherit = 'account.journal'

    bank_category = fields.Selection([ ('mcb', 'MCB'),('meezan', 'Meezan'),('alfalah', 'Alfalah'),('mashreq', 'Mashreq'),],default=None)


















