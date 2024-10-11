import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContractApproval(models.Model):
	_name           = 'hr.contract.approval'
	_description    = "Contract Changes Approval"
	
	name            		= fields.Many2one('hr.employee', string='Pegawai', Required = False)
	date					= fields.Date(string='Tanggal Perubahan', Required = False)
	contract_id     		= fields.Many2one('hr.contract', string='Contract', Required = False)
	currency_id 			= fields.Many2one(string="Currency", related='contract_id.company_id.currency_id', readonly=True)

	# current
	department_id  			= fields.Many2one('hr.department', string='Departement', Required = False)
	start_date				= fields.Date(string='Contract Start Date', Required = False)
	end_date				= fields.Date(string='Contract End Date')
	struct_id     			= fields.Many2one('hr.payroll.structure', string='Salary Struktur', Required = False)
	contract_type  			= fields.Many2one('hr.contract.type', string='Contract Type', Required = False)
	salary_structure_type  	= fields.Many2one('hr.payroll.structure.type', string='Salary Struktur Type', Required = False)
	calendar_id  			= fields.Many2one('resource.calendar', string='Working Schedule', Required = False)
	responsible_id  		= fields.Many2one('res.users', string='HR Responsible', Required = False)
	job_id  				= fields.Many2one('hr.job', string='Job Position', Required = False)

	wage 					= fields.Monetary(string='Wage', default= 0.00)
	da_allowance 			= fields.Monetary(string='Dearing Allowance', default= 0.00)
	acting_allowance 		= fields.Monetary(string='Acting Allowance', default= 0.00)
	competency_allowance 	= fields.Monetary(string='Competency Allowance', default= 0.00)
	location_allowance 		= fields.Monetary(string='Location Allowance', default= 0.00)
	position_allowance 		= fields.Monetary(string='Position Allowance', default= 0.00)
	daily_allowance 		= fields.Monetary(string='Daily Allowance', default= 0.00)
	handphone_allowance     = fields.Monetary(string='Handphone Allowance', default= 0.00)
	performance_allowance   = fields.Monetary(string='Performance Allowance', default= 0.00)
	travel_allowance   		= fields.Monetary(string='Travel Allowance', default= 0.00)
	meal_allowance   		= fields.Monetary(string='Meal Allowance', default= 0.00)
	medical_allowance   	= fields.Monetary(string='Medical Allowance', default= 0.00)
	housing_allowance   	= fields.Monetary(string='Housing Allowance', default= 0.00)
	other_allowance   		= fields.Monetary(string='Other Allowance', default= 0.00)

	#before
	department_id_before  			= fields.Many2one('hr.department', string='Departement Before', Required = False)
	start_date_before				= fields.Date(string='Contract Start Date Before', Required = False)
	end_date_before					= fields.Date(string='Contract End Date Before')
	struct_id_before     			= fields.Many2one('hr.payroll.structure', string='Salary Struktur Before', Required = False)
	contract_type_before  			= fields.Many2one('hr.contract.type', string='Contract Type Before', Required = False)
	salary_structure_type_before  	= fields.Many2one('hr.payroll.structure.type', string='Salary Struktur Type Before', Required = False)
	calendar_id_before  			= fields.Many2one('resource.calendar', string='Working Schedule Before', Required = False)
	responsible_id_before  			= fields.Many2one('res.users', string='HR Responsible Before', Required = False)
	job_id_before  					= fields.Many2one('hr.job', string='Job Position Before', Required = False)

	wage_before 					= fields.Monetary(string='Wage Before', default= 0.00)
	da_allowance_before 			= fields.Monetary(string='Dearing Allowance Before', default= 0.00)
	acting_allowance_before 		= fields.Monetary(string='Acting Allowance Before', default= 0.00)
	competency_allowance_before 	= fields.Monetary(string='Competency Allowance Before', default= 0.00)
	location_allowance_before 		= fields.Monetary(string='Location Allowance Before', default= 0.00)
	position_allowance_before 		= fields.Monetary(string='Position Allowance Before', default= 0.00)
	daily_allowance_before 			= fields.Monetary(string='Daily Allowance Before', default= 0.00)
	handphone_allowance_before     	= fields.Monetary(string='Handphone Allowance Before', default= 0.00)
	performance_allowance_before   	= fields.Monetary(string='Performance Allowance Before', default= 0.00)
	travel_allowance_before   		= fields.Monetary(string='Travel Allowance Before', default= 0.00)
	meal_allowance_before   		= fields.Monetary(string='Meal Allowance Before', default= 0.00)
	medical_allowance_before   		= fields.Monetary(string='Medical Allowance Before', default= 0.00)
	housing_allowance_before   		= fields.Monetary(string='Housing Allowance Before', default= 0.00)
	other_allowance_before   		= fields.Monetary(string='Other Allowance Before', default= 0.00)

	state							= fields.Selection([('submit','Submitted'),('approve','Approved'),('reject','Rejected')])
	reviewed_by  					= fields.Many2one('res.users', string='Reviewed By', Required = False)
	description						= fields.Text(string='Description')
	description_request				= fields.Text(string='Request Description')

	@api.onchange('name')
	def onchange_periode(self):
		employee_info = self.env['hr.employee'].sudo().search([('id','=', self.name.id)])

		self.contract_id 				= employee_info.contract_id
		self.department_id				= employee_info.contract_id.department_id.id
		self.start_date					= employee_info.contract_id.date_start
		self.end_date					= employee_info.contract_id.date_end
		self.struct_id					= employee_info.contract_id.struct_id.id
		self.contract_type				= employee_info.contract_id.type_id.id
		self.salary_structure_type		= employee_info.contract_id.structure_type_id
		self.calendar_id				= employee_info.contract_id.resource_calendar_id.id
		self.responsible_id				= employee_info.contract_id.hr_responsible_id.id
		self.job_id						= employee_info.contract_id.job_id.id
		self.wage						= employee_info.contract_id.wage
		self.da_allowance				= employee_info.contract_id.da
		self.acting_allowance			= employee_info.contract_id.acting_allowance
		self.competency_allowance		= employee_info.contract_id.competency_allowance
		self.location_allowance			= employee_info.contract_id.location_allowance
		self.position_allowance			= employee_info.contract_id.position_allowance
		self.daily_allowance			= employee_info.contract_id.daily_allowance
		self.handphone_allowance		= employee_info.contract_id.handphone_allowance
		self.performance_allowance		= employee_info.contract_id.performance_allowance
		self.travel_allowance			= employee_info.contract_id.travel_allowance
		self.meal_allowance				= employee_info.contract_id.meal_allowance
		self.medical_allowance			= employee_info.contract_id.medical_allowance
		self.housing_allowance			= employee_info.contract_id.housing_allowance
		self.other_allowance			= employee_info.contract_id.other_allowance

		# sebelum
		self.department_id_before				= employee_info.contract_id.department_id.id
		self.start_date_before					= employee_info.contract_id.date_start
		self.end_date_before					= employee_info.contract_id.date_end
		self.struct_id_before					= employee_info.contract_id.struct_id.id
		self.contract_type_before				= employee_info.contract_id.type_id.id
		self.salary_structure_type_before		= employee_info.contract_id.structure_type_id
		self.calendar_id_before					= employee_info.contract_id.resource_calendar_id.id
		self.responsible_id_before				= employee_info.contract_id.hr_responsible_id.id
		self.job_id_before						= employee_info.contract_id.job_id.id
		self.wage_before						= employee_info.contract_id.wage
		self.da_allowance_before				= employee_info.contract_id.da
		self.acting_allowance_before			= employee_info.contract_id.acting_allowance
		self.competency_allowance_before		= employee_info.contract_id.competency_allowance
		self.location_allowance_before			= employee_info.contract_id.location_allowance
		self.position_allowance_before			= employee_info.contract_id.position_allowance
		self.daily_allowance_before				= employee_info.contract_id.daily_allowance
		self.handphone_allowance_before			= employee_info.contract_id.handphone_allowance
		self.performance_allowance_before		= employee_info.contract_id.performance_allowance
		self.travel_allowance_before			= employee_info.contract_id.travel_allowance
		self.meal_allowance_before				= employee_info.contract_id.meal_allowance
		self.medical_allowance_before			= employee_info.contract_id.medical_allowance
		self.housing_allowance_before			= employee_info.contract_id.housing_allowance
		self.other_allowance_before				= employee_info.contract_id.other_allowance

	# on approve, updating contract data
	



