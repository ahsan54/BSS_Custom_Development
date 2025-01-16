from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError


class AccountingCustom(models.Model):
    _inherit = 'account.payment'
    _description = 'Payments'

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit_approval', 'Submitted For Approval'),
            ('approval_one', 'Approval One'),
            ('approval_two', 'Approval Two'),
            ('posted', 'Posted'),
            ('cancel', 'Cancel')
        ],
        default='draft',
        string="State"
    )

    def action_submit_for_approval(self):
        for x in self:
            # x.message_post(subject="Approval Request", body='Please Approve the Payment for further proceed.',
            #                partner_ids=[2], subtype_id=self.env.ref('mail.act').id)
            #---> send payment to clock icon,timeline for a reminder , use this code
            x.activity_schedule(activity_type_id=self.env.ref('mail.mail_activity_data_todo').id, summary="Approval Required..!", user_id = 2, note="Please review and approve this Record", date_deadline=fields.Date.today())
            x.state = 'submit_approval'

    def action_approval_1(self):
        for x in self:
            x.state = 'approval_one'

    def action_approval_2(self):
        for x in self:
            x.state = 'approval_two'

    def action_post(self):
        res = super(AccountingCustom, self).action_post()
        for x in self:
            x.state = 'posted'
        return res

    def action_cancel(self):
        res = super(AccountingCustom, self).action_cancel()
        for x in self:
            x.state = 'cancel'
        return res

    def action_draft(self):
        res = super(AccountingCustom, self).action_draft()
        for x in self:
            x.state = 'draft'
        return res

