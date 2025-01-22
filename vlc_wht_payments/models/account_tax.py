

from odoo.exceptions import UserError
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare


class AccountTaxInh(models.Model):
    _inherit = 'account.tax'

    is_wht = fields.Boolean(string='Is Withholding Tax')

