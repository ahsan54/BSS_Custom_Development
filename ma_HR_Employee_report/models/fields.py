from odoo import api, fields, models
from odoo.exceptions import UserError
from bs4 import BeautifulSoup

import datetime

class CustomerModel(models.Model):
    _inherit="hr.employee"
    
    relation = fields.Char(string="Relation")
    blood_group = fields.Char(string="Blood Group")
    
    def onboarding_report(self):
        tasks = []
        act_obboarding = self.env['mail.message'].search([
            ('res_id', '=', self.id),
            ('model', '=', 'hr.employee'),
            ('subtype_id', '=', 2),
            ('body', 'like', "The plan Onboarding has been started")
        ])
        for aonb in act_obboarding:
            soup = BeautifulSoup(aonb.body, 'html.parser')

            # Finding the list
            task_list = soup.find('ul')

            # Extracting tasks
            
            for li in task_list.find_all('li'):
                text = li.text
                parts = text.split(', assigned to ')
                activity = parts[0]
                assigned_part = parts[1].split(', due on the ')
                assigned_to = assigned_part[0]
                due_date = assigned_part[1]
                status='Canceled'
                check_in_activity=self.env['mail.activity'].search([['res_id','=',self.id],['res_model','=','hr.employee'],['summary','=',activity]])
                act_obboarding_done=self.env['mail.message'].search([['res_id','=',self.id],['model','=','hr.employee'],['subtype_id','=',3],['body','like',"done"],['body','like',activity]])

                if check_in_activity:
                    status="To Do"
                elif act_obboarding_done:
                    status="Done"

                # Append the dictionary to the list
                tasks.append({
                    "activity": activity,
                    "assigned_to": assigned_to,
                    "due_date": due_date,
                    "status":status
                })
        
        return tasks
    
    def offboarding_report(self):
        tasks = []
        act_obboarding = self.env['mail.message'].search([
            ('res_id', '=', self.id),
            ('model', '=', 'hr.employee'),
            ('subtype_id', '=', 2),
            ('body', 'like', "The plan Offboarding has been started")
        ])
        for aonb in act_obboarding:
            soup = BeautifulSoup(aonb.body, 'html.parser')

            # Finding the list
            task_list = soup.find('ul')

            # Extracting tasks
            
            for li in task_list.find_all('li'):
                text = li.text
                parts = text.split(', assigned to ')
                activity = parts[0]
                assigned_part = parts[1].split(', due on the ')
                assigned_to = assigned_part[0]
                due_date = assigned_part[1]
                status='Canceled'
                check_in_activity=self.env['mail.activity'].search([['res_id','=',self.id],['res_model','=','hr.employee'],['summary','=',activity]])
                act_obboarding_done=self.env['mail.message'].search([['res_id','=',self.id],['model','=','hr.employee'],['subtype_id','=',3],['body','like',"done"],['body','like',activity]])

                if check_in_activity:
                    status="To Do"
                elif act_obboarding_done:
                    status="Done"

                # Append the dictionary to the list
                tasks.append({
                    "activity": activity,
                    "assigned_to": assigned_to,
                    "due_date": due_date,
                    "status":status
                })
        
        return tasks
    
class HRRecruitmentCandidate(models.Model):
    _inherit="hr.applicant"


    applicant_cnic =  fields.Char(string="CNIC")
    applicant_gender_married_status = fields.Selection([('Mr', 'Mr'), ('Mrs', 'Mrs'),('Miss','Miss')], string="Greating")
    ref_no = fields.Char(string="Employee ID")

    def get_joining_date(self):
        if self.emp_id:
            joining_date = datetime.datetime.strptime(str(self.emp_id.joining_date), '%Y-%m-%d')
            return joining_date.strftime('%d-%B-%Y')
     
    def get_current_month(self):
        return datetime.datetime.today().date()
    
    def get_job_location(self):
        return self.job_id.address_id.city
    def employment_letter(self):
        tasks = []
        act_obboarding = self.env['mail.message'].search([
            ('res_id', '=', self.id),
            ('model', '=', 'hr.employee'),
            ('subtype_id', '=', 2),
            ('body', 'like', "The plan Onboarding has been started")
        ])
        for aonb in act_obboarding:
            soup = BeautifulSoup(aonb.body, 'html.parser')

            # Finding the list
            task_list = soup.find('ul')

            # Extracting tasks
            
            for li in task_list.find_all('li'):
                text = li.text
                parts = text.split(', assigned to ')
                activity = parts[0]
                assigned_part = parts[1].split(', due on the ')
                assigned_to = assigned_part[0]
                due_date = assigned_part[1]
                status='Canceled'
                check_in_activity=self.env['mail.activity'].search([['res_id','=',self.id],['res_model','=','hr.employee'],['summary','=',activity]])
                act_obboarding_done=self.env['mail.message'].search([['res_id','=',self.id],['model','=','hr.employee'],['subtype_id','=',3],['body','like',"done"],['body','like',activity]])

                if check_in_activity:
                    status="To Do"
                elif act_obboarding_done:
                    status="Done"

                # Append the dictionary to the list
                tasks.append({
                    "activity": activity,
                    "assigned_to": assigned_to,
                    "due_date": due_date,
                    "status":status
                })
        
        return tasks
    
    