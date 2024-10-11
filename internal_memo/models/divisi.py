import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import requests
from datetime import date, datetime, time
from datetime import timedelta


class JobStatus(models.Model):
	_name           = 'master.job.status'
	_description    = "Job Status"

	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)

class JobTitle(models.Model):
	_name           = 'master.job.title'
	_description    = "Job Title"

	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)

class DivisiCustom(models.Model):
	_inherit = "divisi"

	daily_work_days     = fields.Integer(string = "Hari Kerja Harian")
	monthly_work_days   = fields.Integer(string = "Hari Kerja Bulanan")

	# addition from sunfish
	code     			= fields.Char(string = "Kode", index=True)
	order_id 			= fields.Integer(string='Order', index=True)

	job_status 			= fields.Many2one('master.job.status',string="Job Status")
	job_title 			= fields.Many2one('master.job.title',string="Job Title")
	active				= fields.Boolean(string='Active', index=True)
	periode    			= fields.Selection(
		[ ('periode', 'Periode Waktu'),('month', 'Monthly')], 
		string   = 'Periode Payroll',    
		required =True, 
		Default  = 'month')
	start           	= fields.Integer(string = 'Tanggal Mulai')
	end            		= fields.Integer(string = 'Tanggal Selesai')

	periode_tax    		= fields.Selection(
		[('periode', 'Tgl tertentu'),('month', 'Akhir Bulan')], 
		string   = 'Periode Pajak',    
		required =True, 
		Default  = 'month')
	tax            		= fields.Integer(string = 'Tgl Pajak')

	periode_attend    		= fields.Selection(
		[('periode', 'Periode Waktu'),('month', 'Monthly')], 
		string   = 'Periode Absensi',    
		required =True, 
		Default  = 'month')
	
	attend_start 		= fields.Integer(string='Attendance Start Date')
	attend_end			= fields.Integer(string='Attendance End Date')

	
	
# kode pada employee status
class HrEmployeeStatus(models.Model):
	_inherit = "hr.employee.status"

	code     = fields.Char(string = "Kode", index=True)


# departement dan divisi sama, jadi di buat related aja biar nggak bingung
class DepartementCustom(models.Model):
	_inherit 		= "hr.department"

	division_id 	= fields.Many2one(string = "Divisi" ,comodel_name = "divisi")
	code     		= fields.Char(string = "Kode", index=True)
	order_id 		= fields.Integer(string='Order', index=True)

	job_status 		= fields.Many2one('master.job.status',string="Job Status")
	job_title 		= fields.Many2one('master.job.title',string="Job Title")
	active			= fields.Boolean(string='Active')


# custom area to support sunfish
class AreaCustom(models.Model):
	_inherit 		= "area"

	code     		= fields.Char(string = "Kode")
	code2     		= fields.Char(string = "Kode Area", index=True)
	parent_id 		= fields.Many2one('area',string="Induk Area")
	depth			= fields.Integer(string='Depth', default =1)
	flag			= fields.Integer(string='Depth', default =3)
	active			= fields.Boolean(string='Active', index=True)


class DisciplineType(models.Model):
	_name           = 'discipline.category.type'
	_description    = "Discipline Category Types"

	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)

class DisciplineCategoryCustom(models.Model):
	_inherit 		= "discipline.category"

	code     		= fields.Char(string = "Kode", index=True)
	type_id 		= fields.Many2one('discipline.category.type',string="Type Model")
	month     		= fields.Integer(string = "Bulan")
	point     		= fields.Integer(string = "Point")


class ResignType(models.Model):
	_name           = 'hr.resignation.type'
	_description    = "Resignation Types"

	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)

class ResignReason(models.Model):
	_name           = 'hr.resignation.reason'
	_description    = "Resignation Reason"

	type_id 		= fields.Many2one('hr.resignation.type',string="Resign Type")
	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)


class HrResignationCustom(models.Model):
	_inherit 		= "hr.resignation"

	reason_id 		= fields.Many2one('hr.resignation.reason',string="Reason Option", index=True)
	type_id 		= fields.Many2one('hr.resignation.type',string="Resign Type", related="reason_id.type_id")


