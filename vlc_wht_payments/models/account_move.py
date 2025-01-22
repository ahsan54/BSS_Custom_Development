from odoo.exceptions import UserError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    wht_payment_id = fields.Many2one('account.payment', string='WHT Payment Reference')

