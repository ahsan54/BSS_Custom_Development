from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import rgb_to_hex


class SalaryRegisterReport(models.AbstractModel):
    _name = "report.salary_register_report.salary_register_xls_report"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs):

        payslip_ids = objs.slip_ids
        payslip_ids = payslip_ids.sorted(lambda x: x.employee_id.biometric_id)
        print(payslip_ids)
        sheet = workbook.add_worksheet(f"{objs.name}")
        sheet1 = workbook.add_worksheet(f"{objs.name} Banking")
        # # sheet.fit_to_pages(1, )
        # sheet.set_landscape()
        # sheet.set_margins(left=0.25, right=0.25, top=0.5, bottom=0.5)
        # sheet.center_horizontally()
        # sheet.center_vertically()
        # sheet.scroll_panes = (0, 3)  # Scroll horizontally starting from column 1

        bold_format = workbook.add_format({'bold': True})

        main_header_format = workbook.add_format({'bold': True, 'font_size': 16, 'align': 'center',
                                                  'valign': 'vcenter',
                                                  'border': 0
                                                  })

        header_format = workbook.add_format({
            'bold': True,
            # 'font_color': '#FFFFFF',  # White font
            # 'bg_color': '#0000FF',  # Blue background
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,  # Adding border to cells
            'color': 'black',
            'text_wrap': True,
            'bg_color': "#D3D3D3",
        })

        fotter_format = workbook.add_format({
            'bold': True,
            # 'font_color': '#FFFFFF',  # White font
            # 'bg_color': '#0000FF',  # Blue background
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,  # Adding border to cells
            'color': 'black',
            'text_wrap': True,
            'bg_color': "#D3D3D3",
            'num_format': '#,##0.00'
        })

        data_format = workbook.add_format({
            'font_size': 10,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'color': 'purple',
            'text_wrap': True,
            'num_format': '@',
        })
        amount_format = workbook.add_format({
            'font_size': 10,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'color': 'purple',
            'text_wrap': True,
            'num_format': '#,##0.00'
        })

        medium_format = workbook.add_format({
            'font_size': 15, 'align': 'center', 'valign': 'bottom'
        })  # valign , yahi krta ha , ke text ko ider , uder uper nechay krta , center ma rakhte huwe.

        # Set the width of columns A to U to 30 (adjust the value as needed)
        sheet.set_column('A:A', 5)  # 30 is the width, adjust as per your need
        sheet.set_column('B:B', 10)  # 30 is the width, adjust as per your need
        sheet.set_column('C:U', 15)  # 30 is the width, adjust as per your need
        sheet.set_column('V:V', 20)  # 30 is the width, adjust as per your need

        # Set the height of row 0 (first row) to 40 (adjust the value as needed)
        # for rows in range(100):
        #     sheet.set_row(rows, 30 )  # 50 is the height, adjust as per your need

        # we can merge cells by doing like this:-
        sheet.merge_range('A1:V1', 'Business Solutions & Services', main_header_format)
        sheet.merge_range('A3:V3', f'Salary For The Month Of {str(objs.date_start.strftime("%B, %Y")).upper()}',
                          main_header_format)

        sheet.write(3, 0, 'SR#', header_format)
        sheet.write(3, 1, 'Emp No.', header_format)
        sheet.write(3, 2, 'Name', header_format)
        sheet.write(3, 3, 'CNIC #', header_format)
        sheet.write(3, 4, 'Bank A/C #', header_format)
        sheet.write(3, 5, 'EOBI #', header_format)
        sheet.write(3, 6, 'Emp Joining Date #', header_format)
        sheet.write(3, 7, 'Designation', header_format)
        sheet.write(3, 8, 'Gross Salary', header_format)
        sheet.write(3, 9, 'Basic Salary', header_format)
        sheet.write(3, 10, 'Re-Imb', header_format)
        sheet.write(3, 11, 'Total', header_format)
        sheet.write(3, 12, 'Income Tax', header_format)
        sheet.write(3, 13, 'Health Ins.', header_format)
        sheet.write(3, 14, 'EOBI Ded', header_format)
        sheet.write(3, 15, 'Loan', header_format)
        sheet.write(3, 16, 'UnPaid Leaves', header_format)
        sheet.write(3, 17, 'Other Deduction', header_format)
        sheet.write(3, 18, 'Total Deduction', header_format)
        sheet.write(3, 19, f'{str(objs.date_start.strftime("%b-%y")).upper()} Salary MCB', header_format)
        sheet.write(3, 20, 'Previous Salary MCB', header_format)
        sheet.write(3, 21, 'Note', header_format)

        row = 4
        sr_no = 1
        grand_gross = grand_basic = grand_reimbursement = grand_income_tax_ded = grand_health_ded = grand_eobi_ded = grand_loan_ded = grand_unpaid_leaves_ded = grand_other_ded = grand_total_ded = grand_net_salary = 0
        for payslip in payslip_ids:
            sheet.write(row, 0, sr_no, data_format)
            sheet.write(row, 1, payslip.employee_id.biometric_id or '', data_format)
            sheet.write(row, 2, payslip.employee_id.name or 'NONE',
                        data_format)
            sheet.write(row, 3, payslip.employee_id.identification_id or '', data_format)
            sheet.write(row, 4, payslip.employee_id.bank_account_id.acc_number or '', data_format)
            sheet.write(row, 5, payslip.employee_id.eobi or '', data_format)
            sheet.write(row, 6, payslip.contract_id.first_contract_date.strftime('%d/%m/%Y') or '', data_format)
            sheet.write(row, 7, payslip.employee_id.job_title or '', data_format)

            gross_salary = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'GROSS')])
            gross_salary = sum(line.total for line in gross_salary)
            grand_gross += gross_salary
            sheet.write(row, 8, gross_salary or 0, amount_format)

            basic_salary = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'BASIC')])
            basic_salary = sum(line.total for line in basic_salary)
            grand_basic += basic_salary
            sheet.write(row, 9, basic_salary or 0, amount_format)

            reimbursement = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'REIMBURSEMENT')])
            reimbursement = sum(line.total for line in reimbursement)
            grand_reimbursement += reimbursement
            sheet.write(row, 10, reimbursement or 0, amount_format)

            sheet.write(row, 11, 0, amount_format)

            income_tax_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'INTX')])
            income_tax_ded = sum(line.total for line in income_tax_ded)
            grand_income_tax_ded += income_tax_ded
            sheet.write(row, 12, income_tax_ded or 0, amount_format)

            health_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'HLTINS')])
            health_ded = sum(line.total for line in health_ded)
            grand_health_ded += health_ded
            sheet.write(row, 13, health_ded or 0, amount_format)

            eobi_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'EOBI')])
            eobi_ded = sum(line.total for line in eobi_ded)
            grand_eobi_ded += eobi_ded
            sheet.write(row, 14, eobi_ded or 0, amount_format)

            loan_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'LO')])
            loan_ded = sum(line.total for line in loan_ded)
            grand_loan_ded += loan_ded
            sheet.write(row, 15, loan_ded or 0, amount_format)

            unpaid_leaves_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'UNPAID')])
            unpaid_leaves_ded = sum(line.total for line in unpaid_leaves_ded)
            grand_unpaid_leaves_ded += unpaid_leaves_ded
            sheet.write(row, 16, unpaid_leaves_ded or 0, amount_format)

            other_ded = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'DEDUCTION')])
            other_ded = sum(line.total for line in other_ded)
            grand_other_ded += other_ded
            sheet.write(row, 17, other_ded or 0, amount_format)

            total_ded = income_tax_ded + health_ded + eobi_ded + loan_ded + unpaid_leaves_ded + other_ded
            grand_total_ded += total_ded
            sheet.write(row, 18, total_ded or 0, amount_format)

            net_salary = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip.id), ('code', '=', 'NET')])
            net_salary = sum(line.total for line in net_salary)
            grand_net_salary += net_salary

            sheet.write(row, 19, net_salary or 0, amount_format)

            sheet.write(row, 20, 0, amount_format)
            sheet.write(row, 21, payslip.note or "", data_format)
            row += 1
            sr_no += 1
        # Grand Total
        sheet.write(row, 0, '', header_format)
        sheet.write(row, 1, '', header_format)
        sheet.write(row, 2, '', header_format)
        sheet.write(row, 3, '', header_format)
        sheet.write(row, 4, '', header_format)
        sheet.write(row, 5, '', header_format)
        sheet.write(row, 6, '', header_format)
        sheet.write(row, 7, '', header_format)
        sheet.write(row, 8, grand_gross or 0, fotter_format)
        sheet.write(row, 9, grand_basic or 0, fotter_format)
        sheet.write(row, 10, grand_reimbursement or 0, fotter_format)
        sheet.write(row, 11, 0, fotter_format)
        sheet.write(row, 12, grand_income_tax_ded or 0, fotter_format)
        sheet.write(row, 13, grand_health_ded or 0, fotter_format)
        sheet.write(row, 14, grand_eobi_ded or 0, fotter_format)
        sheet.write(row, 15, grand_loan_ded or 0, fotter_format)
        sheet.write(row, 16, grand_unpaid_leaves_ded or 0, fotter_format)
        sheet.write(row, 17, grand_other_ded or 0, fotter_format)
        sheet.write(row, 18, grand_total_ded or 0, fotter_format)
        sheet.write(row, 19, grand_net_salary or 0, fotter_format)
        sheet.write(row, 20, 0, fotter_format)
        sheet.write(row, 21, '', fotter_format)

        # Sheet 01

        # Set the width of columns A to U to 30 (adjust the value as needed)
        sheet1.set_column('A:A', 5)  # 30 is the width, adjust as per your need
        sheet1.set_column('B:B', 10)  # 30 is the width, adjust as per your need
        sheet1.set_column('C:F', 25)  # 30 is the width, adjust as per your need

        # Set the height of row 0 (first row) to 40 (adjust the value as needed)
        # for rows in range(100):
        #     sheet.set_row(rows, 30 )  # 50 is the height, adjust as per your need

        # we can merge cells by doing like this:-
        sheet1.merge_range('A1:F1', 'Business Solutions & Services', main_header_format)
        sheet1.merge_range('A3:F3', f'Salary For The Month Of {str(objs.date_start.strftime("%B, %Y")).upper()}',
                           main_header_format)

        sheet1.write(3, 0, 'SR#', header_format)
        sheet1.write(3, 1, 'Emp No.', header_format)
        sheet1.write(3, 2, 'Name', header_format)
        sheet1.write(3, 3, 'Bank A/C #', header_format)
        sheet1.write(3, 4, f'{str(objs.date_start.strftime("%b-%y")).upper()} Salary MCB', header_format)
        sheet1.write(3, 5, 'Note', header_format)

        row1 = 4
        sr_no1 = 1
        for payslip1 in payslip_ids:
            sheet1.write(row1, 0, sr_no1, data_format)
            sheet1.write(row1, 1, payslip1.employee_id.biometric_id or '', data_format)
            sheet1.write(row1, 2, payslip1.employee_id.name or 'NONE',
                         data_format)
            sheet1.write(row1, 3, payslip1.employee_id.bank_account_id.acc_number or '', data_format)
            net_salary1 = self.env['hr.payslip.line'].search(
                [('slip_id', '=', payslip1.id), ('code', '=', 'NET')])
            net_salary1 = sum(line.total for line in net_salary1)
            sheet1.write(row1, 4, net_salary1 or 0, amount_format)
            sheet1.write(row1, 5, payslip1.note or "", data_format)
            row1 += 1
            sr_no1 += 1
        # Grand Total
        sheet1.write(row1, 0, '', header_format)
        sheet1.write(row1, 1, '', header_format)
        sheet1.write(row1, 2, '', header_format)
        sheet1.write(row1, 3, '', header_format)
        sheet1.write(row1, 4, grand_net_salary or 0, fotter_format)
        sheet1.write(row1, 5, '', fotter_format)
