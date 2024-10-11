import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import requests
from datetime import date, datetime, time
from datetime import timedelta
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class JobMaster(models.Model):
	_name           = 'master.job'
	_description    = "Position Master"

	name            = fields.Char(string = 'Name')
	divisi_id 		= fields.Many2one(string = "Divisi" ,comodel_name = "hr.department") 
	parent_id 		= fields.Many2one(string = "Parent" ,comodel_name = "master.job") 
	grade_id 		= fields.Many2one(string = "Grade" ,comodel_name = "hr.grade")

	# tambahan sunfish
	code     			= fields.Char(string = "Kode", index=True)
	order_id 			= fields.Integer(string='Order', index=True)

	job_status 			= fields.Many2one('master.job.status',string="Job Status", index=True)
	job_title 			= fields.Many2one('master.job.title',string="Job Title")
	active				= fields.Boolean(string='Active', index=True, default=True)

	@api.constrains('parent_id')
	def _validate_parent_id(self):
			for doc in self:
					if doc.parent_id and doc.parent_id.id == doc.id:
							raise ValidationError(_("parent_id and id cant be the same"))
					

	# on create
	@api.model
	def create(self,vals):
		# insert all hr_job
		#all_job = self.env['master.job'].sudo().search([])

		#for joba in all_job:
		#	job_info = self.env['hr.job'].sudo().search([('master_id','=',joba.id)])

		#	is_exist = False

		#	for joi in job_info:
		#		is_exist = True

		#		if joba.name =='Facility Services Manager' or joba.name == 'Acting Operation Commander' or joba.name == 'IFS Coordinator':
		#			joi.write({
		#				'active' 			: joba.active,
		#				'department_id' 	: joba.divisi_id.id,
		#				'name'				: joba.name+' ('+joba.job_status.name+')'
		#			})
		#		else:
		#			joi.write({
		#				'active' 			: joba.active,
		#				'department_id' 	: joba.divisi_id.id,
		#				'name'				: joba.name
		#			})

		#	if is_exist == False:
		#		if joba.name =='Facility Services Manager' or joba.name == 'Acting Operation Commander' or joba.name == 'IFS Coordinator':
		#			result = self.env['hr.job'].sudo().create({
		#				'active' 					: joba.active,
		#				'master_id'					: joba.id,
		#				'department_id' 			: joba.divisi_id.id,
		#				'name'						: joba.name+' ('+joba.job_status.name+')',
		#				'is_published'				: False,
		#				'work_area_line_count'		: 0
		#			})
		#		else:
		#			result = self.env['hr.job'].sudo().create({
		#				'active' 					: joba.active,
		#				'master_id'					: joba.id,
		#				'department_id' 			: joba.divisi_id.id,
		#				'name'						: joba.name,
		#				'is_published'				: False,
		#				'work_area_line_count'		: 0
		#			})

		res = super(JobMaster, self).create(vals)

		result = self.env['hr.job'].sudo().create({
			'active' 					: res.active,
			'master_id'					: res.id,
			'department_id' 			: res.divisi_id.id,
			'name'						: res.name,
			'is_published'				: False,
			'work_area_line_count'		: 0
		})

		return res
	
	def write(self, values):
		res = super(JobMaster, self).write(values)

		job_info = self.env['hr.job'].sudo().search([('master_id','=',res.id)])

		for job in job_info:
			job.write({
				'active' 			: res.active,
				'department_id' 	: res.divisi_id.id,
				'name'				: res.name
			})

		return res
	
	# unlink
	def unlink(self):
		# unlink hr.job
		active_id =  self.env.context.get('active_id')

		hr_job = self.env['hr.job'].sudo().search([('master_id','=',active_id)])
		
		for hr in hr_job:
			hr.unlink()

		return super(JobMaster, self).unlink()


class GradePosition(models.Model):
	_inherit = "hr.grade"

	parent_id 		= fields.Many2one(string = "Parent" ,comodel_name = "hr.grade") 

