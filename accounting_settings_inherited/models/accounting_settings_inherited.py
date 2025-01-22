from odoo import api, _, models, fields, _
import logging

_logger = logging.getLogger(__name__)


class AccountingSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_default_journal = fields.Many2one(
        'account.journal',
        string="Default Payment Journal",
        config_parameter='base.payment_default_journal',
        domain="[('type', 'in', ['bank', 'cash'])]",
        help="Select the default journal for payments."
    )


class AccountPaymentJournal(models.Model):
    _inherit = 'account.payment'

    def default_get(self, fields_list):
        # Fetch default values
        defaults = super(AccountPaymentJournal, self).default_get(fields_list)

        # Get the configured default journal ID from `res.config.settings`
        journal_id = self.env['ir.config_parameter'].sudo().get_param('base.payment_default_journal')

        # Check if the journal ID exists and is valid
        if journal_id and journal_id.isdigit():
            journal = self.env['account.journal'].browse(int(journal_id))
            if journal.exists() and journal.type in ['bank', 'cash']:
                defaults['journal_id'] = journal.id

        return defaults



class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        compute='_compute_journal_id', inverse='_inverse_journal_id', store=True, readonly=False, precompute=True,
        required=True,
        states={'draft': [('readonly', False)]},
        check_company=True,
        domain="[('id', 'in', suitable_journal_ids)]",
        default=lambda self: self._get_default_vendor_bill_journal()
    )

    @api.model
    def _get_default_vendor_bill_journal(self):
        if self.env.context.get('default_move_type') == 'in_invoice':
            vendor_bill_journals = self.env['account.journal'].search([('type', '=', 'purchase')])
            if vendor_bill_journals:
                last_vendor_bill_journal = vendor_bill_journals[-1]
                return last_vendor_bill_journal.id
        return False
