import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, time

class ApprovalCategoryCustom(models.Model):
	_inherit        = "approval.category"
	_description    = "Approval Model"

	type_id            = fields.Selection([('default','Default'),('contract','Contract')],string = 'Approval Type')
	

class ApprovalRequestCustom(models.Model):
	_inherit        = "approval.request"
	_description    = "Approval Request"
	
	type_id            = fields.Selection([('default','Default'),('contract','Contract')],string = 'Approval Type', related='category_id.type_id')
	
	# untuk perubahan kontrak
	contract_employee_id             	= fields.Many2one('hr.employee', string='Pegawai', Required = False)
	contract_date						= fields.Date(string='Tanggal Perubahan', Required = False)
	contract_contract_id     			= fields.Many2one('hr.contract', string='Contract', Required = False)
	currency_id 						= fields.Many2one(string="Currency", related='contract_contract_id.company_id.currency_id', readonly=True)

	# current
	contract_department_id  			= fields.Many2one('hr.department', string='Departement', Required = False)
	contract_start_date					= fields.Date(string='Contract Start Date', Required = False)
	contract_end_date					= fields.Date(string='Contract End Date')
	contract_struct_id     				= fields.Many2one('hr.payroll.structure', string='Salary Struktur', Required = False)
	contract_contract_type  			= fields.Many2one('hr.contract.type', string='Contract Type', Required = False)
	contract_salary_structure_type  	= fields.Many2one('hr.payroll.structure.type', string='Salary Struktur Type', Required = False)
	contract_calendar_id  				= fields.Many2one('resource.calendar', string='Working Schedule', Required = False)
	contract_responsible_id  			= fields.Many2one('res.users', string='HR Responsible', Required = False)
	contract_job_id  					= fields.Many2one('hr.job', string='Job Position', Required = False)

	contract_wage 						= fields.Monetary(string='Wage', default= 0.00)
	contract_da_allowance 				= fields.Monetary(string='Dearing Allowance', default= 0.00)
	contract_acting_allowance 			= fields.Monetary(string='Acting Allowance', default= 0.00)
	contract_competency_allowance 		= fields.Monetary(string='Competency Allowance', default= 0.00)
	contract_location_allowance 		= fields.Monetary(string='Location Allowance', default= 0.00)
	contract_position_allowance 		= fields.Monetary(string='Position Allowance', default= 0.00)
	contract_daily_allowance 			= fields.Monetary(string='Daily Allowance', default= 0.00)
	contract_handphone_allowance     	= fields.Monetary(string='Handphone Allowance', default= 0.00)
	contract_performance_allowance   	= fields.Monetary(string='Performance Allowance', default= 0.00)
	contract_travel_allowance   		= fields.Monetary(string='Travel Allowance', default= 0.00)
	contract_meal_allowance   			= fields.Monetary(string='Meal Allowance', default= 0.00)
	contract_medical_allowance   		= fields.Monetary(string='Medical Allowance', default= 0.00)
	contract_housing_allowance   		= fields.Monetary(string='Housing Allowance', default= 0.00)
	contract_other_allowance   			= fields.Monetary(string='Other Allowance', default= 0.00)

	#before
	contract_department_id_before  				= fields.Many2one('hr.department', string='Departement Before', Required = False)
	contract_start_date_before					= fields.Date(string='Contract Start Date Before', Required = False)
	contract_end_date_before					= fields.Date(string='Contract End Date Before')
	contract_struct_id_before     				= fields.Many2one('hr.payroll.structure', string='Salary Struktur Before', Required = False)
	contract_contract_type_before  				= fields.Many2one('hr.contract.type', string='Contract Type Before', Required = False)
	contract_salary_structure_type_before  		= fields.Many2one('hr.payroll.structure.type', string='Salary Struktur Type Before', Required = False)
	contract_calendar_id_before  				= fields.Many2one('resource.calendar', string='Working Schedule Before', Required = False)
	contract_responsible_id_before  			= fields.Many2one('res.users', string='HR Responsible Before', Required = False)
	contract_job_id_before  					= fields.Many2one('hr.job', string='Job Position Before', Required = False)

	contract_wage_before 						= fields.Monetary(string='Wage Before', default= 0.00)
	contract_da_allowance_before 				= fields.Monetary(string='Dearing Allowance Before', default= 0.00)
	contract_acting_allowance_before 			= fields.Monetary(string='Acting Allowance Before', default= 0.00)
	contract_competency_allowance_before 		= fields.Monetary(string='Competency Allowance Before', default= 0.00)
	contract_location_allowance_before 			= fields.Monetary(string='Location Allowance Before', default= 0.00)
	contract_position_allowance_before 			= fields.Monetary(string='Position Allowance Before', default= 0.00)
	contract_daily_allowance_before 			= fields.Monetary(string='Daily Allowance Before', default= 0.00)
	contract_handphone_allowance_before     	= fields.Monetary(string='Handphone Allowance Before', default= 0.00)
	contract_performance_allowance_before   	= fields.Monetary(string='Performance Allowance Before', default= 0.00)
	contract_travel_allowance_before   		= fields.Monetary(string='Travel Allowance Before', default= 0.00)
	contract_meal_allowance_before   		= fields.Monetary(string='Meal Allowance Before', default= 0.00)
	contract_medical_allowance_before   		= fields.Monetary(string='Medical Allowance Before', default= 0.00)
	contract_housing_allowance_before   		= fields.Monetary(string='Housing Allowance Before', default= 0.00)
	contract_other_allowance_before   		= fields.Monetary(string='Other Allowance Before', default= 0.00)

	contract_state							= fields.Selection([('submit','Submitted'),('approve','Approved'),('reject','Rejected')])
	contract_reviewed_by  					= fields.Many2one('res.users', string='Reviewed By', Required = False)
	contract_description						= fields.Text(string='Description')
	contract_description_request				= fields.Text(string='Request Description')

	mpr_ump_wilayah_id = fields.Many2one("hr.payroll.regional.setting", string="UMP / UMK Wilayah")
	mpr_ump_wilayah_nilai = fields.Monetary(string="UMP / UMK (Rp.)")

	@api.onchange('mpr_ump_wilayah_id')
	def _onchange_mpr_ump(self):
		if self.mpr_ump_wilayah_id and self.mpr_tanggal_pemenuhan:
			ump_value_id =self.env['hr.payroll.regional.setting.value'].search([('name', '=', self.mpr_ump_wilayah_id.id), ('state', '=', 'active')], limit=1)
			self.mpr_ump_wilayah_nilai = ump_value_id.value if ump_value_id else False
		else:
			self.mpr_ump_wilayah_nilai = False
	
	mpr_job_status_domain = fields.Many2many("master.job.status", store=True)
	mpr_job_status_id = fields.Many2one("master.job.status", string="Job Status", domain="[('id', 'in', mpr_job_status_domain)]")

	@api.onchange("employment_status")
	def onchange_employement_status(self):
		if self.employment_status and ('contract' in self.employment_status.code.lower() or 'permanent' in self.employment_status.code.lower()):
			job_status_ids = self.env['master.job.status'].search([('code', 'in', ['OPS', 'NONOPS'])])
			self.mpr_job_status_domain = [(6,0,job_status_ids.ids)]
		else:
			job_status_ids = self.env['master.job.status'].search([])
			self.mpr_job_status_domain = [(6,0,job_status_ids.ids)]
	
	@api.onchange("mpr_job_id")
	def onchange_mpr_job_id(self):
		if self.mpr_job_id:
			self.mpr_job_status_id = self.mpr_job_id.master_id.job_status
		else:
			self.mpr_job_status_id = False