class JobPosition(models.Model):
	_inherit = "hr.job"

	master_id 			= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job") 

	code     			= fields.Char(string = "Kode", related='master_id.code')
	order_id 			= fields.Integer(string='Order', related='master_id.order_id')

	job_status 			= fields.Many2one('master.job.status',string="Job Status", related='master_id.job_status')
	job_title 			= fields.Many2one('master.job.title',string="Job Title", related='master_id.job_title')
	active				= fields.Boolean(string='Active', related='master_id.active')
	work_area_id = fields.Many2one('res.partner', string='Work  Address')


	@api.onchange('master_id')
	def _onchange_master_id(self):
		job_info = self.env['master.job'].sudo().search_read([('id','=',self.master_id.id)],['id','name'])

		if len(job_info) > 0:
			for job in job_info:
				self.name	= job['name']

class HrWorkLocationMemo(models.Model):
	_inherit = "hr.work.location"

	regional_id = fields.Many2one(string = "Regional" ,comodel_name = "hr.payroll.regional.setting") 


class HrEmployeePayrollPembayaran(models.Model):
	_name           = 'hr.employee.pembayaran'
	_description    = "Pengaturan Pembayaran"

	name            = fields.Many2one("hr.employee", string = "Pegawai") 
	category        = fields.Many2one(string = "Pembayaran Untuk" ,comodel_name = "hr.periode.category") 
	method			= fields.Selection([('BANK','BANK'),('CASH','CASH')], string='Metode Bayar')
	partner_id		= fields.Many2one("res.partner", string = "Partner", related="name.address_home_id") 

	rekening		= fields.Many2one(string = "Rekening" ,comodel_name = "res.partner.bank", domain="[('partner_id','=', partner_id)]") 



