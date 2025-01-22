# Dev_Print_Cheque
Migrated The Module To Odoo 16 by adding attrs in invisible , required attributes then implemented the custom functionality.
#### Added Dynamic Cheque Numbering and Bank-Specific Logic
Introduced the journal_type field, related to journal_id.type, to dynamically toggle the visibility of the is_a/c_pay, custom_partner_title, and cheque_no fields. These fields are only visible when the journal type is set to "bank".
##### Implemented two separate sequences for generating cheque numbers:
###### Meezan Bank Sequence: 
Automatically generates cheque numbers for journals categorized under "Meezan" in the bank_category field.
###### MCB Bank Sequence: 
Similarly, generates cheque numbers for journals categorized under "MCB".
Cheque numbers are dynamically generated based on the selected bank's sequence. The sequence only propagates when the record is saved, ensuring consistency.

Users can manually update the cheque number. The sequence dynamically adjusts to reflect the next number based on the manually entered value. For example, if the current cheque number is 00003 and the user updates it to 00007, the next cheque number will automatically generate as 00008.
Ensured that the Meezan and MCB sequences operate independently of each other, preventing any interference between the two categories.












# Accounting_Customization
Removed the working of approvals related to amount ranges and developed this module to handle approvals section.

Extended the account.payment model to include a custom approval workflow with new states: submit_approval, approval_one, approval_two, posted, and cancel.
Overrided  state field to manage payment approvals at different stages.

#### Implemented the following methods:
##### action_submit_for_approval: Moves the payment to the "Submitted for Approval" state and schedules an activity for a specific user with a deadline and approval reminder.

##### action_approval_1 and action_approval_2: Transition payments to their respective approval levels.

##### Overrode action_post, action_cancel, and action_draft methods to update the custom state field while maintaining core functionality.

Enhanced the approval process by integrating scheduled activities and user notifications to ensure timely action on payments.



# Account_Settings_Inherited
#### Added Default Journal Configuration for Payments and Vendor Bills
Developed the module from scratch to enhance default journal behavior in the Accounting module.

Added a new payment_default_journal field (Many2one) in res.config.settings.

The field allows users to configure a default journal for payments with a domain restricted to journals of type bank and cash.
This configuration is stored as a parameter and can be dynamically accessed.
Overridden default_get in account.payment:

##### Implemented logic to fetch the configured default journal (payment_default_journal) from settings and pre-fill it in the Journal field of payments.
Ensured the default behavior is preserved for scenarios where no default journal is configured or the selected journal becomes invalid.
Modified Journal Behavior in Vendor Bills (account.move):

##### Overridden the journal_id field in the account.move model to:
Compute a default journal specific to vendor bills (move_type = in_invoice) based on journals of type purchase.
Display the last created purchase journal for vendor bills, while retaining default behavior for other move types and pages.
This module provides flexibility by allowing admins to define a default payment journal while ensuring seamless functionality across different accounting workflows.


# Sh_Portal_DashBoard
#### Enhanced Leave Request Portal: 
Added functionality for employees to request full-day or half-day leaves through the portal. Validates allocated leave types, handles unpaid leaves, and calculates leave durations dynamically.

#### Payslip Portal: 
Implemented a feature to display the latest three payslips for the logged-in employee with details, ensuring a user-friendly payslip overview.

#### Tax Certificate Request: 
Developed tax certificate request flow, allowing employees to request tax certificates directly from their payslips. This updates the payslip record and generates an approval request to account office user for further processing.
#### Loan Details View: 
Designed a detailed loan view for employees to track their loan payment schedules and statuses, ensuring transparency and accessibility.

#### Validation and Security: 
Incorporated proper validation, error handling, and security measures for user-related operations across the portal features.


# Gd_Custom_Reports 
Dynamic Payment and Receipt Voucher Report
##### Developed a dynamic voucher report in Odoo, adapting titles and content based on journal type and payment direction:

Cash Payment/Receipt Vouchers for cash transactions.

Bank Payment/Receipt Vouchers for bank transactions.

Payment Voucher, Journal Entries Report. 

Bss Customer Invoice $ 


#### Key Enhancements:
Dynamically displays partner names, voucher numbers, and dates.

Adjusts fields like Cheque No for specific cases (e.g., inbound bank payments).

Built a detailed account lines table with account details, cost center, and calculated totals.

Added amount in words conversion using a backend utility for multilingual support.

Includes formatted remarks and approval signatures.

Backend extensions include get_amount_in_words() for text conversion, dynamic report titles via print_report_name, and analytic distribution formatting for clear account allocations. This ensures clarity and flexibility across diverse payment scenarios.

Developed BSS_$_Invoice report  for customer invoices, featuring detailed  dynamic calculations for discounted prices, total amounts, and currency conversions (USD to PKR). 








# Salary_Register_Excel_Report
Developed a dynamic Salary Register Report, which generates a comprehensive salary register in an Excel format, with a detailed breakdown for employees.

Employee Information: Displays employee ID, name, CNIC, bank account, and joining date.

Salary Breakdown: Lists gross salary, basic salary, reimbursements, deductions (income tax, health, EOBI, loans, unpaid leaves), total deductions, and net salary.

Grand Totals: Includes grand totals for all categories at the end of the report for easy summary.

Banking Information: Includes a separate sheet showing net salary and bank account numbers for payment processing.






# Ma_HR-Employee_Pdf_Reports

Developed the internship_offer_letter report , employee_offer_letter report , non_discloure report , employee_off_boarding report.


# Vlc_Wht_Payments : WithHolding Tax

Migrated the V17 module to V16.
This module enhances the payment process by integrating Withholding Tax. It allows automatic calculation of WHT on payments, creates corresponding journal entries for vendor and customer transactions, and supports configuring WHT in  settings of accounts.