class HrLeaveGrade(models.Model):
	_name           = 'hr.leave.grade'
	_description    = "Leave Grade"

	name            = fields.Char(string = 'Name')
	code            = fields.Char(string = 'Code', index=True)
	order_id		= fields.Integer(string='Order', index=True)


class HrLeaveTypeCustom(models.Model):
	_inherit 		= "hr.leave.type"

	formula			= fields.Text(string='Formula')
	day_count		= fields.Char(string='Day Count')
	available_after	= fields.Integer(string='Available After (Days)')
	valid_periode	= fields.Integer(string='Valid Period (Days)')
	repeat_flag		= fields.Boolean(string='Repeat leave')
	repeat_periode	= fields.Integer(string='Repeat Period')
	availability	= fields.Selection([('FULL','Full Availability'),('0','Not Available')], string='Availability')

	min_day_request	= fields.Integer(string='Minimum Day Request')


class ResCountryStateCustom(models.Model):
	_inherit 		= "res.country.state"

	old_id			= fields.Integer(string='Old ID', index = True)

class HrWorkLocationCustom2(models.Model):
	_inherit 		= "hr.work.location"

	code2			= fields.Char(string='Code', index = True)
	address			= fields.Text(string='Address')
	email			= fields.Char(string='Email')
	fax				= fields.Char(string='Fax')
	phone			= fields.Char(string='Phone')

	country_id 		= fields.Many2one('res.country',string="Country", index=True)
	state_id 		= fields.Many2one('res.country.state',string="State", index=True)
	city2_id 		= fields.Many2one('res.city',string="City", index=True)

	workstation_type	= fields.Selection([('Apartment','Apartment'),('Entertainment','Entertainment'),('Factory','Factory'),('Hospital','Hospital'),('Hotel','Hotel'),('House','House'),('Mall','Mall'),('Manufacture','Manufacture'),('Mining','Mining'),('Mobile','Mobile'),('Office','Office'),('Office','Office'),('Retail','Retail'),('School','School'),('The East Owner','The East Owner'),('University','University')],string='Workstation Type', index=True)


class ResCountryCity(models.Model):
	_name           = 'res.country.city'
	_description    = "Kabupaten"

	name            = fields.Char(string = 'Name')
	state_id 		= fields.Many2one('res.country.state',string="State", index=True)
	country_id 		= fields.Many2one('res.country',string="Country", index=True)
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)

# ternyata sudah ada yang bikin
class ResCityCustom(models.Model):
	_inherit 		= "res.city"
	_description    = "City Custom"

	state_id 		= fields.Many2one('res.country.state',string="State", index=True)
	country_id 		= fields.Many2one('res.country',string="Country", index=True)
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)



class ResCountryDistrict(models.Model):
	_name           = 'res.country.district'
	_description    = "Kecamatan"

	name            = fields.Char(string = 'Name')
	city_id 		= fields.Many2one('res.country.city',string="City", index=True)
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)

class ResDistrictCustom(models.Model):
	_inherit 		= "res.district"
	_description    = "District Custom"

	city_id 		= fields.Many2one('res.city',string="City", index=True)
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)


class ResCountrySubdistrict(models.Model):
	_name           = 'res.country.subdistrict'
	_description    = "Kelurahan"

	name            = fields.Char(string = 'Name')
	district_id 	= fields.Many2one('res.country.district',string="District", index=True)
	zipcode         = fields.Char(string = 'Zip Code')
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)

class ResVillageCustom(models.Model):
	_inherit        = 'res.village'
	_description    = "Kelurahan"

	name 			= fields.Char(string="Village Name")
	district_id 	= fields.Many2one('res.district',string="District", index=True)
	zipcode         = fields.Char(string = 'Zip Code')
	active			= fields.Boolean(string='active')
	old_id			= fields.Integer(string='Old ID', index = True)


# tax location
class TaxLocationCustom(models.Model):
	_inherit 		= "tax.location"
	_description    = "Tax Location"

	code            = fields.Char(string = 'Code', index=True)
	tax_no          = fields.Char(string = 'Number')
	address         = fields.Char(string = 'Address')
	authorize       = fields.Char(string = 'Authorize')
	phone       	= fields.Char(string = 'Phone')
	email       	= fields.Char(string = 'Email')
	city       		= fields.Char(string = 'City')
	npwp       		= fields.Char(string = 'NPWP')
	kpp_name        = fields.Char(string = 'KPP Name')

