from odoo import fields, api, models, _


class SalarySlipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def print_xlsx_salary_register(self):
        return self.env.ref("salary_register_report.report_salary_register_xls").report_action(self)
