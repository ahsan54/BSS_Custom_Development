# Dev Print Cheque
Migrated The Module To Odoo 16 by adding attrs in invisible , required attributes then implemented the custom functionality.
#### Added Dynamic Cheque Numbering and Bank-Specific Logic
Introduced the journal_type field, related to journal_id.type, to dynamically toggle the visibility of the is_a/c_pay, custom_partner_title, and cheque_no fields. These fields are only visible when the journal type is set to "bank".
###### Implemented two separate sequences for generating cheque numbers:
Meezan Bank Sequence: Automatically generates cheque numbers for journals categorized under "Meezan" in the bank_category field.
MCB Bank Sequence: Similarly, generates cheque numbers for journals categorized under "MCB".
Cheque numbers are dynamically generated based on the selected bank's sequence. The sequence only propagates when the record is saved, ensuring consistency.
Users can manually update the cheque number. The sequence dynamically adjusts to reflect the next number based on the manually entered value. For example, if the current cheque number is 00003 and the user updates it to 00007, the next cheque number will automatically generate as 00008.
Ensured that the Meezan and MCB sequences operate independently of each other, preventing any interference between the two categories.












# Accounting Customization
Removed the working of approvals related to amount ranges and developed this module to handle approvals section.
Extended the account.payment model to include a custom approval workflow with new states: submit_approval, approval_one, approval_two, posted, and cancel.
Overrided  state field to manage payment approvals at different stages.
Implemented the following methods:
action_submit_for_approval: Moves the payment to the "Submitted for Approval" state and schedules an activity for a specific user with a deadline and approval reminder.
action_approval_1 and action_approval_2: Transition payments to their respective approval levels.
Overrode action_post, action_cancel, and action_draft methods to update the custom state field while maintaining core functionality.
Enhanced the approval process by integrating scheduled activities and user notifications to ensure timely action on payments.




















# Gd Custom Reports 

# Salary Register Excel Report

# Ma_HR-Employee Pdf Reports

# Sh_Portal_DashBoard
Enhanced Leave Request Portal: Added functionality for employees to request full-day or half-day leaves through the portal. Validates allocated leave types, handles unpaid leaves, and calculates leave durations dynamically.
Payslip Portal: Implemented a feature to display the latest three payslips for the logged-in employee with details, ensuring a user-friendly payslip overview.
Tax Certificate Request: Developed tax certificate request flow, allowing employees to request tax certificates directly from their payslips. This updates the payslip record and generates an approval request to account office user for further processing.
Loan Details View: Designed a detailed loan view for employees to track their loan payment schedules and statuses, ensuring transparency and accessibility.
Validation and Security: Incorporated proper validation, error handling, and security measures for user-related operations across the portal features.
