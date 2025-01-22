# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Company(models.Model):
    _inherit = "res.company"

    sh_portal_dashboard_is_show_sale_chart = fields.Boolean(
        string="Sales Analysis (Sales Chart)?")
    sh_portal_dashboard_is_show_purchase_chart = fields.Boolean(
        string="Purchase Analysis (Purchase Chart)?")
    sh_portal_dashboard_is_show_invoice_chart = fields.Boolean(
        string="Invoice Analysis (Invoice Chart)?")
    sh_portal_dashboard_is_show_bill_chart = fields.Boolean(
        string="Bills Analysis (Bills Chart)?")
    sh_portal_dashboard_is_show_project_task_chart = fields.Boolean(
        string="Is Show Project Task Table?")
    sh_portal_dashboard_is_show_last_quote_table = fields.Boolean(
        string="Is Show Recent Quotation Table?")
    sh_portal_dashboard_is_show_last_sale_order_table = fields.Boolean(
        string="Is Show Recent Sale Order Table?")
    sh_portal_dashboard_is_show_last_rfq_table = fields.Boolean(
        string="Is Show Recent RFQ Table?")
    sh_portal_dashboard_is_show_last_purchase_order_table = fields.Boolean(
        string="Is Show Recent Purchase Order Table?")
    sh_portal_dashboard_is_show_last_invoice_table = fields.Boolean(
        string="Is Show Recent Invoices Table?")
    sh_portal_dashboard_is_show_last_bill_table = fields.Boolean(
        string="Is Show Recent Bill Table?")
    sh_portal_dashboard_is_show_last_inventory_transfer_table = fields.Boolean(
        string="Is Show Recent Inventory Transfer Table?")

    sh_portal_dashboard_is_show_products_table = fields.Boolean(
        string="Is Show Products quantity Table?")

    sh_portal_dashboard_is_show_last_record_limit = fields.Integer(
        string="How Many Recent Records Do You Want To Show?", default=5)

    @api.onchange('sh_portal_dashboard_is_show_last_record_limit')
    def on_change_sh_portal_dashboard_is_show_last_record_limit(self):
        if self.sh_portal_dashboard_is_show_last_record_limit <= 0:
            raise UserError(_('Value must be greater than 0.'))


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_portal_dashboard_is_show_sale_chart = fields.Boolean(string="Sales Analysis (Sales Chart)?",
                                                            related="company_id.sh_portal_dashboard_is_show_sale_chart",
                                                            readonly=False
                                                            )

    sh_portal_dashboard_is_show_purchase_chart = fields.Boolean(string="Purchase Analysis (Purchase Chart)?",
                                                                related="company_id.sh_portal_dashboard_is_show_purchase_chart",
                                                                readonly=False
                                                                )
    sh_portal_dashboard_is_show_invoice_chart = fields.Boolean(string="Invoice Analysis (Invoice Chart)?",
                                                               related="company_id.sh_portal_dashboard_is_show_invoice_chart",
                                                               readonly=False
                                                               )
    sh_portal_dashboard_is_show_bill_chart = fields.Boolean(string="Bills Analysis (Bills Chart)?",
                                                            related="company_id.sh_portal_dashboard_is_show_bill_chart",
                                                            readonly=False
                                                            )

    sh_portal_dashboard_is_show_project_task_chart = fields.Boolean(string="Is Show Project Task Table?",
                                                                    related="company_id.sh_portal_dashboard_is_show_project_task_chart",
                                                                    readonly=False
                                                                    )

    sh_portal_dashboard_is_show_last_quote_table = fields.Boolean(string="Is Show Recent Quotation Table?",
                                                                  related="company_id.sh_portal_dashboard_is_show_last_quote_table",
                                                                  readonly=False
                                                                  )

    sh_portal_dashboard_is_show_last_sale_order_table = fields.Boolean(string="Is Show Recent Sale Order Table?",
                                                                       related="company_id.sh_portal_dashboard_is_show_last_sale_order_table",
                                                                       readonly=False
                                                                       )

    sh_portal_dashboard_is_show_last_rfq_table = fields.Boolean(string="Is Show Recent RFQ Table?",
                                                                related="company_id.sh_portal_dashboard_is_show_last_rfq_table",
                                                                readonly=False
                                                                )

    sh_portal_dashboard_is_show_last_purchase_order_table = fields.Boolean(string="Is Show Recent Purchase Order Table?",
                                                                           related="company_id.sh_portal_dashboard_is_show_last_purchase_order_table",
                                                                           readonly=False
                                                                           )

    sh_portal_dashboard_is_show_last_invoice_table = fields.Boolean(string="Is Show Recent Invoices Table?",
                                                                    related="company_id.sh_portal_dashboard_is_show_last_invoice_table",
                                                                    readonly=False
                                                                    )

    sh_portal_dashboard_is_show_last_bill_table = fields.Boolean(string="Is Show Recent Bill Table?",
                                                                 related="company_id.sh_portal_dashboard_is_show_last_bill_table",
                                                                 readonly=False
                                                                 )
    sh_portal_dashboard_is_show_last_inventory_transfer_table = fields.Boolean(string="Is Show Recent Inventory Transfer Table?",
                                                                 related="company_id.sh_portal_dashboard_is_show_last_inventory_transfer_table",
                                                                 readonly=False
                                                                 )                                                        

                                                              
    sh_portal_dashboard_is_show_products_table = fields.Boolean(string="Is Show Products quantity Table?",
                                                                 related="company_id.sh_portal_dashboard_is_show_products_table",
                                                                 readonly=False
                                                                 )                                                        

    sh_portal_dashboard_is_show_last_record_limit = fields.Integer(string="How Many Recent Records Do You Want To Show?",
                                                                   related="company_id.sh_portal_dashboard_is_show_last_record_limit",
                                                                   readonly=False
                                                                   )

    @api.onchange('sh_portal_dashboard_is_show_last_record_limit')
    def on_change_sh_portal_dashboard_is_show_last_record_limit(self):
        if self.sh_portal_dashboard_is_show_last_record_limit <= 0:
            raise UserError(_('Value must be greater than 0.'))