class HrEmployeeJabatan(models.Model):
	_inherit = "hr.employee"

	# one2many
	pembayaran_ids 	= fields.One2many('hr.employee.pembayaran', 'name', 'Pengaturan Pembayaran')

	master_id 		= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job") 
	religion_id 	= fields.Many2one(string = "Agama" ,comodel_name = "ref.religion") 
	code			= fields.Char(string='Kode Smart Presence')

	# change area and other to 
	area			= fields.Many2one(string = "Cost Center" ,comodel_name = "area" )
	divisi			= fields.Many2one(string = "Divisi" ,comodel_name = "divisi") 
	cabang			= fields.Many2one(string = "Cabang" ,comodel_name = "cabang") 

	# from sunfish
	first_name		= fields.Char(string='First Name')
	middle_name		= fields.Char(string='Middle Name')
	last_name		= fields.Char(string='Last Name')
	geocoord		= fields.Char(string='GEO Coordinate')
	req_status		= fields.Boolean(string="Req Status")
	lastreqno		= fields.Char(string='Last Req No')
	official_name	= fields.Char(string='Official Name')
	initial_name	= fields.Char(string='Initial Name')
	recruitment_no	= fields.Char(string='Recruitment No')
	marital_date	= fields.Date(string='marital Date')
	married_place	= fields.Char(string='Married Place')

	marital 		= fields.Selection(selection_add=[
    		('widow', 'Widow')
	])

	job_status 		= fields.Many2one('master.job.status',string="Job Status")

	# custom fields
	c1			= fields.Char(string='Custom Field 1')
	c2			= fields.Char(string='Custom Field 2')
	c3			= fields.Char(string='Custom Field 3')
	c4			= fields.Char(string='Custom Field 4')
	c5			= fields.Char(string='Custom Field 5')
	c6			= fields.Char(string='Custom Field 6')
	c7			= fields.Char(string='Custom Field 7')
	c8			= fields.Char(string='Custom Field 8')
	c9			= fields.Char(string='Custom Field 9')
	c10			= fields.Char(string='Custom Field 10')

	job_status 		 	= fields.Many2one('master.job.status',string="Job Status")

	custom1 		 	= fields.Many2one('hr.payroll.regional.setting',string="Regional")
	custom2				= fields.Selection([('Ex ISS','Ex ISS'),('NEW','NEW'),('ABSORB','ABSORB')],string='Flag')
	custom3				= fields.Selection([('DAILY','DAILY'),('MONTHLY','MONTHLY')],string='PayFreq')
	custom4				= fields.Selection([('8','8 Jam'),('12','12 Jam')],string='Security Type')
	#c3			= fields.Char(string='Custom Field 3')
	#c4			= fields.Char(string='Custom Field 4')
	custom7				= fields.Selection([('A','A'),('B','B'),('C','C')],string='Performance')
	custom8				= fields.Date(string='Tanggal PKWT')
	custom9				= fields.Date(string='Tanggal Permanent')
	custom10			= fields.Date(string='Expired SKCK')
	custom11			= fields.Selection([('1','Yes'),('0','No')],string='Employee Certification')
	custom12			= fields.Selection([('Sebelum Deployment','Sebelum Deployment'),('Setelah Deployment','Setelah Deployment'),('Belum Training','Belum Training')],string='Training (NCC, GP, dll)')

	nip 				= fields.Char('NIP', index=True)

	# additional
	supervisor_code			= fields.Char('Supervisor Code', index=True)
	contract_type			= fields.Many2one('hr.contract.type',string="Contract Type")

	#bank_ids 				= fields.One2many('res.partner.bank', 'partner_id', string='Banks')
	info_work 				= fields.Boolean(string='Access Work Info', compute="_get_info_work", default = True)

	# contract type	
	employment_status 		 = fields.Many2one('hr.contract.type',string="Employment Status")

	# send email status
	send_mail				 = fields.Selection([('yes','Ya'),('no','Tidak')], string='Kirim Email Gaji') 

	@api.onchange("master_id")
	def onchange_master_id(self):
		self.department_id = self.master_id.divisi_id

		job_info = self.env['hr.job'].sudo().search([('master_id','=', self.master_id.id)])

		if job_info.id != False:
			self.job_id = job_info

		if self.master_id.grade_id.id != False:
			self.grade_id = self.master_id.grade_id

	def _get_info_work(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_work_group'):
			self.info_work = True
		else:
			self.info_work = False

	info_private 				= fields.Boolean(string='Access Work Info', compute="_get_info_private", default = True)

	def _get_info_private(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_private_group'):
			self.info_private = True
		else:
			self.info_private = False

	info_hr 				= fields.Boolean(string='HR Setting', compute="_get_info_hr", default = True)

	def _get_info_hr(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_history_group'):
			self.info_hr = True
		else:
			self.info_hr = False

	info_badge 				= fields.Boolean(string='HR Setting', compute="_get_info_badge", default = True)

	def _get_info_badge(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_badge_group'):
			self.info_badge = True
		else:
			self.info_badge = False

	info_academic 				= fields.Boolean(string='Academic Detail Access', compute="_get_info_academic", default = True)

	def _get_info_academic(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_academic_group'):
			self.info_academic = True
		else:
			self.info_academic = False


	info_certificate 				= fields.Boolean(string='Certificate Detail Access', compute="_get_info_certificate", default = True)

	def _get_info_certificate(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_certificate_group'):
			self.info_certificate = True
		else:
			self.info_certificate = False
	
	info_profesional 				= fields.Boolean(string='Proffesional Detail Access', compute="_get_info_profesional", default = True)

	def _get_info_profesional(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_profesional_group'):
			self.info_profesional = True
		else:
			self.info_profesional = False

	info_summary 				= fields.Boolean(string='Summary Detail Access', compute="_get_info_summary", default = True)

	def _get_info_summary(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_summary_group'):
			self.info_summary = True
		else:
			self.info_summary = False

	info_history 				= fields.Boolean(string='History Detail Access', compute="_get_info_history", default = True)

	def _get_info_history(self):
		if self.env.user.has_group('internal_memo.custom_employee_field_access_setting_history_group'):
			self.info_history = True
		else:
			self.info_history = False

	
	# sending API
	@api.model
	def create(self,vals):
		res = super(HrEmployeeJabatan, self).create(vals)

		if res:
			# jika ada applicant ids
			if len(res.applicant_id) > 0:
				for applyc in res.applicant_id:
					# approval
					mpr_info = self.env['approval.request'].sudo().search([('id','=',applyc.approval_request_id.id)])

					# struktur will be based on current employee status
					periode_info = self.env['hr.periode'].sudo().search([('status_id','=', res.employee_status_id.id),('category_id.code','=','DEFAULT')])

					is_periode_info = False

					for period in periode_info:
						is_periode_info = True
						# find default salary structure
						struct_id = self.env['hr.payroll.structure'].sudo().search([('periode_id','=',period.id)])
					
					if is_periode_info == False:
						raise UserError('Periode Payroll Belum Di Set')		

					trans_info = self.env['hr.employee.history.transition'].sudo().search([('name','=','JOIN')])
					action_info	= self.env['hr.employee.history.action'].sudo().search([('name','=','NEW')])

					# finding tunjangan berdasarkan MPR
					tunjangan_jabatan 		= 0
					acting_allowance    	= 0
					competency_allowance    = 0
					location_allowance		= 0
					allow_locationsm        = 0
					position_allowance      = 0
					daily_allowance         = 0
					tor_allowance           = 0
					handphone_allowance     = 0
					performance_allowance   = 0
					travel_allowance        = 0
					meal_allowance          = 0
					medical_allowance       = 0
					housing_allowance       = 0
					shift_allowance         = 0
					guarantine_allowance    = 0
					allow_incentive         = 0
					adjustment_plus         = 0
					all_backup              = 0
					national_allowance      = 0
					netral_allowance        = 0
					rapel_allowance         = 0
					tax_adjustment          = 0
					travel2_allowance       = 0
					bonus                   = 0
					car_allowance           = 0
					deduct_adv              = 0
					deduct_car              = 0
					deduct_dormit           = 0
					deduct_meal             = 0
					deduct_rapel            = 0
					deduct_seragam          = 0
					deduct_sepatu           = 0
					deduct_training         = 0
					deduct_security         = 0
					bpjs_ks_mitra           = 0
					bpjs_tk_mitra           = 0
					other_allowance         = 0
					
					if len(mpr_info.mpr_tunjangan) > 0:
						for tunj in mpr_info.mpr_tunjangan:
							if tunj.name.name == 'Competency Allowance':
								competency_allowance = tunj.value
							elif  tunj.name.name == 'Daily Allowance':
								daily_allowance = tunj.value
							elif  tunj.name.name == 'Handphone Allowance':
								handphone_allowance = tunj.value
							elif  tunj.name.name == 'Location Allowance':
								location_allowance = tunj.value
							elif  tunj.name.name == 'Transport Allowance':
								travel_allowance = tunj.value
							elif  tunj.name.name == 'Guaranteed Incentive':
								guarantine_allowance = tunj.value
							elif  tunj.name.name == 'Housing Allowance':
								housing_allowance = tunj.value
							elif  tunj.name.name == 'Meal Allowance':
								meal_allowance = tunj.value
							elif  tunj.name.name == 'Position Allowance':
								position_allowance = tunj.value
							elif  tunj.name.name == 'TOR Allowance':
								tor_allowance = tunj.value


					resx = self.env['hr.contract'].sudo().create({
						'employee_id'               : res.id,
						'date_start'                : mpr_info.mpr_tgl_kontrak_mulai,
						'date_end'                  : mpr_info.mpr_tgl_kontrak_selesai,
						'department_id'             : res.department_id.id,
						'master_id'                 : res.master_id.id,
						'structure_type_id'         : 1, 
						'resource_calendar_id'      : 1,
						'schedule_pay'              : 'monthly',
						'struct_id'                 : struct_id.id,
						'type_id'                   : res.employment_status.id,
						'job_id'                    : res.job_id.id,
						'contract_type_id'          : res.employment_status.id,
						'hr_responsible_id'         : False,
						'employee_status2_id'        : res.employee_status_id.id,
						'work_location_id'          : res.work_location_id.id,
						'work_address_id'           : res.work_location_id.address_id.id,
						'wage'                      : mpr_info.mpr_ump_wilayah_nilai,
						'tunjangan_jabatan'         : tunjangan_jabatan,
						'acting_allowance'          : acting_allowance,
						'competency_allowance'      : competency_allowance,
						'location_allowance'        : location_allowance,
						'allow_locationsm'          : allow_locationsm,
						'position_allowance'        : position_allowance,
						'daily_allowance'           : daily_allowance,
						'tor_allowance'             : tor_allowance,
						'handphone_allowance'       : handphone_allowance,
						'performance_allowance'     : performance_allowance,
						'travel_allowance'          : travel_allowance,
						'meal_allowance'            : meal_allowance,
						'medical_allowance'         : medical_allowance,
						'housing_allowance'         : housing_allowance,
						'shift_allowance'           : shift_allowance,
						'guarantine_allowance'      : guarantine_allowance,
						'allow_incentive'           : allow_incentive,
						'adjustment_plus'           : adjustment_plus,
						'all_backup'                : all_backup,
						'national_allowance'        : national_allowance,
						'netral_allowance'          : netral_allowance,
						'rapel_allowance'           : rapel_allowance,
						'tax_adjustment'            : tax_adjustment,
						'travel2_allowance'         : travel2_allowance,
						'bonus'                     : bonus,
						'car_allowance'             : car_allowance,
						'deduct_adv'                : deduct_adv,
						'deduct_car'                : deduct_car,
						'deduct_dormit'             : deduct_dormit,
						'deduct_meal'               : deduct_meal,
						'deduct_rapel'              : deduct_rapel,
						'deduct_seragam'            : deduct_seragam,
						'deduct_sepatu'             : deduct_sepatu,
						'deduct_training'           : deduct_training,
						'deduct_security'           : deduct_security,
						'bpjs_ks_mitra'             : bpjs_ks_mitra,
						'bpjs_tk_mitra'             : bpjs_tk_mitra,
						'other_allowance'           : other_allowance,
						'trans_id'             		: trans_info.id,
						'action_id'            		: action_info.id,
						'grade_id'                  : res.grade_id.id,
						'job_status_id'             : res.job_status.id,
						'resign_type_id'       		: False,
						'resign_reason_id'     		: False,
						'resign_date'	          	: False,
						'supervisor_id'        		: res.coach_id.id,
						'manager_id'           		: res.parent_id.id,
						'remark'               		: 'New Employee',
						'area_id'                   : res.area.id,
						'nik'                       : res.nip,
						'request_no'           		: mpr_info.name
					})

					if resx:
						# write
						resx.write({
							'state' : 'open'
						})

						# inserting pemenuhan
						# current date
						today = date.today()

						if res.gender =='male':
							submit_pemenuhan_male 	= 1
							submit_pemenuhan_female = 0
						else:
							submit_pemenuhan_male 	= 0
							submit_pemenuhan_female = 1

						res_pemenuhan = self.env['riwayat.pemenuhan'].sudo().create({
							'name' 						: res.name,
							'submit_pemenuhan'			: 1,
							'submit_pemenuhan_male'		: submit_pemenuhan_male,
							'submit_pemenuhan_female' 	: submit_pemenuhan_female,
							'confirm_pemenuhan'			: 0,
							'confirm_pemenuhan_male'	: 0,
							'confirm_pemenuhan_female'	: 0,
							'date'						: today,
							'request_id'				: mpr_info.id,
							'state'						: 'submitted'
						})
						email_to = mpr_info.request_owner_id.login
						mpr_info.send_request_approval_pemenuhan_email(email_to)
		try:
			# sending to API
			url = 'https://api.smartpresence.id/v1/customrequest/employee_insert'

			location_info = self.env['hr.work.location'].sudo().search([('id','=', res.work_location_id.id)])

			headers = {
				"Content-Type"	: "application/json", 
				"Accept"		: "*/*", 
				"Catch-Control"	: "no-cache",
				"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
			}

			dt = datetime.combine(res.join_date, datetime.min.time())

			data = {
				"name"          : res.name,
				"religionid"    : res.religion_id.code,
				"pin"           : res.pin,
				#"workhourid"    : null,
				"phonenumber"   : res.work_phone,
				"scanner"           : "",
				"location"          : [location_info.code],
				"attributevalue"    : [res.area.code],
				"attributevariable" : [
						{"idatributvariable":8,"variable": res.nip},
								{"idatributvariable":4,"variable": dt.strftime('%Y-%m-%d')}
				],
				"activedate": dt.strftime('%Y-%m-%d')
			}

			response = requests.post(url, data=json.dumps(data), headers=headers)
			json_response = response.json()
			
			if json_response['status'] == 'OK':
				res.write({
									'code': str(json_response['id'])
							})
			else:
				raise UserError('Gagal Input Pada API')

			return res
		except:
			raise UserError('Gagal Input Pada API')

	
	# on update
	def write(self, values):
		nip_before = self.nip
		current_id = self.id

		res = self.env['hr.employee'].sudo().search([('id','=', current_id)])
		return super(HrEmployeeJabatan, self).write(values)

		url = 'https://api.smartpresence.id/v1/customrequest/employee_update'

		location_info = self.env['hr.work.location'].sudo().search([('id','=', res.work_location_id.id)])

		headers = {
			"Content-Type"	: "application/json", 
			"Accept"		: "*/*", 
			"Catch-Control"	: "no-cache",
			"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
		}

		dt = datetime.combine(res.join_date, datetime.min.time())

		if str(values.get('pin')) != 'None':
			data = {
				"empno"         : nip_before,
				"name"          : res.name,
				"religionid"    : res.religion_id.code,
				"pin"           : res.pin,
				#"workhourid"    : null,
				"phonenumber"   : res.work_phone,
				"scanner"           : "",
				"location"          : [location_info.code],
				"attributevalue"    : [res.area.code],
				"attributevariable" : [
						{"idatributvariable":8,"variable": res.nip},
						{"idatributvariable":4,"variable": dt.strftime('%Y-%m-%d')}
				],
				"activedate": dt.strftime('%Y-%m-%d')
			}
		else:
			data = {
				"empno"         : nip_before,
				"name"          : res.name,
				"religionid"    : res.religion_id.code,
				"pin"           : "",
				#"workhourid"    : null,
				"phonenumber"   : res.work_phone,
				"scanner"           : "",
				"location"          : [location_info.code],
				"attributevalue"    : [res.area.code],
				"attributevariable" : [
						{"idatributvariable":8,"variable": res.nip},
						{"idatributvariable":4,"variable": dt.strftime('%Y-%m-%d')}
				],
				"activedate": dt.strftime('%Y-%m-%d')
			}


		##response 			= requests.post(url, data=json.dumps(data), headers=headers)
		##json_response 		= response.json()

		#_logger.error('CHECK VALUE UPDATE')
		#_logger.error(data)
		#_logger.error(json_response)

		##if json_response['status'] == 'OK':
		##	halo = 1
		##else:
		##	if json_response['status'] == 'error' and json_response['errormsg'] == 'Employee No is not found':
				# sending to API
		##		url = 'https://api.smartpresence.id/v1/customrequest/employee_insert'

		##		location_info = self.env['hr.work.location'].sudo().search([('id','=', res.work_location_id.id)])

		##		headers = {
		##			"Content-Type"	: "application/json", 
		##			"Accept"		: "*/*", 
		##			"Catch-Control"	: "no-cache",
		##			"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
		##		}

		##		dt = datetime.combine(res.join_date, datetime.min.time())

		##		data = {
		##			"name"          : res.name,
		##			"religionid"    : res.religion_id.code,
		##			"pin"           : res.pin,
					#"workhourid"    : null,
		##			"phonenumber"   : res.work_phone,
		##			"scanner"           : "",
		##			"location"          : [location_info.code],
		##			"attributevalue"    : [res.area.code],
		##			"attributevariable" : [
		##					{"idatributvariable":8,"variable": res.nip},
		##					{"idatributvariable":4,"variable": dt.strftime('%Y-%m-%d')}
		##			],
		##			"activedate": dt.strftime('%Y-%m-%d')
		##		}

		##		#_logger.error('CHECK VALUE INSERT')
		##		#_logger.error(data)

		##		response = requests.post(url, data=json.dumps(data), headers=headers)

		##		json_response = response.json()

		##		if json_response['status'] == 'OK':
		##			res.write({
		##				'code': str(json_response['id'])
		##			})
		##		else:
		##			raise UserError('Gagal Input Pada API')

		##	else:
		##		raise UserError(json_response['errormsg'])

		return res2

	
	#onchange
	@api.onchange('job_id')
	def _onchange_job_id(self):
		if self.job_id.master_id.grade_id.id != False:
			self.grade_id 	= self.job_id.master_id.grade_id.id
		
		self.master_id	= self.job_id.master_id.id
		self.job_title	= self.job_id.master_id.name
		
		#job_info = self.env['hr.job'].sudo().search_read([('id','=',self.job_id.master_id.id)],['id','name','grade_id'])

		#if len(job_info) > 0:
		#	for job in job_info:
		#		self.grade_id 	= self.job_id.master_id.grade_id.id
		#		self.master_id	= self.job_id.master_id.id
		#		self.job_title	= self.job_id.master_id.name

	@api.onchange('master_id')
	def _onchange_master_id(self):
		job_info = self.env['master.job'].sudo().search_read([('id','=',self.master_id.id)],['id','name','grade_id'])

		if len(job_info) > 0:
			for job in job_info:
				if job['name'] != False:
					self.job_title	= job['name']

				if job['grade_id'] != False:
					self.grade_id 	= job['grade_id'][0]

	@api.onchange('grade_id')
	def _onchange_grade_id(self):
		job_info = self.env['hr.grade'].sudo().search_read([('id','=',self.grade_id.id)],['id','name'])

		if len(job_info) > 0:
			for job in job_info:
				self.job_title	= job['name']


