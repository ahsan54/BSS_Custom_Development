# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from datetime import date
from odoo import api, fields, models, _


class ResCompanyInh(models.Model):
    _inherit = "res.company"

    wht_journal_id = fields.Many2one(comodel_name='account.journal', string='Withholding Journal')


class ConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    wht_journal_id = fields.Many2one(comodel_name='account.journal',
                                     config_parameter='vlc_wht_payments.wht_journal_id',
                                     readonly=False, string="Withholding Journal")