class ResUserCustom(models.Model):
	_name           = 'res.users.custom'
	_description    = "Kelurahan"

	user_id 		= fields.Many2one('res.users',string="Users", index=True)
	old_id			= fields.Integer(string='Old ID', index = True)
	uuid			= fields.Char(string='UUID')
	username		= fields.Char(string='Username')

# inherit cabang
class CabangCustom(models.Model):
	_inherit            = 'cabang'
	_description    	= "Cabang"

	code            = fields.Char(string = 'Code', index=True)


class BankGroup(models.Model):
	_name           = 'res.bank.group'
	_description    = "Group Bank"

	name  		= fields.Char(string='Name')
	code 		= fields.Char(string='Code', index=True)
	pay_gate	= fields.Char(string='Payment Gate')
	order_id 	= fields.Integer(string='Order', index=True)

class BankCustom(models.Model):
	_inherit            = 'res.bank'
	_description    	= "Bank"

	group_id 			= fields.Many2one('res.bank.group',string="Group", index=True)
	code            	= fields.Char(string = 'Code', index=True)
	branch            	= fields.Char(string = 'Branch')
	bi_code            	= fields.Char(string = 'BI Code')
	clr_code            = fields.Char(string = 'Clearing Code')	
	branch_code         = fields.Char(string = 'Branch Code')
	branch_scode        = fields.Char(string = 'Branch SCode')
	#branch            	= fields.Char(string = 'Branch')
	atm_code            = fields.Char(string = 'Kode ATM Bersama')
	rtgs_code           = fields.Char(string = 'RTGS Code')
	ach_code            = fields.Char(string = 'ACH Code')
	ibg_code            = fields.Char(string = 'IBG Code')
	bnm_code            = fields.Char(string = 'BNM Code')
	rentas_code         = fields.Char(string = 'Rentas Code')


class PartnerAccountCustom(models.Model):
	_name           	= 'res.partner.bank.custom'
	_description    	= "Partner bank"

	account_id 			= fields.Many2one('res.partner.bank',string="Account ID", index=True)
	bank_id            	= fields.Char(string = 'bank ID', index=True)

class PartnerBankCustom(models.Model):
	_inherit           	= 'res.partner.bank'
	_description    	= "Partner bank"

	code            	= fields.Char(string = 'Code', index=True)
	is_default			= fields.Boolean(string='Is Default')


class HrEmployeeStatus(models.Model):
	_name           	= 'hr.employee.status.type'
	_description    	= "Employee HR Periode"

	name 				= fields.Many2one('hr.employee' , string="Employee")
	periode_id 			= fields.Many2one('hr.periode' ,  string="Periode Gaji")

class HrEmployeeRelationCustom(models.Model):
	_inherit            = 'hr.employee.relation'
	_description    	= "Employee Relation"

	code            	= fields.Char(string = 'Code', index=True)
	is_child			= fields.Boolean(string='Anak ?', default=False)


class HrEmployeeFamilyCustom(models.Model):
	_inherit            = 'hr.employee.family'
	_description    	= "Employee Family"

	dependent			= fields.Boolean(string='Dependent')
	gender				= fields.Selection([('male','Laki-Laki'),('female','Perempuan'),('lain','Lainnya')], string='Gender')
	alive				= fields.Boolean(string='Alive')
	birthplace			= fields.Char(string='Birthplace')
	occupation			= fields.Char(string='Occupation')
	marital				= fields.Selection([('single','Single'),('married','Married'),('widower','Widower'),('divorced','Divorced'),('widow','Widow'),('cohabitant','Legal Cohabitant')], string='Marital Status')
	blood_type			= fields.Char(string='Blood Type')
	phone				= fields.Char(string='Phone')
	address				= fields.Char(string='Address')
	child_order			= fields.Integer(string='Child Order')

# tax location
#class HrEmployeeFamilyCustom(models.Model):
#	_inherit            = 'tax.location'
#	_description    	= "Tax Location"

#	code			= fields.Char(string='Code')
#	tax_no			= fields.Char(string='Tax No')
#	tax_address		= fields.Char(string='Address')
#	tax_emp			= fields.Char(string='Authorized Employee')
#	tax_phone		= fields.Char(string='Phone')
#	tax_email		= fields.Char(string='Email')
#	tax_city		= fields.Char(string='City')
#	tax_npwp		= fields.Char(string='NPWP')
#	tax_kpp			= fields.Char(string='KPP')


