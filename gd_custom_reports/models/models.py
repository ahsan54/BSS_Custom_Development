# -*- coding: utf-8 -*-

from odoo import models, fields, api
import num2words


class AccountMove(models.Model):
    _inherit = 'account.move'

    exchange_rate_usd_to_pkr = fields.Float(
        string="Exchange Rate",
        compute="_compute_exchange_rate",
        store=True,
        digits=(10, 6),
        help="Displays the exchange rate based on the selected currency."
    )

    @api.depends('currency_id', 'date')
    def _compute_exchange_rate(self):
        usd_currency = self.env.ref('base.USD')
        for move in self:
            if move.currency_id == usd_currency:
                usd_rate_line = usd_currency.rate_ids.filtered(lambda r: r.name <= move.date).sorted('name',
                                                                                                     reverse=True)[:1]
                if usd_rate_line:
                    if move.currency_id == usd_currency:
                        move.exchange_rate_usd_to_pkr = usd_rate_line.inverse_company_rate
                else:
                    move.exchange_rate_usd_to_pkr = 1.0
            else:
                move.exchange_rate_usd_to_pkr = 1.0

    def num2words_function(self, amount):
        return num2words.num2words(amount).capitalize()

    def get_amount_in_words(self, amount):
        for rec in self:
            # Handle the case where amount is None
            if amount is None:
                amount = 0.0
            text = rec.currency_id.amount_to_text(amount)
            return text.title()




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @property
    def print_report_name(self):
        for rec in self:
            if rec.journal_id.type == 'cash' and rec.payment_type == 'outbound':
                return 'Cash Payment Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'bank' and rec.payment_type == 'outbound':
                return 'Bank Payment Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'cash' and rec.payment_type == 'inbound':
                return 'Cash Receipt Voucher - %s' % (rec.name)
            elif rec.journal_id.type == 'bank' and rec.payment_type == 'inbound':
                return 'Bank Receipt Voucher - %s' % (rec.name)
            return 'Voucher - %s' % (rec.name)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def compute_analytic_distribution_formatted(self):
        if self.analytic_distribution:
            distribution = []
            for key, value in self.analytic_distribution.items():
                plan = self.env['account.analytic.account'].browse(int(key))
                if plan:
                    distribution.append(f"{plan.name}:{value}%")
            return distribution
        else:
            return ""
