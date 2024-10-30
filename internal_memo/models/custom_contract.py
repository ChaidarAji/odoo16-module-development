import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, time,timedelta


class HrPeriode(models.Model):
	_name           = 'hr.periode'
	_description    = "HR Periode"

	name            = fields.Char(string = 'Name')
	periode    		= fields.Selection(
		[ ('periode', 'Periode Waktu'),('month', 'Monthly')], 
		string   = 'Model Gaji',    
		required =True, 
		Default  = 'month')
	start           = fields.Integer(string = 'Start')
	end            	= fields.Integer(string = 'End')

	# custom sunfish
	frequency    		= fields.Selection(
		[ ('MONTHLY', 'MONTHLY'),('ANUALLY', 'ANUALLY')], 
		string   = 'Pay Frequency',    
		required =True, 
		Default  = 'MONTHLY')
	
	paydate 		= fields.Date(string='Pay Date')
	taxdate			= fields.Date(string='Tax Date')
	limitdate		= fields.Date(string='Limit Date')
	calculatetax	= fields.Boolean(string='Calculate Tax')
	currency_code	= fields.Char(string='Currency Code')
	lookupperiod	= fields.Char(string='Lookup Periode')
	backpayperiod	= fields.Char(string='Backpay Periode')
	remark			= fields.Char(string='Remark')
	usesalary		= fields.Boolean(string='Use Salary')
	salarystartdate	= fields.Date(string='Salary Start Date')
	salaryenddate	= fields.Date(string='Salary End Date')
	salarymonthend  = fields.Boolean(string='Salary Month End')
	useattend		= fields.Boolean(string='Use Attendance')
	attendstartdate = fields.Date(string='Attendance Start Date')
	attendenddate	= fields.Date(string='Attendance End Date')
	attendmonthend	= fields.Boolean(string='Attendance Month End')

	category_id 	= fields.Many2one('hr.periode.category',string="Category")
	status_id 		= fields.Many2one('hr.employee.status' , string="Employee Status")
	status			= fields.Selection([('open', 'Open'),('close', 'Close')], string="Status", default='open')


	def button_close_periode(self):
		#check hr.payslip draft
		payslip_draft = self.env['hr.payslip'].sudo().search([('periode_id', '=', self.id), ('state', '=', 'draft')])
		#chek hr.pre.payroll active
		pre_payroll_active = self.env['hr.pre.payroll'].sudo().search([('status', '=', 'active'), ('periode', '=', self.id)])
		if payslip_draft or pre_payroll_active:
			return {
				'type': 'ir.actions.act_window',
				'res_model': 'hr.periode.close.wizard',
				'view_mode': 'form',
				'target': 'new',
				'context': {
					'default_periode_id': self.id,
					'default_payslip_ids_draft': [(6, 0, payslip_draft.ids)],
					'default_pre_payroll_ids_active': [(6, 0, pre_payroll_active.ids)],
				}
			}
			
class HrPeriodeCloseWizard(models.TransientModel):
	_name = 'hr.periode.close.wizard'
	_description = 'HR Periode Close Wizard'

	periode_id = fields.Many2one('hr.periode', string="Periode")
	payslip_ids_draft = fields.Many2many('hr.payslip', string="Payslip Draft")
	pre_payroll_ids_active = fields.Many2many('hr.pre.payroll', string="Pre Payroll Active")
	

class HrContractType(models.Model):
	_inherit = "hr.contract.type"
	
	salary_type    = fields.Selection(
		[ ('daily', 'Harian'),('monthly', 'Bulanan')], 
		string   = 'Model Gaji',    
		required =True, 
		default  = 'monthly')

	salary_amount	  = fields.Integer(string = 'Persen Gaji', default = 100)

	periode = fields.Many2one(
        'hr.periode',
        string="Periode Gaji"
    )

	salary_structure = fields.Many2one(
        'hr.payroll.structure',
        string="Salary Structure"
    )

	# code for auto numbering
	code = fields.Char(string='Kode Kontrak')