class TaxType(models.Model):
	_name           	= 'tax.type'
	_description    	= "Tax Type"

	name 				= fields.Char(string='Name')
	code 				= fields.Char(string='Code')
	order_id 			= fields.Char(string='Order')
	is_default			= fields.Boolean(string='Default')


# salary structure will be based on catery by default Normal Monthly, Additional, THR, Bonus

class HrPeriodCategory(models.Model):
	_name           	= 'hr.periode.category'
	_description    	= "category HR Periode"

	name 				= fields.Char(string='Name')
	code 				= fields.Char(string='Code')


class HrPayrollStructure(models.Model):
	_inherit            = 'hr.payroll.structure'
	_description    	= "HR Payroll Structure"

	periode_id 			= fields.Many2one('hr.periode' , string="Periode")


# create day up
class HrPayrollDayUp(models.Model):
	_name           	= 'hr.payroll.dayup'
	_description    	= "HR Payroll Day Up"

	name 				= fields.Char(string='Name')
	year				= fields.Integer(string='Tahun')
	month    			= fields.Selection(
		[ 
			('01', 'January'),
			('02', 'February'),
			('03', 'March'),
			('04', 'April'),
			('05', 'May'),
			('06', 'June'),
			('07', 'July'),
			('08', 'August'),
			('09', 'September'),
			('10', 'Oktober'),
			('11', 'November'),
			('12', 'December')
		], 
		string   = 'Bulan',    
		required =True)
	
	dayup			= fields.Integer(string='Day Up')
	
# academic detail not equal with ODOO
#class AcademicDetailCustom(models.Model):
#	_inherit            = 'academic.detail'
#	_description    	= "Academic Detail"

#	edu_type 			= fields.Char(string="Edu Type")
#	is_default			= fields.Boolean(string='Default ?')

#	education_level = fields.Selection(selection_add=[
#       ("sd", "Elementary School"),("smp", "Junior High chool")
#    ])

#	start_year2			= fields.Integer(string='Start Year')
#	end_year2			= fields.Integer(string='End Year')


class ResPartnerCustomAddress(models.Model):
	_inherit 			= "res.partner"
	_description    	= "Partner"


	rt     			= fields.Char(string = "RT")
	rw				= fields.Char(string = "RW")

	city_id 		= fields.Many2one('res.city',string="City", index=True)
	district_id 	= fields.Many2one('res.district',string="District", index=True)
	village_id 		= fields.Many2one('res.village',string="Village", index=True)
	
	
# perubahan job disini aja karena faktor area
class HrJobAreaCustom(models.Model):
	_inherit 			= "hr.job"
	_description    	= "Job Position"

	#work_area_id        = fields.Many2one('area', string='Work Area', required=True)
	work_address_id     = fields.Many2one('res.partner', string='Work Address', required=False, domain="[('is_company','=', True)]")

	# def compute_aging_days(val):


	def send_email_outstanding(self):
		all_jobs = self.search([])
		all_area_line = self.env['work.area.line'].search([('outstanding', '>', 0)])
		# mpr_unit_ids = all_area_line.mapped('approval_request_ids').mapped('mpr_unit')
		approval_request_ids = sorted(list(all_area_line.mapped('approval_request_ids')), key=lambda x: int((datetime.now().date()-x.mpr_tanggal_pemenuhan).days), reverse=True)
		# user_ids = mpr_unit_ids.mapped('pemenuhan')

		# for user in user_ids:
		# units = mpr_unit_ids
		subject = "Outstanding Recruitment"
		body_html = """
		<h1>Outstanding Items</h1>
		<p>Dear Recruitment Teams,</p>
		<p>Here is a brief information regarding the ongoing recruitment request</p>
		<p>Status Kebutuhan Manpower</p>
		<table style="border-collapse: collapse; ">
		<tr>
		<th style="border: 1px solid black; text-align: center;"><b>Branch</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Unit</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Segmentasi</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Request Code</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Tipe</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Req. Date</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Rqrd. Date</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Work Area</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Agging Days</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Jabatan</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Cost Center</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Area</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Lokasi</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Req. Pria</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Req. Wanita</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Total Req.</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Pemenuhan Pria</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Pemenuhan Wanita</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Total Pemenuhan</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Outstanding Pria</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Outstanding Wanita</b></th>
		<th style="border: 1px solid black; text-align: center;"><b>Total Outstanding</b></th>
		</tr>"""
		# for unit in units:
		# 	area_line_unit = all_area_line.filtered(lambda x: unit in x.approval_request_ids.mapped('mpr_unit'))
		# 	# job_ids = all_jobs.filtered(lambda x: x.user_id == user)
		# 	# for job in job_ids:
		# 	for area_line in area_line_unit:
		# 		work_area = area_line.work_area_id.name
		# 		# agging_days =  area_line.age_days
		# 		# outstanding = area_line.outstanding
		# 		# expected_new_employees = area_line.total_expected_new_employees
				# for mpr in area_line.approval_request_ids:
		for mpr in approval_request_ids:
			if mpr.request_status == "done":
				continue
			outstanding = mpr.mpr_jml_req - mpr.mpr_jumlah_pemenuhan
			outstanding_male = mpr.mpr_jumlah_male - mpr.mpr_jumlah_pemenuhan_male
			outstanding_female = mpr.mpr_jumlah_female - mpr.mpr_jumlah_pemenuhan_female
			agging_days = (fields.Date.today() - mpr.mpr_tanggal_request).days
			if agging_days > 0 and outstanding:
				subject = "Outstanding Recruitment"
				body_html += """
				<tr>
				<td style="border: 1px solid black; text-align: center;">{branch}</td>
				<td style="border: 1px solid black; text-align: center;">{unit}</td>
				<td style="border: 1px solid black; text-align: center;">{segmentasi}</td>
				<td style="border: 1px solid black; text-align: center;">{request_code}</td>
				<td style="border: 1px solid black; text-align: center;">{tipe}</td>
				<td style="border: 1px solid black; text-align: center;">{req_date}</td>
				<td style="border: 1px solid black; text-align: center;">{rqrd_date}</td>
				<td style="border: 1px solid black; text-align: center;">{work_area}</td>
				<td style="border: 1px solid black; text-align: center;">{agging_days}</td>
				<td style="border: 1px solid black; text-align: center;">{jabatan}</td>
				<td style="border: 1px solid black; text-align: center;">{cost_center}</td>
				<td style="border: 1px solid black; text-align: center;">{area}</td>
				<td style="border: 1px solid black; text-align: center;">{lokasi}</td>
				<td style="border: 1px solid black; text-align: center;">{req_pria}</td>
				<td style="border: 1px solid black; text-align: center;">{req_wanita}</td>
				<td style="border: 1px solid black; text-align: center;">{total_req}</td>
				<td style="border: 1px solid black; text-align: center;">{pemenuhan_pria}</td>
				<td style="border: 1px solid black; text-align: center;">{pemenuhan_wanita}</td>
				<td style="border: 1px solid black; text-align: center;">{total_pemenuhan}</td>
				<td style="border: 1px solid black; text-align: center;">{outstanding_male}</td>
				<td style="border: 1px solid black; text-align: center;">{outstanding_female}</td>
				<td style="border: 1px solid black; text-align: center;">{total_outstanding}</td>
				</tr>
				""".format(
					branch=mpr.mpr_cabang.name,
					unit=mpr.mpr_unit.name,
					segmentasi=mpr.mpr_segmentasi,
					request_code=mpr.name,
					tipe=mpr.mpr_tipe_request,
					req_date=mpr.mpr_tanggal_request,
					rqrd_date=mpr.mpr_tanggal_pemenuhan,
					work_area=mpr.mpr_area.name,
					agging_days=agging_days,
					jabatan=mpr.mpr_job_id.name,
					cost_center=mpr.mpr_kode_site_card,
					area=mpr.mpr_area.name,
					lokasi=mpr.mpr_alamat_lokasi_pengerjaan,
					req_pria=mpr.mpr_jumlah_male,
					req_wanita=mpr.mpr_jumlah_female,
					total_req=mpr.mpr_jml_req,
					pemenuhan_pria=mpr.mpr_jumlah_pemenuhan_male,
					pemenuhan_wanita=mpr.mpr_jumlah_pemenuhan_female,
					total_pemenuhan=mpr.mpr_jumlah_pemenuhan,
					outstanding_male=outstanding_male,
					outstanding_female=outstanding_female,
					total_outstanding=outstanding,
					# expected_new_employees=mpr.mpr_jml_req
				)
		email = self.env.company.recruitment_email
		body_html+="""</table>"""
		mail_values = {
			'subject': subject,
			'body_html': body_html,
			'email_to': email,
		}
		mail = self.env['mail.mail'].create(mail_values)
		mail.send()