# auto numbering contract on create
class HrContract(models.Model):
	_inherit = "hr.contract"

	year 				= fields.Integer(string='Tahun')
	month				= fields.Integer(string='Bulan')
	code 				= fields.Integer(string='Kode Urutan')
	# kapan auto generate

	master_id 			= fields.Many2one('master.job',string="Job Position")
	tax_type_id 		= fields.Many2one('tax.type',string="Tax Type")
	description			= fields.Char(string='Description')
	payfreq				= fields.Selection([('MONTH','MONTH'),('DAY','DAY')],string='Pay Frequency')
	tax_location_id 	= fields.Many2one('tax.location',string="Tax Location")

	# untuk mitra nilai BPJS dan lain-lain beda
	bpjs_ks_mitra		= fields.Integer(string='BPJS KS Untuk Mitra', default = 0)	
	bpjs_tk_mitra		= fields.Integer(string='BPJS TK Untuk Mitra', default = 0)	

	deduction_lebih = fields.Monetary(
		'Potongan Lebih Bayar',
		currency_field="currency_id",
		default=0.0,
	)
	

	# insentif can include on contract
	allow_incentive = fields.Monetary(
		'Incentive',
		currency_field="currency_id",
		default=0.0,
	)

	allow_locationsm = fields.Monetary(
		'Location Allowance TSM',
		currency_field="currency_id",
		default=0.0,
	)

	def aktivasi_kontrak(self):
		today 		= fields.Datetime.now()
		hours_diff 					= 7
		#diff_hours 				= hours_diff*-1
		today 						= today + timedelta(hours=hours_diff)
		today_date 					= today.date()
		
		contract_list 				= self.env['hr.contract'].sudo().search([('date_start','=',today_date)])

		if contract_list:
			for cont in contract_list:
				if cont.state =='draft':
					# finding before
					before_contract = self.env['hr.contract'].sudo().search([('state','=','open'),('employee_id','=',cont.employee_id.id )])
					#new_contract_date = datetime.strptime(record[6], '%Y-%m-%d')
					new_contract_date = datetime.combine(cont.date_start, datetime.min.time())
					close_date = new_contract_date
					close_date = close_date - timedelta(days=1)

					#_logger.error('before contract')
					#_logger.error(before_contract)
					for befo in before_contract:
						befo.write({
							'state'			: 'close',
							'date_end'		: close_date
						})


					cont.write({
						'state' : 'open'
					})

					emp_info = self.env['hr.employee'].sudo().search([('id','=', cont.employee_id.id)])

					# update employee status
					emp_info.write({
						'nip' 				: cont.nik,
						'employment_status'	: cont.contract_type_id.id,
						'job_status'		: cont.job_status_id.id,
						'job_id'			: cont.job_id.id,
						'master_id'			: cont.master_id.id,
						'department_id'		: cont.department_id.id,
						'area'				: cont.area_id.id,
						'work_location_id'	: cont.work_location_id.id,
						'address_id'		: cont.work_location_id.address_id.id
					})

		

	@api.model
	def default_get(self, fields):
		res = super(HrContract,self).default_get(fields)

		# get current year
		current_year 	= datetime.now().year
		current_month 	= datetime.now().month

		contract_code = self.employee_id.contract_id.contract_type_id.code

		if contract_code == False:
			contract_code = self.contract_type_id.code

			if contract_code == False:
				contract_code = ''

		# calculate number before
		current_number = self.env['hr.contract'].sudo().search_read([('year','=',current_year)], order='code DESC', limit=1)

		integer_code = 1

		if len(current_number) > 0:
			current_code = ''
			for curr in current_number:
				current_code = str(curr['code']).zfill(4)
				integer_code = curr['code']
		else:
			current_code = '0001'
			integer_code = 1

		res.update({
			'name' 	: contract_code+str(current_year)+str(current_month).zfill(2)+current_code,
			'year'	: current_year,
			'month'	: current_month,
			'code'	: integer_code
		})

		return res
	
	# on change
	@api.onchange('employee_id', 'contract_type_id')
	def onchange_get_number(self):
		contract_code 	= self.contract_type_id.code
		integer_code	= self.code

		if contract_code != False and integer_code != False:
			self.name	    =  contract_code+str(self.year)+str(self.month).zfill(2)+str(self.code).zfill(4)




class RefReligion(models.Model):
	_name           = 'ref.religion'
	_description    = "Agama"

	name            = fields.Char(string = 'Nama')
	code			= fields.Char(string='Kode Smart Presence')
	code2			= fields.Char(string='Kode')

# area sync
class Area(models.Model):
	_inherit = "area"

	code			= fields.Char(string='Kode Smart Presence')

# work location
class HrWorkLocation(models.Model):
	_inherit = "hr.work.location"

	code			= fields.Char(string='Kode Smart Presence')
	area_id 		= fields.Many2one(string = "Area" ,comodel_name = "area") 