class HrJobPositionRequestAreaCustom(models.Model):
	_inherit 			= 'job.position.request'
	_description    	= "Job Request"

	work_area_id        = fields.Many2one('area', string='Work Area')
	work_address_id     = fields.Many2one('res.partner', string='Work Address')

	def create_new_job_position(self):
		vals = {
				'work_area_id': self.work_area_id.id,
				'expected_new_employees': self.expected_new_employees,
				'outstanding': self.expected_new_employees,
				'age_days': self.age_days,
				'job_id': self.job_id.id,
				'approval_request_ids': [(6,0, self.approval_request_id.ids)]
			}
		self.job_id.website_published = True
		self.state = 'job_position_created'
		lines = self.job_id.work_area_line.filtered(lambda line: line.work_area_id.id == self.approval_request_id.mpr_area.id)
		print('ccccccccccccccc', lines)
		if lines:
			for line in lines:
				line.write({
					'approval_request_ids': [(4, self.approval_request_id.id)],
				})
		else:
			for rec in self.job_id:
				rec.write({'work_area_line': [(0, 0, vals)]})
				

class HrJobLineCustom(models.Model):
	_inherit 			= 'work.area.line'
	_description    	= "Work Area Line"

	work_area_id        = fields.Many2one('area', string='Work Area')

	def _compute_age_days(self):
		for rec in self:
				obj = self.env['job.position.request'].search([('work_area_id','=',rec.work_area_id.id),('job_id','=',rec.job_id.id),('state','=','job_position_created')],order='id DESC',limit=1)
				if obj:
					rec.age_days = obj.age_days
				else:
					rec.age_days = 0






# custom untuk pergerakan pegawai
class HrEmployeeHistoryCustom(models.Model):
	_inherit 			= 'hr.employee.history'
	_description    	= "HR Employee History"

	action_type 		= fields.Selection(selection_add=[('new', 'New'),('rehire', 'REHIRE'),('statuschange', 'STATUSCHANGE')])
	trans_code			= fields.Selection([('JOIN','JOIN'),('MOVEMENT','MOVEMENT'),('REHIRE','REHIRE'),('TERMINATION','TERMINATION')],string='Transition Code', default = 'MOVEMENT')

	emp_no				= fields.Char(string='Employee No')
	master_id 			= fields.Many2one(string = "Job Position" ,comodel_name = "master.job")
	employee_status_id 	= fields.Many2one(string = "Employment Status" ,comodel_name = "hr.contract.type")
	grade_id 			= fields.Many2one(string = "Grade" ,comodel_name = "hr.grade")
	
	job_status_id 		= fields.Many2one(string = "Job Status" ,comodel_name = "master.job.status")
	tax_id 				= fields.Many2one(string = "Tax Location" ,comodel_name = "tax.location")
	resign_type_id 		= fields.Many2one(string = "Resign Type" ,comodel_name = "hr.resignation.type")
	resign_reason_id 	= fields.Many2one(string = "Resign Reason" ,comodel_name = "hr.resignation.reason")
	resign_date			= fields.Date(string='Resign Date')

	supervisor_id 		= fields.Many2one(string = "Supervisor" ,comodel_name = "hr.employee")
	manager_id 			= fields.Many2one(string = "Manager" ,comodel_name = "hr.employee")

	remark				= fields.Char(string='Remark')
	vacant				= fields.Boolean(string='vacant')
	curr_id 			= fields.Many2one(string = "Currency" ,comodel_name = "res.currency")
	salary 				= fields.Monetary(
		'Salary',
		currency_field="curr_id",
		default=0.0,
	)

	salary_update		= fields.Boolean(string='vacant', default = False)











    