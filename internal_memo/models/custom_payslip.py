# -*- coding:utf-8 -*-

import babel
from collections import defaultdict
from datetime import date, datetime, time
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pytz import utc

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_utils

import json
import requests
import logging
import base64
import io

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter

class HrPrePayroll(models.Model):
	_name           = 'hr.pre.payroll'
	_description    = "Process Payroll Data"

	periode 		= fields.Many2one(string = "Payroll Periode" ,comodel_name = "hr.periode") 
	name			= fields.Many2one(string = "Pegawai" ,comodel_name = "hr.employee")
	rule_id			= fields.Many2one(string = "Komponen Payroll" ,comodel_name = "hr.salary.rule")
	rule_code		= fields.Char(string='Salary Rule Code', related="rule_id.code")
	value			= fields.Float(string='Nominal')
	status			= fields.Selection([('active','Aktif'),('inactive','Tidak Aktif')], string='Status Payroll')
	year			= fields.Integer(string='Tahun')
	bulan   		 = fields.Selection(
		[ 
			('01', 'Januari'),
			('02', 'Februari'),
			('03', 'Maret'),
			('04', 'April'),
			('05', 'Mei'),
			('06', 'Juni'),
			('07', 'Juli'),
			('08', 'Agustus'),
			('09', 'September'),
			('10', 'Oktober'),
			('11', 'November'),
			('12', 'Desember')
		], 
		string   = 'Bulan',    
		required =True, 
		Default  = datetime.now().strftime("%m"))
	
	ignore_formula		= fields.Boolean(string='Ignore Formula')
	nik					= fields.Char(string='NIK')

	


class HrPayslipContract(models.Model):
	_name           = 'hr.payslip.contract'
	_description    = "Payslip Contract"

	name            	= fields.Many2one(string = "Contract" ,comodel_name = "hr.contract") 
	date_start			= fields.Date(string='Date Start', related = 'name.date_start')
	date_end			= fields.Date(string='Date End', related = 'name.date_end')
	payslip_id          = fields.Many2one(string = "Payslip" ,comodel_name = "hr.payslip") 
	work_days			= fields.Char(string='Work Days')


class HrPayslipCustom(models.Model):
	_inherit = "hr.payslip"

	send_mail	= fields.Selection([('yes','Ya'),('no','Tidak')], string='Kirim Email Gaji', related="employee_id.send_mail") 

	


	currency_id = fields.Many2one('res.currency', string="Currency",
								 default=lambda
								 self: self.env.user.company_id.currency_id.id)
	
	year = fields.Integer(
		'Year',
		default=datetime.now().strftime("%Y"),
	)
	month    = fields.Selection(
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
		string   = 'Month',    
		required =True, 
		Default  = datetime.now().strftime("%m"))

	# because split cost there will be parent child
	parent_id	= fields.Many2one('hr.payslip',string="Main Payslip", index=True)
	child_ids 	= fields.One2many('hr.payslip', 'parent_id', string='Payslip Per Cost Center', readonly=True)

	nik						= fields.Char(string='NIK', related = 'employee_id.nip')
	employee_name			= fields.Char(string='Name', related = 'employee_id.name')

	contract_type = fields.Many2one(
		'hr.contract.type',
		string="Contract Type",
		related='contract_id.contract_type_id',
	)

	province = fields.Many2one(
		'res.country.state',
		string="Province"
	)

	ump = fields.Monetary(
		'UMP',
		currency_field="currency_id",
		default=0.0,
	)

	is_resign = fields.Boolean(
		string="Resign ?",
	)

	work_days = fields.Integer(
		'Work Days',
		default=0.0,
	)

	work_expected = fields.Integer(
		'Days Expected',
		default=0.0,
	)

	salary = fields.Monetary(
		'Salary',
		currency_field="currency_id",
		default=0.0,
	)

	position_id = fields.Many2one(
		'master.job',
		string="Job Position"
	)

	departement_id = fields.Many2one(
		'hr.department',
		string="Departement"
	)

	location_id = fields.Many2one(
		'hr.work.location',
		string="Work Location"
	)

	area_id = fields.Many2one(
		'area',
		string="Cost Centre"
	)

	grade_id = fields.Many2one(
		'hr.grade',
		string="Grade"
	)

	tax_type 		= fields.Selection([('local','Local'),('fixed','Fixed')], string='Tax Type')
	tax_location_id = fields.Many2one('tax.location',string="Tax Location")
	payfreq			= fields.Selection([('DAILY','DAILY'),('MONTHLY','MONTHLY')], string='PayFreq')
	payroll_periode	= fields.Many2one('hr.periode',string="Payroll Periode")
	category		= fields.Many2one('hr.periode.category',string="Categori Gaji", related="payroll_periode.category_id")

	periode_search	= fields.Char(string='Periode Gaji')

	ptkp_id			= fields.Many2one('hr.ptkp',string="PTKP")


	is_resign = fields.Boolean(
		string="Resign ?",
	)

	service_length = fields.Char(
		string="Length Of Services",
	)

	ptkp_id = fields.Many2one(
		'hr.ptkp',
		string="Tax Status"
	)

	allow_jht = fields.Monetary(
		'JHT Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_jkk = fields.Monetary(
		'JKK Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_jkm = fields.Monetary(
		'JKM Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_meal = fields.Monetary(
		'Meal Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_competency = fields.Monetary(
		'Competency Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_bpjs_pensiun = fields.Monetary(
		'BPJS Pensiun Perusahaan',
		currency_field="currency_id",
		default=0.0,
	)

	allow_bpjs_kesehatan = fields.Monetary(
		'BPJS Kesehatan Perusahaan',
		currency_field="currency_id",
		default=0.0,
	)

	allow_tor = fields.Monetary(
		'Tor Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_guaranteed_incentive = fields.Monetary(
		'Guaranteed Incentive',
		currency_field="currency_id",
		default=0.0,
	)

	allow_incentive = fields.Monetary(
		'Incentive',
		currency_field="currency_id",
		default=0.0,
	)

	allow_location = fields.Monetary(
		'Location Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_position = fields.Monetary(
		'Position Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_transport = fields.Monetary(
		'Transport Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_daily = fields.Monetary(
		'Daily Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_housing = fields.Monetary(
		'Housing Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_phone = fields.Monetary(
		'Handphone Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_performance = fields.Monetary(
		'Performance Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	travel_performance = fields.Monetary(
		'Travel Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	bonus = fields.Monetary(
		'Bonus',
		currency_field="currency_id",
		default=0.0,
	)

	car_allowance = fields.Monetary(
		'Car Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	allow_medical = fields.Monetary(
		'Medical Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_jht = fields.Monetary(
		'JHT Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_bpjs = fields.Monetary(
		'BPJS Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_pensiun = fields.Monetary(
		'Pensiun Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_koperasi = fields.Monetary(
		'Koperasi Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_kehadiran = fields.Monetary(
		'Presence Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_mess = fields.Monetary(
		'Mess Deduction',
		currency_field="currency_id",
		default=0.0,
	)

	tax_total = fields.Monetary(
		'Total Tax',
		currency_field="currency_id",
		default=0.0,
	)
	

	total_allowance = fields.Monetary(
		'Total Allowance',
		currency_field="currency_id",
		default=0.0,
	)

	total_deduction = fields.Monetary(
		'Total Deduction',
		currency_field="currency_id",
		default=0.0,
	)


	salary_netto = fields.Monetary(
		'Salary Netto',
		currency_field="currency_id",
		default=0.0,
	)

	adjustment = fields.Monetary(
		'Adjustment',
		currency_field="currency_id",
		default=0.0,
	)

	long_shift = fields.Monetary(
		'Long Shift',
		currency_field="currency_id",
		default=0.0,
	)

	overtime = fields.Monetary(
		'Overtime',
		currency_field="currency_id",
		default=0.0,
	)

	all_backup = fields.Monetary(
		'All Backup',
		currency_field="currency_id",
		default=0.0,
	)

	national_holiday = fields.Monetary(
		'Ins. National Daily',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_advanced = fields.Monetary(
		'Potongan Advanced',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_presence= fields.Monetary(
		'Potongan Kehadiran',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_shoes = fields.Monetary(
		'Uang Jaminan Sepatu',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_rapel = fields.Monetary(
		'Potongan Rapel',
		currency_field="currency_id",
		default=0.0,
	)

	allowance_rapel = fields.Monetary(
		'Allowance Rapel',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_lebih = fields.Monetary(
		'Potongan Lebih Bayar',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_training = fields.Monetary(
		'Potongan Jaminan Training',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_seragam = fields.Monetary(
		'Potongan Jaminan Seragam',
		currency_field="currency_id",
		default=0.0,
	)


	deduction_food = fields.Monetary(
		'Potongan Uang Makan',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_housing = fields.Monetary(
		'Potongan Asrama',
		currency_field="currency_id",
		default=0.0,
	)

	deduction_sec_guard = fields.Monetary(
		'Potongan Training Sec. Guard',
		currency_field="currency_id",
		default=0.0,
	)

	take_home_pay = fields.Monetary(
		'Take Home Pay',
		currency_field="currency_id",
		default=0.0,
	)

	pph21 = fields.Monetary(
		'Tax',
		currency_field="currency_id",
		default=0.0,
	)

	accumulation_pph21_year = fields.Monetary(
		'Tax Accumulative',
		currency_field="currency_id",
		default=0.0,
	)

	accumulation_netto_year = fields.Monetary(
		'Netto Accumulative',
		currency_field="currency_id",
		default=0.0,
	)

	allow_locationsm = fields.Monetary(
		'Location Allowance TSM',
		currency_field="currency_id",
		default=0.0,
	)


	terminated 			= fields.Boolean(string='Pensiun/mengundurkan Diri', default=False)
	work_days			= fields.Integer(string='hari Kerja Seharusnya', default=0)
	work_terminated		= fields.Integer(string='hari Kerja Pensiun/Mundur', default=0)

	contract_ids 		= fields.One2many('hr.payslip.contract', 'payslip_id', string='Contract List', readonly=True)

	total_hari_hadir 	= fields.Integer(string='Total Hari kehadiran', default=0)
	age					= fields.Integer(string='Age')

	# additional for report
	paydate				= fields.Date(string='Pay Date')
	bank_transfer		= fields.Many2one('res.partner.bank', string='Bank Transfer')
	bank_name			= fields.Char(string='Nama Bank')
	bank_owner			= fields.Char(string='Nama Pemilik')
	bank_number			= fields.Char(string='Nomor Rekening')

	tax            		= fields.Date(string = 'Tgl Pajak')
	attend_start 		= fields.Date(string='Attendance Start Date')
	attend_end			= fields.Date(string='Attendance End Date')

	generate_paydate	= fields.Date(string='For Salary Rule')

	method				= fields.Selection([('BANK','BANK'),('CASH','CASH')], string='Metode Bayar')

	line_ids2 			= fields.One2many('hr.payslip.line', 'slip_id', string='Payslip Lines', readonly=True,
		states={'draft': [('readonly', False)]}, domain=[('amount','>',0),('code','not in',['DATETOJOINDATE','DATETOJOINDATE','NEPRORATEPEMBAGI','ENDDATEDATETO','ENDDATEDATEFROM','DATEFROMJOINDATE','DATEFROMENDDATE','DATEENDJOINDATE','DATETOENDDATE','DATETODATEFROM','PRORATEJOINONPERIODE','TERMINATEONPERIOD','PRORATEJOINRESIGN2','PRORATETERMINONPERIOD','PRORATETERMINONPERIOD2','PRORATEJOINRESIGNWORK','PRORATEWORKDAYS','PRORATEJOINONPERIODEWORK','JOINONPERIODE','PRORATEJOINRESIGN','NOTPRORATE','JOINANDRESIGN','PRORATETERMINONPERIODWORK'])])


	# kasusnya adalah proportional lebih dari dua


	def compute_after_payslip(self):
		_logger = logging.getLogger(__name__)

		for rec in self:
			# find THP
			thp_line = rec.line_ids.filtered(lambda r: r.code == "NETTOPPH")
			rec.take_home_pay = thp_line.amount

			# find PPH 21
			pph_line = rec.line_ids.filtered(lambda r: r.code == "PPH21")
			rec.pph21 = pph_line.amount

 
	def compute_api_payslip2(self):
		_logger = logging.getLogger(__name__)

		for rec in self:
			employee_info = self.env['hr.employee'].sudo().search_read([('id','=',rec.employee_id.id)],['id','name','contract_id','address_id','address_home_id'])
			work_days_data = self.env['hr.payslip.worked_days'].search_read([('payslip_id','=', rec.id)])

			# everything will based on contract
			if rec.payslip_run_id.periode_id.id != False:
				structure_selected = self.env['hr.periode'].sudo().search([('category_id','=',rec.contract_id.employee_status2_id.id),('status_id','=',rec.employee_id.employee_status_id.id)])
				# ketemu periode, cari strukture
				struct_id_arr		= self.env['hr.payroll.structure'].sudo().search([('periode_id','=', structure_selected.id)])
				rec.struct_id    	= struct_id_arr.id
				rec.payroll_periode = struct_id_arr.periode_id.id

			rec.position_id 		= rec.contract_id.master_id.id
			rec.departement_id 		= rec.contract_id.department_id.id
			rec.location_id 		= rec.contract_id.work_location_id.id 
			rec.grade_id			= rec.contract_id.grade_id.id 
			rec.payfreq				= rec.employee_id.custom3
			rec.tax_location_id		= rec.contract_id.work_location_id.tax_location_id.id
			rec.area_id				= rec.contract_id.area_id.id

			if rec.contract_id.employee_status2_id.code == 'STAFF' or rec.contract_id.employee_status2_id.code == 'OP':
				rec.tax_type = 'local'
			else:
				rec.tax_type = 'fixed'

			rec.periode_search = rec.month+'-'+str(rec.year)

			rec.ptkp_id			= rec.employee_id.ptkp_id.id

			# PPH nggak bisa based disini, harus all dulu
			rec.accumulation_netto_year = 0
			rec.accumulation_pph21_year	= 0
			join_date 			= rec.employee_id.join_date

			today 				= date.today()
			age 				= relativedelta(today, join_date)

			rec.service_length	= str(age.years)+' tahun '+str(age.months)+' bulan'
			rec.province		= rec.contract_id.work_location_id.state_id.id
			rec.ump				= rec.contract_id.work_location_id.state_id.ump

			# calculate age based on 
			current_age 		= relativedelta(today, rec.employee_id.birthday)
			rec.age				= current_age.years

			rec.generate_paydate	= datetime.strptime("21"+rec.month+str(rec.year), "%d%m%Y").date()

			if len(employee_info) > 0:
				for emp in employee_info:
					# find contract type
					contract_type = rec.contract_id.contract_type_id

					payment_info = self.env['hr.employee.pembayaran'].sudo().search([('name','=',rec.employee_id.id),('category','=',rec.payslip_run_id.periode_id.id)])
					
					if len(payment_info) > 0:
						for binf in payment_info:
							if binf.method =='BANK':
								rec.method = 'BANK'
								rec.bank_transfer = binf.rekening.id

								rec.bank_name = binf.rekening.bank_id.name
								rec.bank_owner	= binf.rekening.acc_holder_name
								rec.bank_number	= binf.rekening.acc_number
							else:
								rec.method = 'CASH'

			contract_list 			= self.env['hr.contract'].sudo().search([('id','=', rec.contract_id.id)])
			termination_date 		= rec.employee_id.end_date

			active_days 		= []
			days_counter        = 0

			if rec.employee_id.custom3 == 'DAILY':
				rec.work_days = rec.employee_id.divisi.daily_work_days
			else:
				rec.work_days = rec.employee_id.divisi.monthly_work_days

			rec.total_hari_hadir = 0
			if len(work_days_data) > 0:
				if rec.employee_id.custom3 == 'DAILY':
					for work_day in work_days_data:
						if work_day['code'] == 'WORK100':
							rec.total_hari_hadir = rec.total_hari_hadir + work_day['number_of_hours']
				else:
					for work_day in work_days_data:
						if work_day['code'] == 'WORK100':
							rec.total_hari_hadir = rec.total_hari_hadir + work_day['number_of_days']
			else:
				rec.total_hari_hadir = 0




	def compute_api_payslip(self):
		_logger = logging.getLogger(__name__)
		# kasusnya adalah work days data harus masuk dulu sebelum payslip, tapi dia langsung disini
		for rec in self:
			employee_info = self.env['hr.employee'].sudo().search_read([('id','=',rec.employee_id.id)],['id','name','contract_id','address_id','address_home_id'])
	
			work_days_data = self.env['hr.payslip.worked_days'].search_read([('payslip_id','=', rec.id)])
			
			# struktur yang dipakai tergantung tipe
			#if rec.payslip_run_id.struktur_id.id != False:
			#	rec.struct_id    = rec.payslip_run_id.struktur_id.id
			#else:
			#	rec.struct_id 	= rec.contract_id.struct_id.id
			
			if rec.payslip_run_id.periode_id.id != False:
				structure_selected = self.env['hr.periode'].sudo().search([('category_id','=',rec.payslip_run_id.periode_id.id),('status_id','=',rec.employee_id.employee_status_id.id)])
				# ketemu periode, cari strukture
				struct_id_arr		= self.env['hr.payroll.structure'].sudo().search([('periode_id','=', structure_selected.id)])
				rec.struct_id    	= struct_id_arr.id
				rec.payroll_periode = struct_id_arr.periode_id.id
			

			rec.position_id 	= rec.employee_id.master_id.id
			rec.departement_id 	= rec.employee_id.department_id.id
			rec.location_id 	= rec.employee_id.work_location_id.id 
			rec.grade_id		= rec.employee_id.grade_id.id 
			rec.payfreq			= rec.employee_id.custom3
			rec.tax_location_id	= rec.employee_id.work_location_id.tax_location_id.id
			rec.area_id			= rec.employee_id.area.id

			if rec.employee_id.employee_status_id.code == 'STAFF' or rec.employee_id.employee_status_id.code == 'OP':
				rec.tax_type = 'local'
			else:
				rec.tax_type = 'fixed'

			rec.periode_search = rec.month+'-'+str(rec.year)
			rec.ptkp_id			= rec.employee_id.ptkp_id.id


			

			# get accumulated PPH21 and netto from other month same year fiscal
			all_payslip 		= self.env['hr.payslip'].sudo().search([('year','=', rec.year),('employee_id','=',rec.employee_id.id),('state','=','done'),('id','!=', rec.id)])

			total_netto 		= 0
			total_pph21			= 0

			if len(all_payslip) > 0:
				for allp in all_payslip:
					if allp.month != False and allp.month < self.month:
						total_netto = total_netto + allp.take_home_pay
						total_pph21 = total_pph21 + allp.pph21

			rec.accumulation_netto_year = total_netto
			rec.accumulation_pph21_year	= total_pph21

			join_date 			= rec.employee_id.join_date

			today 				= date.today()
			age 				= relativedelta(today, join_date)

			rec.service_length	= str(age.years)+' tahun '+str(age.months)+' bulan'
			#rec.province		= rec.employee_id.work_location_id.address_id.state_id.id
			rec.province		= rec.employee_id.work_location_id.state_id.id
			rec.ump				= rec.employee_id.work_location_id.state_id.ump

			# calculate age based on 
			current_age 		= relativedelta(today, rec.employee_id.birthday)

			rec.age					= current_age.years
			rec.generate_paydate	= datetime.strptime("21"+rec.month+str(rec.year), "%d%m%Y").date()
			




			contract_data = {}
			#find salary based on contract 
			if len(employee_info) > 0:
				for emp in employee_info:
					contract_info = self.env['hr.contract'].sudo().search_read([('id','=',emp['contract_id'][0])])

					if len(contract_info) > 0:
						for contract in contract_info:
							contract_data = contract

							# find contract type
							contract_type_info  = self.env['hr.contract.type'].sudo().search_read([('id','=', contract_data['contract_type_id'][0])])
							
							if len(contract_type_info) > 0:
								for typein in contract_type_info:
									contract_type = typein

					# find bank account, based on type will be different
					payment_info = self.env['hr.employee.pembayaran'].sudo().search([('name','=',rec.employee_id.id),('category','=',rec.payslip_run_id.periode_id.id)])
					
					if len(payment_info) > 0:
						for binf in payment_info:
							if binf.method =='BANK':
								rec.method = 'BANK'
								rec.bank_transfer = binf.rekening.id

								rec.bank_name = binf.rekening.bank_id.name
								rec.bank_owner	= binf.rekening.acc_holder_name
								rec.bank_number	= binf.rekening.acc_number
							else:
								rec.method = 'CASH'
								

					#bank_info = self.env['res.partner.bank'].sudo().search([('partner_id','=', emp['address_home_id'][0]),('allow_out_payment','=', True)])
					#raise UserError(str(emp['address_id'][0]))
					#if len(bank_info) > 0:
					#	for binf in bank_info:
					#		rec.bank_transfer = binf.id

					#		rec.bank_name = binf.bank_id.name
					#		rec.bank_owner	= binf.acc_holder_name
					#		rec.bank_number	= binf.acc_number


			
			# kasusnya adalah absensi akan pengaruh gimana ?
			# untuk bulanan pengaruhnya adalah pada kontrak
			contract_list = self.env['hr.contract'].sudo().search(['&',('state','in',['open','close']),'&',('employee_id','=', rec.employee_id.id),'|',('state','=','open'),'|','&',('date_end','>=', rec.date_from),('date_end','<=', rec.date_to),'|','&',('date_start','>=', rec.date_from),('date_start','<=', rec.date_to),'&',('date_start','<=', rec.date_from),('date_end','>=', rec.date_to) ], order="date_start asc")

			# check apakah termination atau tidak
			termination_date = rec.employee_id.end_date

			active_days 		= []
			days_counter        = 0

			# work days will be based on contract type, only one contract type allowed

			
			#for contr in contract_list:
			#	calendar_ids   = contr.resource_calendar_id.attendance_ids

			#	if len(calendar_ids) > 0:
			#		for calendar in calendar_ids:
			#			if calendar.dayofweek not in active_days:
			#				active_days.append(calendar.dayofweek)

			#	if contr.date_start >= rec.date_from:
			#		start_date = contr.date_start
			#	else:
			#		start_date = rec.date_from

			#	if contr.date_end <= rec.date_to:
			#		end_date = contr.date_end
			#	else:
			#		end_date = rec.date_to

			#	current_days     	    = start_date
			#	calculated_is_end 		= False

			#	while calculated_is_end == False:
			#		if current_days > end_date:
			#			calculated_is_end = True
			#			break
							
			#		calculated_weekday = current_days.weekday()
							
			#		if str(calculated_weekday) in active_days:
			#			days_counter = days_counter + 1
								
			#		current_days = current_days + timedelta(days=1)

			#if contract_type['salary_type'] == 'daily':
			
			if rec.employee_id.custom3 == 'DAILY':
				rec.work_days = rec.employee_id.divisi.daily_work_days
			else:
				rec.work_days = rec.employee_id.divisi.monthly_work_days

			rec.total_hari_hadir = 0
			if len(work_days_data) > 0:
				if rec.employee_id.custom3 == 'DAILY':
					for work_day in work_days_data:
						if work_day['code'] == 'WORK100':
							rec.total_hari_hadir = rec.total_hari_hadir + work_day['number_of_hours']
				else:
					for work_day in work_days_data:
						if work_day['code'] == 'WORK100':
							rec.total_hari_hadir = rec.total_hari_hadir + work_day['number_of_days']
			else:
				rec.total_hari_hadir = 0


			# inserting work days for every contract, work days will be based on join date, termination date, and payslip periode
			if termination_date != False and termination_date >= rec.date_from and termination_date < rec.date_to:
				# hitung hari kerja terminate, langsung aja dari currenct contract
				rec.terminated = True
			else:
				rec.terminated = False
			

			if len(contract_list) == 1:
				# hanya 1 kontrak maka langsung
				item_contract = []
				item_contract.append([5, 0, False])

				for contr in contract_list:
					item_contract.append([0, 0, {'name': contract_data['id'], 'work_days' : rec.work_days}])

				rec.write({'contract_ids' : item_contract})
			else:
				for contr in contract_list:
					work_days_contract = 0
					# tentukan kontrak posisinya start >= date_from dan end <= date_to
					# artinya murni berada ditengah periode
					if contr.date_start >= rec.date_from and contr.date_end <= rec.date_to:
						# ditengah kontrak
						if rec.terminated == False:
							# nilai hari kontrak adalah hari kontrak akhir dikruangi awal
							if rec.work_days < 30:
								work_days_contract2 = contr.date_end - contr.date_start
								work_days_contract  = work_days_contract2.days + 1
							else:
								halo = 3
						else:
							# terminate, jika terminate pada range
							if termination_date >= contr.date_start and termination_date < contr.date_end:
								if rec.work_days < 30:
									work_days_contract2 = termination_date - contr.date_start
									work_days_contract  = work_days_contract2.days
								else:
									halo = 4
							else:
								# terminate mungkin bulan depan, atau kontrak berikutnya
								if rec.work_days < 30:
									work_days_contract2 = contr.date_end - contr.date_start
									work_days_contract  = work_days_contract2.days + 1
								else:
									halo = 5
					# kontrak berselisih dengan periode
					elif contr.start_date < rec.date_from and contr.date_end <= rec.date_to:
						halo = 2
					else:
						halo = 1 



			if termination_date != False and termination_date >= rec.date_from and termination_date < rec.date_to:
				# hitung hari kerja terminate, langsung aja dari currenct contract
				rec.terminated = True
				
				if rec.employee_id.custom3 == 'MONTHLY':
					if contr.date_start >= rec.date_from:
						start_date = contr.date_start
					else:
						start_date = rec.date_from

					if rec.work_days < 30:
						end_date = termination_date

						calendar_ids   = rec.contract_id.resource_calendar_id.attendance_ids

						if len(calendar_ids) > 0:
							for calendar in calendar_ids:
								if calendar.dayofweek not in active_days:
									active_days.append(calendar.dayofweek)

						current_days     	    = start_date
						calculated_is_end 		= False

						while calculated_is_end == False:
							if current_days > end_date:
								calculated_is_end = True
								break
									
							calculated_weekday = current_days.weekday()
									
							if str(calculated_weekday) in active_days:
								days_counter = days_counter + 1
										
							current_days = current_days + timedelta(days=1)
					else:
						# maks 30 maka hari kerja dihitung adalah langsung pengurang
						days_counter2 = termination_date - start_date
						days_counter  = days_counter2.days + 1

					rec.work_terminated = days_counter
				else:
					rec.work_terminated = 0
			else:
				# hari kerja normalnya berapa
				rec.terminated = False
				

			if len(contract_list) == 1:
				# kontrak hanya 1
				if len(work_days_data) > 0:
					for work_day in work_days_data:
						if work_day['code'] == 'WORK100':
							#jika kontrak harian
							if rec.employee_id.custom3 == 'DAILY':
								#dikali jumlah hari
								rec.salary 	= contract_data['wage']*work_day['number_of_days']
							else:
								# dikali langsung
								rec.salary 	= contract_data['wage']

								if rec.terminated:
									rec.salary = rec.salary*(rec.work_terminated/rec.work_days)
				else:
					if rec.employee_id.custom3 == 'DAILY':
						rec.salary = 0
					else:
						# ada presensi atau tidak ada presensi gaji tetap
						rec.salary 	= contract_data['wage']

						if rec.terminated:
							rec.salary = rec.salary*(rec.work_terminated/rec.work_days)

				# kasus tunjangan lainnya gimana ?
				if rec.allow_meal <= 0:
					rec.allow_meal = contract_data['meal_allowance']


				
			else:
				# banyak kontrak, pada kasus bulanan, pembagiannya adalah berdasar hari kerja, bukan absen
				# pada bulanan menggunakan absesn
				rec.salary = 0 
				for contr in contract_list:
					if rec.employee_id.custom3 == 'DAILY':
						w_days = rec.worked_days_line_ids.filtered(lambda r: r.contract_id == contr.id)

						if len(w_days) > 0:
							for wday in w_days:
								rec.salary 	= rec.salary + (contr.wage*wday.number_of_hours)
					else:
						# bulanan
						if rec.terminated == True:
							if termination_date < contr.date_start:
									continue

							calendar_ids   	= contr.resource_calendar_id.attendance_ids
							days_counter 	= 0
							if len(calendar_ids) > 0:
								for calendar in calendar_ids:
									if calendar.dayofweek not in active_days:
										active_days.append(calendar.dayofweek)

										if contr.date_start >= rec.date_from:
											start_date = contr.date_start
										else:
											start_date = rec.date_from

										if contr.date_end <= termination_date:
											end_date = contr.date_end
										else:
											end_date = termination_date

										current_days     	    = start_date
										calculated_is_end 		= False

										while calculated_is_end == False:
											if current_days > end_date:
												calculated_is_end = True
												break
													
											calculated_weekday = current_days.weekday()
													
											if str(calculated_weekday) in active_days:
												days_counter = days_counter + 1
														
											current_days = current_days + timedelta(days=1)

							rec.salary = rec.salary + ((days_counter/rec.work_days)*contr.wage)
						else:
							calendar_ids   	= contr.resource_calendar_id.attendance_ids
							days_counter 	= 0
							if len(calendar_ids) > 0:
								for calendar in calendar_ids:
									if calendar.dayofweek not in active_days:
										active_days.append(calendar.dayofweek)

										if contr.date_start >= rec.date_from:
											start_date = contr.date_start
										else:
											start_date = rec.date_from

										if contr.date_end <= rec.date_to:
											end_date = contr.date_end
										else:
											end_date = rec.date_to

										current_days     	    = start_date
										calculated_is_end 		= False

										while calculated_is_end == False:
											if current_days > end_date:
												calculated_is_end = True
												break
													
											calculated_weekday = current_days.weekday()
													
											if str(calculated_weekday) in active_days:
												days_counter = days_counter + 1
														
											current_days = current_days + timedelta(days=1)

							rec.salary = rec.salary + ((days_counter/rec.work_days)*contr.wage)
							

			# internal memo
			internal_memo_list = self.env['internal.memo.employee'].sudo().search([('memo_id.date_memo','>=',self.date_from),('memo_id.date_memo','<=',self.date_to),('employee_id','<=',self.employee_id.id)])
			
			#_logger.error('TEST MEMO')
			#_logger.error(internal_memo_list)


			rec.adjustment 			= 0
			rec.all_backup 			= 0
			rec.national_holiday 	= 0
			rec.overtime			= 0
			rec.deduction_seragam	= 0
			rec.deduction_training 	= 0
			rec.long_shift			= 0
			rec.deduction_shoes		= 0
			rec.deduction_lebih		= 0
			rec.deduction_food		= 0
			rec.deduction_housing	= 0
			rec.deduction_sec_guard = 0
			rec.deduction_rapel  	= 0
			rec.deduction_kehadiran = 0
			rec.allowance_rapel = 0
			rec.car_allowance = 0
			rec.bonus = 0
			rec.travel_performance = 0

			for internal in internal_memo_list:
				_logger.error(internal.memo_id.type_id.code)
				if internal.memo_id.type_id.code == 'ADJUSTPLUS':
					rec.adjustment = rec.adjustment + internal.total_amount
				elif internal.memo_id.type_id.code == 'BACKUP':
					rec.all_backup = rec.all_backup + internal.total_amount
				elif internal.memo_id.type_id.code == 'ARAPEL':
					rec.allowance_rapel = rec.allowance_rapel + internal.total_amount
				elif internal.memo_id.type_id.code == 'NASIONAL':
					rec.national_holiday = rec.national_holiday + internal.total_amount
				elif internal.memo_id.type_id.code == 'OVERTIME':
					rec.overtime = rec.overtime + internal.total_amount
				elif internal.memo_id.type_id.code == 'SERAGAM':
					rec.deduction_seragam = rec.deduction_seragam + internal.total_amount
				elif internal.memo_id.type_id.code == 'TRAINING':
					rec.deduction_training = rec.deduction_training + internal.total_amount
				# no long shift internal memo
				#elif internal.memo_id.type_id.code == 'SHIFT':
				#	rec.long_shift = rec.long_shift + internal.total_amount
				elif internal.memo_id.type_id.code == 'SEPATU':
					rec.deduction_shoes = rec.deduction_shoes + internal.total_amount
				elif internal.memo_id.type_id.code == 'LEBIHBAYAR':
					rec.deduction_lebih = rec.deduction_lebih + internal.total_amount
				elif internal.memo_id.type_id.code == 'MAKAN':
					rec.deduction_food = rec.deduction_food + internal.total_amount
				elif internal.memo_id.type_id.code == 'ASRAMA':
					rec.deduction_housing = rec.deduction_housing + internal.total_amount
				elif internal.memo_id.type_id.code == 'SECGUARD':
					rec.deduction_sec_guard = rec.deduction_sec_guard + internal.total_amount
				elif internal.memo_id.type_id.code == 'RAPEL':
					rec.deduction_rapel = rec.deduction_rapel + internal.total_amount
				elif internal.memo_id.type_id.code == 'HADIR':
					rec.deduction_kehadiran = rec.deduction_kehadiran + internal.total_amount
				elif internal.memo_id.type_id.code == 'TRAVEL':
					rec.travel_performance = rec.travel_performance + internal.total_amount
				elif internal.memo_id.type_id.code == 'BONUS':
					rec.bonus = rec.bonus + internal.total_amount
				elif internal.memo_id.type_id.code == 'CAR':
					rec.car_allowance = rec.car_allowance + internal.total_amount

			# default allowance based on contract if null
			if rec.allow_transport <= 0:
				rec.allow_transport = contract_data['travel_allowance']

			#if rec.allow_meal <= 0:
			#	rec.allow_meal = contract_data['meal_allowance']

			if rec.allow_performance <= 0:
				rec.allow_performance = contract_data['performance_allowance']

			if rec.allow_incentive <= 0:
				rec.allow_incentive = contract_data['allow_incentive']

			if rec.allow_competency <= 0:
				rec.allow_competency = contract_data['competency_allowance']

			if rec.allow_location <= 0:
				rec.allow_location = contract_data['location_allowance']

			if rec.allow_position <= 0:
				rec.allow_position = contract_data['position_allowance']

			if rec.allow_daily <= 0:
				rec.allow_daily = contract_data['daily_allowance']

			if rec.allow_housing <= 0:
				rec.allow_housing = contract_data['housing_allowance']

			if rec.allow_phone <= 0:
				rec.allow_phone = contract_data['handphone_allowance']

			if rec.allow_locationsm <= 0:
				rec.allow_locationsm = contract_data['allow_locationsm']

			
			if rec.allow_medical <= 0:
				rec.allow_medical = contract_data['medical_allowance']

			if rec.allow_tor <= 0:
				rec.allow_tor = contract_data['tor_allowance']

			if rec.allow_guaranteed_incentive <= 0:
				rec.allow_guaranteed_incentive = contract_data['guarantine_allowance']

			if rec.long_shift <= 0:
				rec.long_shift = contract_data['shift_allowance']


	def compute_sheet(self):
		for payslip in self:
			if payslip.parent_id.id == False:
				payslip.compute_api_payslip()
				number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
				# delete old payslip lines
				payslip.line_ids.unlink()
				# set the list of contract for which the rules have to be applied
				# if we don't give the contract, then the rules to apply should be for all current contracts of the employee
				contract_ids = payslip.contract_id.ids or \
					self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
				
				
				# the problem there will be override value and it will get problematic
				# because it's reinsert data, if it's delete and reinsert data it will be problematic

				if not contract_ids:
					raise ValidationError(_("No running contract found for the employee: %s or no contract in the given period" % payslip.employee_id.name))
				lines = [(0, 0, line) for line in self._get_payslip_lines(contract_ids, payslip.id)]
				payslip.write({'line_ids': lines, 'number': number})

				payslip.compute_after_payslip()

				# delete and regenerate

				for chi in payslip.child_ids:
					chi.unlink()

				for child_id in payslip.contract_ids:
					# worked days line by line
					worked_lines 		= []
					contract_ids_new 	= []

					for wo_id in payslip.worked_days_line_ids:
						if child_id.name.id == wo_id.contract_id.id:
							worked_lines.append(
									(
										0,
										0,
										{
											'name'				: _("Hari kerja"),
											'sequence'			: 1,
											'code'				: 'WORK100',
											'number_of_days'	: wo_id.number_of_days,
											'number_of_hours'	: wo_id.number_of_hours,
											'contract_id'		: wo_id.contract_id.id
										}
							))

							# work days based on divisi
							if wo_id.contract_id.employee_id.custom3 == 'DAILY':
								work_days_new = wo_id.contract_id.employee_id.divisi.daily_work_days
							else:
								work_days_new = wo_id.contract_id.employee_id.divisi.monthly_work_days
								

							contract_ids_new.append((
								0,
								0,
								{
									'name'		: wo_id.contract_id.id,
									'work_days'	: work_days_new
								}
							))




					# date from date to based on contract
					if child_id.name.date_start < payslip.date_from:
						date_from = payslip.date_from
					else:
						date_from = child_id.date_start

					if child_id.name.date_end == False or child_id.name.date_end > payslip.date_to:
						date_to = payslip.date_to
					else:
						date_to	= child_id.name.date_end

					# untuk presensi by default ikut parent aja
					# hilangkan dulu ya split cost nya
					#res2 = {
					#	'employee_id'           : payslip.employee_id.id,
					#	'name'                  : child_id.name.employee_id.nip +' '+child_id.name.employee_id.name+' '+child_id.name.master_id.name + ' '+child_id.name.area_id.name,
					#	'struct_id'             : payslip.struct_id.id,
					#	'contract_id'           : child_id.name.id,
					#	'contract_ids'          : contract_ids_new,
					#	'payslip_run_id'        : payslip.payslip_run_id.id,
					#	'input_line_ids'        : False,
					#	'worked_days_line_ids'  : worked_lines,
					#	'date_from'             : date_from,
					#	'date_to'               : date_to,
					#	'credit_note'           : payslip.credit_note,
					#	'company_id'            : payslip.employee_id.company_id.id,
					#	'year'                  : payslip.year,
					#	'month'                 : payslip.month,
					#	'attend_start'          : payslip.attend_start,
					#	'attend_end'            : payslip.attend_end,
					#	'tax'                   : payslip.tax,
					#	'paydate'               : payslip.paydate,
					#	'parent_id'             : payslip.id

					#}
					
					#res2_result = self.env['hr.payslip'].create(res2)
					#res2_result.compute_sheet()

			#else:
				# kasus child
			#	payslip.compute_api_payslip2()

			#	number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
			#	payslip.line_ids.unlink()

		return True
	
	def compute_sheet_update(self):
		_logger = logging.getLogger(__name__)

		for payslip in self:
			payslip.compute_api_payslip()
			number = payslip.number or self.env['ir.sequence'].next_by_code('salary.slip')
			# delete old payslip lines
			previous_data = self.env['hr.payslip.line'].sudo().search([('slip_id','=',payslip.id)])
			
			filtered_data = previous_data.filtered(lambda r: r.code == 'MTH_STAFF_BASIC')
			#_logger.error('TEST LINE')
			#_logger.error(filtered_data.is_override)
			#_logger.error(filtered_data.amount_correction)

			
			#payslip.line_ids.unlink()
			# set the list of contract for which the rules have to be applied
			# if we don't give the contract, then the rules to apply should be for all current contracts of the employee
			contract_ids = payslip.contract_id.ids or \
				self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
			
			
			# the problem there will be override value and it will get problematic
			# because it's reinsert data, if it's delete and reinsert data it will be problematic

			if not contract_ids:
				raise ValidationError(_("No running contract found for the employee: %s or no contract in the given period" % payslip.employee_id.name))
			
			_logger = logging.getLogger(__name__)

			#for line in self._get_payslip_lines_upgrade(contract_ids, payslip.id, previous_data):
			

			lines = [(1, line['id'], line) for line in self._get_payslip_lines_upgrade(contract_ids, payslip.id, previous_data)]
			#_logger.error('LINES DATA')
			#_logger.error(lines)
			payslip.write({'line_ids': lines, 'number': number})

			payslip.compute_after_payslip()
		return True
	
	

	

	def compute_override(self, code, override_value, is_override):
		# find rule to override
		halo = 1

		# generate categories
		

		#baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
		
		
		#selected_rule = self.env['hr.salary.rule'].sudo().search([('code','=', rule)])
		
		#localdict['result'] = None
		#localdict['result_qty'] = 1.0
		#localdict['result_rate'] = 100
		#check if the rule can be applied
		#if rule._satisfy_condition(localdict):
			#compute the amount of the rule
		#	amount, qty, rate = selected_rule._compute_rule(localdict)


	
	def onchange_periode_id(self, month, year, employee_id, periode_id):
		employee = self.env['hr.employee'].browse(employee_id)
		
		# kasusnya disini adalah sesuai dengan MTH masing-masing
		# di replace, kasus salary range, tax range, attendance range based on hr_periode, adan divisi
		periode_info = self.env['hr.periode'].sudo().search([('category_id','=', periode_id),('status_id','=',employee.employee_status_id.id)])
		divisi_info	 = self.env['divisi'].sudo().search([('id','=',employee.divisi.id)])

		struct_id 		= False
		tanggal_awal 	= False
		tanggal_akhir	= False

		tanggal_attend_awal = False	
		tanggal_attend_akhir = False



		if len(periode_info) > 0:
			for per in periode_info:
				# struktur dari periode yang di pilih
				struktur_info = self.env['hr.payroll.structure'].sudo().search([('periode_id','=',per.id)])

				if len(struktur_info) > 0:
					for stru in struktur_info:
						struct_id = stru.id


				# there is setting on hr_periode
				if per.salarystartdate == False:
					# based on division
					if len(divisi_info) > 0:
						for divi in divisi_info:
							if divi.periode == 'periode':
								# periode dimulai start dan end
								bulan_angka = int(month)

								if bulan_angka == 1:
									bulan_sebelum = 12
									tahun_sebelum = year - 1
								else:
									bulan_sebelum = bulan_angka - 1
									tahun_sebelum = year

								# to date
								tanggal_awal = datetime.strptime(str(divi.start).zfill(2)+str(bulan_sebelum).zfill(2)+str(tahun_sebelum), '%d%m%Y').date()
								tanggal_akhir = datetime.strptime(str(divi.end).zfill(2)+month+str(year), '%d%m%Y').date()

							else:
								# period will be based on start and end month
								if month == '01':
									start_periode = 1
									end_periode = 31
								elif month == '02':
									quotient, is_kabisat = divmod(year,4)
									start_periode = 1

									if is_kabisat==0:
										end_periode = 29
									else:
										end_periode = 28
								elif month == '03':
									start_periode = 1
									end_periode = 31
								elif month == '04':
									start_periode = 1
									end_periode = 30
								elif month == '05':
									start_periode = 1
									end_periode = 31
								elif month == '06':
									start_periode = 1
									end_periode = 30
								elif month == '07':
									start_periode = 1
									end_periode = 31
								elif month == '08':
									start_periode = 1
									end_periode = 31
								elif month == '09':
									start_periode = 1
									end_periode = 30
								elif month == '10':
									start_periode = 1
									end_periode = 31
								elif month == '11':
									start_periode = 1
									end_periode = 30
								elif month == '12':
									start_periode = 1
									end_periode = 31

								tanggal_awal = datetime.strptime(str(start_periode).zfill(2)+month+str(year), '%d%m%Y').date()
								tanggal_akhir = datetime.strptime(str(end_periode).zfill(2)+month+str(year), '%d%m%Y').date()

				else:
					# obveeride division
					tanggal_awal 	= per.salarystartdate
					tanggal_akhir	= per.salaryenddate

				# tanggal absensi
				if per.attendstartdate == False:
					# based on division
					if len(divisi_info) > 0:
						for divi in divisi_info:
							if divi.periode_attend == 'periode':
								# periode dimulai start dan end
								bulan_angka = int(month)

								if bulan_angka == 1:
									bulan_sebelum = 12
									tahun_sebelum = year - 1
								else:
									bulan_sebelum = bulan_angka - 1
									tahun_sebelum = year

								# to date
								tanggal_attend_awal = datetime.strptime(str(divi.attend_start).zfill(2)+str(bulan_sebelum).zfill(2)+str(tahun_sebelum), '%d%m%Y').date()
								tanggal_attend_akhir = datetime.strptime(str(divi.attend_end).zfill(2)+month+str(year), '%d%m%Y').date()

							else:
								# period will be based on start and end month
								if month == '01':
									start_periode = 1
									end_periode = 31
								elif month == '02':
									quotient, is_kabisat = divmod(year,4)
									start_periode = 1

									if is_kabisat==0:
										end_periode = 29
									else:
										end_periode = 28
								elif month == '03':
									start_periode = 1
									end_periode = 31
								elif month == '04':
									start_periode = 1
									end_periode = 30
								elif month == '05':
									start_periode = 1
									end_periode = 31
								elif month == '06':
									start_periode = 1
									end_periode = 30
								elif month == '07':
									start_periode = 1
									end_periode = 31
								elif month == '08':
									start_periode = 1
									end_periode = 31
								elif month == '09':
									start_periode = 1
									end_periode = 30
								elif month == '10':
									start_periode = 1
									end_periode = 31
								elif month == '11':
									start_periode = 1
									end_periode = 30
								elif month == '12':
									start_periode = 1
									end_periode = 31

								tanggal_attend_awal = datetime.strptime(str(start_periode).zfill(2)+month+str(year), '%d%m%Y').date()
								tanggal_attend_akhir = datetime.strptime(str(end_periode).zfill(2)+month+str(year), '%d%m%Y').date()

				else:
					# obveeride division
					tanggal_attend_awal 	= per.attendstartdate
					tanggal_attend_akhir	= per.attendenddate


				#raise UserError(str(tanggal_awal)+' '+str(tanggal_akhir))
				if per.taxdate == False:
					if len(divisi_info) > 0:
						for divi in divisi_info:
							if divi.periode_tax == 'periode':
								tanggal_tax = datetime.strptime(str(divi.tax).zfill(2)+month+str(year), '%d%m%Y').date()
							else:
								# period will be based on start and end month
								if month == '01':
									start_periode = 1
									end_periode = 31
								elif month == '02':
									quotient, is_kabisat = divmod(year,4)
									start_periode = 1

									if is_kabisat==0:
										end_periode = 29
									else:
										end_periode = 28
								elif month == '03':
									start_periode = 1
									end_periode = 31
								elif month == '04':
									start_periode = 1
									end_periode = 30
								elif month == '05':
									start_periode = 1
									end_periode = 31
								elif month == '06':
									start_periode = 1
									end_periode = 30
								elif month == '07':
									start_periode = 1
									end_periode = 31
								elif month == '08':
									start_periode = 1
									end_periode = 31
								elif month == '09':
									start_periode = 1
									end_periode = 30
								elif month == '10':
									start_periode = 1
									end_periode = 31
								elif month == '11':
									start_periode = 1
									end_periode = 30
								elif month == '12':
									start_periode = 1
									end_periode = 31

								tanggal_tax = datetime.strptime(str(end_periode).zfill(2)+month+str(year), '%d%m%Y').date()
				else:
					tanggal_tax = per.taxdate
		

				if per.paydate == False:
					# based on last salary date
					paydate = tanggal_akhir
				else:
					paydate = per.paydate
		

		res = {
			'value': {
				'year'			: year,
				'month'			: month,
				'contract_id'	: employee.contract_id.id,
				#'struct_id'		: employee.contract_id.contract_type_id.salary_structure.id,
				'struct_id'		: struct_id,
				'start_periode'	: employee.contract_id.contract_type_id.periode.start,
				'end_periode'	: employee.contract_id.contract_type_id.periode.end,
				'model_periode'	: employee.contract_id.contract_type_id.periode.periode,
				'date_from'		: tanggal_awal,
				'date_to'		: tanggal_akhir,
				'attend_start'	: tanggal_attend_awal,
				'attend_end'	: tanggal_attend_akhir,
				'tax'			: tanggal_tax,
				'paydate'		: paydate		
			}
		}

		return res


	# nanti dulu kalau bukan lewat batch
	@api.onchange('month', 'year')
	def onchange_periode(self):
		if self.month != False and self.year != False:
			if self.employee_id.id != False:
				# calculate periode by master
				self.contract_id = self.employee_id.contract_id.id
				self.struct_id   = self.employee_id.contract_id.contract_type_id.salary_structure

				start_periode    = self.employee_id.contract_id.contract_type_id.periode.start
				end_periode      = self.employee_id.contract_id.contract_type_id.periode.end
				model_periode	 = self.employee_id.contract_id.contract_type_id.periode.periode




				if model_periode == 'periode':
					# periode dimulai start dan end
					bulan_angka = int(self.month)

					if bulan_angka == 1:
						bulan_sebelum = 12
						tahun_sebelum = self.year - 1
					else:
						bulan_sebelum = bulan_angka - 1
						tahun_sebelum = self.year

					# to date
					tanggal_awal = datetime.strptime(str(start_periode).zfill(2)+str(bulan_sebelum).zfill(2)+str(tahun_sebelum), '%d%m%Y').date()
					tanggal_akhir = datetime.strptime(str(end_periode).zfill(2)+self.month+str(self.year), '%d%m%Y').date()

					self.date_from = tanggal_awal
					self.date_to = tanggal_akhir
				else:
					# period will be based on start and end month
					if self.month == '01':
						start_periode = 1
						end_periode = 31
					elif self.month == '02':
						quotient, is_kabisat = divmod(self.year,4)
						start_periode = 1

						if is_kabisat==0:
							end_periode = 29
						else:
							end_periode = 28
					elif self.month == '03':
						start_periode = 1
						end_periode = 31
					elif self.month == '04':
						start_periode = 1
						end_periode = 30
					elif self.month == '05':
						start_periode = 1
						end_periode = 31
					elif self.month == '06':
						start_periode = 1
						end_periode = 30
					elif self.month == '07':
						start_periode = 1
						end_periode = 31
					elif self.month == '08':
						start_periode = 1
						end_periode = 31
					elif self.month == '09':
						start_periode = 1
						end_periode = 30
					elif self.month == '10':
						start_periode = 1
						end_periode = 31
					elif self.month == '11':
						start_periode = 1
						end_periode = 30
					elif self.month == '12':
						start_periode = 1
						end_periode = 31

					tanggal_awal = datetime.strptime(str(start_periode).zfill(2)+self.month+str(self.year), '%d%m%Y').date()
					tanggal_akhir = datetime.strptime(str(end_periode).zfill(2)+self.month+str(self.year), '%d%m%Y').date()

					self.date_from = tanggal_awal
					self.date_to = tanggal_akhir
					
					

					

					
					#raise UserError(str(start_periode)+' '+str(end_periode))
			
		return
	
	def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
		#defaults
		res = {
			'value': {
				'line_ids': [],
				#delete old input lines
				'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
				#delete old worked days lines
				'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
				#'details_by_salary_head':[], TODO put me back
				'name': '',
				'contract_id': False,
				'struct_id': False,
			}
		}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
		employee = self.env['hr.employee'].browse(employee_id)
		locale = self.env.context.get('lang') or 'en_US'

		slip_name = employee.nip +' '+employee.name+' '+employee.master_id.name + ' '+employee.area.name


		res['value'].update({
			'name': slip_name,
			'company_id': employee.company_id.id,
		})

		

		if not self.env.context.get('contract'):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(employee, date_from, date_to)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(employee, date_from, date_to)

		if not contract_ids:
			return res
		contract = self.env['hr.contract'].browse(contract_ids[0])
		res['value'].update({
			'contract_id': contract.id
		})
		struct = contract.struct_id
		if not struct:
			return res
		res['value'].update({
			'struct_id': struct.id,
		})
		#computation of the salary input
		contracts = self.env['hr.contract'].browse(contract_ids)
		worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
		input_line_ids = self.get_inputs(contracts, date_from, date_to)
		res['value'].update({
			'worked_days_line_ids': worked_days_line_ids,
			'input_line_ids': input_line_ids,
		})
		return res
	
	def onchange_employee_id2(self, date_from, date_to, attend_from, attend_to, employee_id=False, contract_id=False):
		#defaults
		res = {
			'value': {
				'line_ids': [],
				#delete old input lines
				'input_line_ids': [(2, x,) for x in self.input_line_ids.ids],
				#delete old worked days lines
				'worked_days_line_ids': [(2, x,) for x in self.worked_days_line_ids.ids],
				#'details_by_salary_head':[], TODO put me back
				'name': '',
				'contract_id': False,
				'struct_id': False,
			}
		}
		if (not employee_id) or (not date_from) or (not date_to):
			return res
		ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
		employee = self.env['hr.employee'].browse(employee_id)
		locale = self.env.context.get('lang') or 'en_US'

		slip_name = employee.nip +' '+employee.name+' '+employee.master_id.name + ' '+employee.area.name
		#self.name = slip_name

		res['value'].update({
			'name': slip_name,
			'company_id': employee.company_id.id,
		})

		if not self.env.context.get('contract'):
			#fill with the first contract of the employee
			contract_ids = self.get_contract(employee, date_from, date_to)
		else:
			if contract_id:
				#set the list of contract for which the input have to be filled
				contract_ids = [contract_id]
			else:
				#if we don't give the contract, then the input to fill should be for all current contracts of the employee
				contract_ids = self.get_contract(employee, date_from, date_to)

		if not contract_ids:
			return res
		contract = self.env['hr.contract'].browse(contract_ids[0])
		res['value'].update({
			'contract_id': contract.id
		})
		struct = contract.struct_id
		if not struct:
			return res
		res['value'].update({
			'struct_id': struct.id,
		})
		#computation of the salary input
		contracts = self.env['hr.contract'].browse(contract_ids)
		worked_days_line_ids = self.get_worked_day_lines(contracts, attend_from, attend_to)
		input_line_ids = self.get_inputs(contracts, date_from, date_to)
		res['value'].update({
			'worked_days_line_ids': worked_days_line_ids,
			'input_line_ids': input_line_ids,
		})
		return res
	
	

	@api.onchange('employee_id', 'date_from', 'date_to')
	def onchange_employee(self):
		# if month and year not defined. no need to proceed
		if self.month == False or self.year == False:
			return

		self.ensure_one()
		if (not self.employee_id) or (not self.date_from) or (not self.date_to):
			return
		employee = self.employee_id
		date_from = self.date_from
		date_to = self.date_to
		contract_ids = []

		ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
		locale = self.env.context.get('lang') or 'en_US'

		slip_name = employee.nip +' '+employee.name+' '+employee.master_id.name + ' '+employee.area.name
		self.name = slip_name

		#self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
		self.company_id = employee.company_id

		if not self.env.context.get('contract') or not self.contract_id:
			contract_ids = self.get_contract(employee, date_from, date_to)
			if not contract_ids:
				return
			self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

		if not self.contract_id.struct_id:
			return
		self.struct_id = self.contract_id.struct_id
		
		self.position_id 	= employee.master_id.id
		self.departement_id = employee.department_id.id
		self.location_id 	= employee.work_location_id.id 
		self.grade_id		= employee.grade_id.id 

		# leng services based on date join
		join_date 			= employee.join_date

		today 				= date.today()
		age 				= relativedelta(today, join_date)

		self.service_length	= str(age.years)+' tahun '+str(age.months)+' bulan'

		#check propinsi dan UMP
		self.province		= employee.work_location_id.address_id.state_id.id
		self.ump			= employee.work_location_id.address_id.state_id.ump
		


		#computation of the salary input
		contracts = self.env['hr.contract'].browse(contract_ids)
		if contracts:
			worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
			worked_days_lines = self.worked_days_line_ids.browse([])
			for r in worked_days_line_ids:
				worked_days_lines += worked_days_lines.new(r)
			self.worked_days_line_ids = worked_days_lines

			input_line_ids = self.get_inputs(contracts, date_from, date_to)
			input_lines = self.input_line_ids.browse([])
			for r in input_line_ids:
				input_lines += input_lines.new(r)
			self.input_line_ids = input_lines
			return



	def action_payslip_done(self):
		self.compute_sheet()
		result = self.write({'state': 'done'})
		self.action_send_email()
		return result
	
	def action_send_email(self):
		if self.send_mail == 'yes':
			mail_template 	= self.env.ref('internal_memo.custom_mail_template_payslip')
			email_values 	= {'email_from' :'noreply.it@virtusway.co.id'}
			mail = mail_template.send_mail(self.id, force_send=True,email_values=email_values)
			mail_id = self.env['mail.mail'].sudo().search([('id','=',mail)])
			if mail_id.state == 'sent':
				self.write({'send_email_status': 'sent'})
			elif mail_id.state == 'exception':
				self.write({'send_email_status': 'error'})
		#self.ensure_one()
		#ir_model_data = self.env['ir.model.data']
		#try:
		#	template_id = self.env.ref('internal_memo.custom_mail_template_payslip').id
		#except ValueError:
		#	template_id = False
		#try:
		#	compose_form_id = ir_model_data._xmlid_lookup('mail.email_compose_message_wizard_form')[2]
		#except ValueError:
		#	compose_form_id = False
		#ctx = {
		#	'default_model': 'hr.payslip',
		#	'default_res_id': self.ids[0],
		#	'default_use_template': bool(template_id),
		#	'default_template_id': template_id,
		#	'default_composition_mode': 'comment',
		#}
		#return {
		#	'name': _('Compose Email'),
		#	'type': 'ir.actions.act_window',
		#	'view_mode': 'form',
		#	'res_model': 'mail.compose.message',
		#	'views': [(compose_form_id, 'form')],
		#	'view_id': compose_form_id,
		#	'target': 'new',
		#	'context': ctx,
		#}

	@api.model
	def get_worked_day_lines(self, contracts, date_from, date_to):
		_logger = logging.getLogger(__name__)
		"""
		@param contract: Browse record of contracts
		@return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
		"""
		res = []
		# fill only if the contract as a working schedule linked
		for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
			day_from = datetime.combine(fields.Date.from_string(date_from), time.min)
			day_to = datetime.combine(fields.Date.from_string(date_to), time.max)

			# compute leave days
			leaves = {}
			calendar = contract.resource_calendar_id
			tz = timezone(calendar.tz)
			day_leave_intervals = contract.employee_id.list_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
			for day, hours, leave in day_leave_intervals:
				holiday = leave.holiday_id
				current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
					'name': holiday.holiday_status_id.name or _('Global Leaves'),
					'sequence': 5,
					'code': holiday.holiday_status_id.code or 'GLOBAL',
					'number_of_days': 0.0,
					'number_of_hours': 0.0,
					'contract_id': contract.id,
				})
				current_leave_struct['number_of_hours'] -= hours
				work_hours = calendar.get_work_hours_count(
					tz.localize(datetime.combine(day, time.min)),
					tz.localize(datetime.combine(day, time.max)),
					compute_leaves=False,
				)
				if work_hours:
					current_leave_struct['number_of_days'] -= hours / work_hours

			
			# tidak perlu ambil bulanan, tapi harian
			# kontrak sesuai dengan range periode
			contract_list = self.env['hr.contract'].sudo().search(['&',('state','in',['open','close']),'&',('employee_id','=', contract.employee_id.id),'|',('state','=','open'),'|','&',('date_end','>=', date_from),('date_end','<=', date_to),'|','&',('date_start','>=', date_from),('date_start','<=', date_to),'&',('date_start','<=', date_from),('date_end','>=', date_to) ], order="date_start asc")

			# based on list contract
			# possible very many contract
			for contr in contract_list:
				# jika periode gaji awal lebih atau sama dengan contract
				if date_from >= contr['date_start']:
					# mulai dari kontrak
					if contr['date_end'] == False or date_to <= contr['date_end']:
						presensi_list = self.env['hr.payroll.presensi.line'].sudo().search_read([('name','=',contract.employee_id.id),('date','>=',date_from),('date','<=',date_to)])
					else:
						presensi_list = self.env['hr.payroll.presensi.line'].sudo().search_read([('name','=',contract.employee_id.id),('date','>=',date_from),('date','<=',contr['date_end'])])
				else:
					if  contr['date_end'] == False or date_to <= contr['date_end']:
						presensi_list = self.env['hr.payroll.presensi.line'].sudo().search_read([('name','=',contract.employee_id.id),('date','>=',contr['date_start']),('date','<=',date_to)])
					else:
						presensi_list = self.env['hr.payroll.presensi.line'].sudo().search_read([('name','=',contract.employee_id.id),('date','>=',contr['date_start']),('date','<=',contr['date_end'])])

				total_hari 		= 0
				total_shift 	= 0

				if len(presensi_list) > 0:
					for presen in presensi_list:
						total_hari 	= total_hari + 1
						total_shift = total_shift + presen['shift']

				# kasus presensi nggak jalan maka pakai api bulanan
				if total_hari == 0:
					headers 	= {
						"Content-Type"	: "text/plain", 
							"Accept"		: "*/*", 
							"Catch-Control"	: "no-cache",
							"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
					}

					url 		= "https://api.smartpresence.id/v1/customrequest/virtusabsence?startdate="+datetime.strftime(date_from, "%Y-%m-%d")+"&enddate="+datetime.strftime(date_to, "%Y-%m-%d")+"&employeenumber="+contract.employee_id.nip
					response 	= requests.get(url, headers=headers)

					json_response = response.json()

					if json_response['status'] == 'OK':
						if len(json_response['data']) > 0 :
							total_hari 	= json_response['data'][0]['presence_count']
							total_shift	= json_response['data'][0]['presence_count']
					else:
						raise UserError('Pengambilan data smart presence gagal')


				attendances = {
					'name'				: _("Hari kerja"),
					'sequence'			: 1,
					'code'				: 'WORK100',
					'number_of_days'	: total_hari,
					'number_of_hours'	: total_shift,
					'contract_id'		: contr.id,
				}

				res.append(attendances)

			
			res.extend(leaves.values())

			# compute worked days
			#work_data = contract.employee_id._get_work_days_data(
			#	day_from,
			#	day_to,
			#	calendar=contract.resource_calendar_id,
			#	compute_leaves=False,
			#)

			
			#headers 	= {
			#				"Content-Type"	: "text/plain", 
			#				"Accept"		: "*/*", 
			#				"Catch-Control"	: "no-cache",
			#				"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
			#		}

			#url 		= "https://api.smartpresence.id/v1/customrequest/virtusabsence?startdate="+datetime.strftime(date_from, "%Y-%m-%d")+"&enddate="+datetime.strftime(date_to, "%Y-%m-%d")+"&employeenumber="+contract.employee_id.nip
			#response 	= requests.get(url, headers=headers)

			#_logger.error('TEST WORK DAYS')
			#_logger.error(url)

			#json_response = response.json()

			#if json_response['status'] == 'OK':
			#	attendances = {
			#		'name': _("Work Day Count"),
			#		'sequence': 1,
			#		'code': 'WORK100',
			#		'number_of_days': json_response['data'][0]['presence_count'],
			#		'number_of_hours': 0,
			#		'contract_id': contract.id,
			#	}

			#	res.append(attendances)

			#	attendances2 = {
			#		'name': _("Work Day Expected"),
			#		'sequence': 1,
			#		'code': 'WORKDAY',
			#		'number_of_days': json_response['data'][0]['workday_count'],
			#		'number_of_hours': 0,
			#		'contract_id': contract.id,
			#	}

			#	res.append(attendances2)

			#	res.extend(leaves.values())

				

			#else:
			#	raise UserError('Pengambilan data smart presence gagal')

			
		return res
	
	@api.model
	def _get_payslip_lines(self, contract_ids, payslip_id):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
			return localdict

		class BrowsableObject(object):
			def __init__(self, employee_id, dict, env):
				self.employee_id = employee_id
				self.dict = dict
				self.env = env

			def __getattr__(self, attr):
				return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(amount) as sum
					FROM hr_payslip as hp, hr_payslip_input as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()[0] or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
					FROM hr_payslip as hp, hr_payslip_worked_days as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()

			def sum(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[0] or 0.0

			def sum_hours(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[1] or 0.0

		class Payslips(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
							FROM hr_payslip as hp, hr_payslip_line as pl
							WHERE hp.employee_id = %s AND hp.state = 'done'
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
							(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()
				return res and res[0] or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules_dict = {}
		worked_days_dict = {}
		inputs_dict = {}
		blacklist = []
		payslip = self.env['hr.payslip'].browse(payslip_id)
		for worked_days_line in payslip.worked_days_line_ids:
			worked_days_dict[worked_days_line.code] = worked_days_line
		for input_line in payslip.input_line_ids:
			inputs_dict[input_line.code] = input_line

		categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
		inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
		worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
		payslips = Payslips(payslip.employee_id.id, payslip, self.env)
		rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

		baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
		#get the ids of the structures on the contracts and their parent id as well
		contracts = self.env['hr.contract'].browse(contract_ids)
		if len(contracts) == 1 and payslip.struct_id:
			structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
		else:
			structure_ids = contracts.get_all_structures()
		#get the rules of the structure and thier children
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
		sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

		for contract in contracts:
			employee = contract.employee_id
			localdict = dict(baselocaldict, employee=employee, contract=contract)
			for rule in sorted_rules:
				key = rule.code + '-' + str(contract.id)
				localdict['result'] = None
				localdict['result_qty'] = 1.0
				localdict['result_rate'] = 100
				#check if the rule can be applied
				if rule._satisfy_condition(localdict) and rule.id not in blacklist:
					#compute the amount of the rule
					amount, qty, rate = rule._compute_rule(localdict)

					#check if there is already a rule computed with that code
					previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
					#set/overwrite the amount computed for this rule in the localdict
					tot_rule = contract.company_id.currency_id.round(amount * qty * rate / 100.0)
					localdict[rule.code] = tot_rule
					rules_dict[rule.code] = rule
					#sum the amount for its salary category
					localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
					#create/overwrite the rule in the temporary results
					result_dict[key] = {
						'salary_rule_id': rule.id,
						'contract_id': contract.id,
						'name': rule.name,
						'code': rule.code,
						'category_id': rule.category_id.id,
						'sequence': rule.sequence,
						'appears_on_payslip': rule.appears_on_payslip,
						'condition_select': rule.condition_select,
						'condition_python': rule.condition_python,
						'condition_range': rule.condition_range,
						'condition_range_min': rule.condition_range_min,
						'condition_range_max': rule.condition_range_max,
						'amount_select': rule.amount_select,
						'amount_fix': rule.amount_fix,
						'amount_python_compute': rule.amount_python_compute,
						'amount_percentage': rule.amount_percentage,
						'amount_percentage_base': rule.amount_percentage_base,
						'register_id': rule.register_id.id,
						'amount': amount,
						'amount_original': amount,
						'employee_id': contract.employee_id.id,
						'quantity': qty,
						'rate': rate,
					}
				else:
					#blacklist this rule and its children
					blacklist += [id for id, seq in rule._recursive_search_of_rules()]

		return list(result_dict.values())
	
	@api.model
	def _get_payslip_lines_upgrade(self, contract_ids, payslip_id, previous_data):
		def _sum_salary_rule_category(localdict, category, amount):
			if category.parent_id:
				localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
			localdict['categories'].dict[category.code] = category.code in localdict['categories'].dict and localdict['categories'].dict[category.code] + amount or amount
			return localdict

		class BrowsableObject(object):
			def __init__(self, employee_id, dict, env):
				self.employee_id = employee_id
				self.dict = dict
				self.env = env

			def __getattr__(self, attr):
				return attr in self.dict and self.dict.__getitem__(attr) or 0.0

		class InputLine(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(amount) as sum
					FROM hr_payslip as hp, hr_payslip_input as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()[0] or 0.0

		class WorkedDays(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""
			def _sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""
					SELECT sum(number_of_days) as number_of_days, sum(number_of_hours) as number_of_hours
					FROM hr_payslip as hp, hr_payslip_worked_days as pi
					WHERE hp.employee_id = %s AND hp.state = 'done'
					AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pi.payslip_id AND pi.code = %s""",
					(self.employee_id, from_date, to_date, code))
				return self.env.cr.fetchone()

			def sum(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[0] or 0.0

			def sum_hours(self, code, from_date, to_date=None):
				res = self._sum(code, from_date, to_date)
				return res and res[1] or 0.0

		class Payslips(BrowsableObject):
			"""a class that will be used into the python code, mainly for usability purposes"""

			def sum(self, code, from_date, to_date=None):
				if to_date is None:
					to_date = fields.Date.today()
				self.env.cr.execute("""SELECT sum(case when hp.credit_note = False then (pl.total) else (-pl.total) end)
							FROM hr_payslip as hp, hr_payslip_line as pl
							WHERE hp.employee_id = %s AND hp.state = 'done'
							AND hp.date_from >= %s AND hp.date_to <= %s AND hp.id = pl.slip_id AND pl.code = %s""",
							(self.employee_id, from_date, to_date, code))
				res = self.env.cr.fetchone()
				return res and res[0] or 0.0

		#we keep a dict with the result because a value can be overwritten by another rule with the same code
		result_dict = {}
		rules_dict = {}
		worked_days_dict = {}
		inputs_dict = {}
		blacklist = []
		payslip = self.env['hr.payslip'].browse(payslip_id)
		for worked_days_line in payslip.worked_days_line_ids:
			worked_days_dict[worked_days_line.code] = worked_days_line
		for input_line in payslip.input_line_ids:
			inputs_dict[input_line.code] = input_line

		categories = BrowsableObject(payslip.employee_id.id, {}, self.env)
		inputs = InputLine(payslip.employee_id.id, inputs_dict, self.env)
		worked_days = WorkedDays(payslip.employee_id.id, worked_days_dict, self.env)
		payslips = Payslips(payslip.employee_id.id, payslip, self.env)
		rules = BrowsableObject(payslip.employee_id.id, rules_dict, self.env)

		baselocaldict = {'categories': categories, 'rules': rules, 'payslip': payslips, 'worked_days': worked_days, 'inputs': inputs}
		#get the ids of the structures on the contracts and their parent id as well
		contracts = self.env['hr.contract'].browse(contract_ids)
		if len(contracts) == 1 and payslip.struct_id:
			structure_ids = list(set(payslip.struct_id._get_parent_structure().ids))
		else:
			structure_ids = contracts.get_all_structures()
		#get the rules of the structure and thier children
		rule_ids = self.env['hr.payroll.structure'].browse(structure_ids).get_all_rules()
		#run the rules by sequence
		sorted_rule_ids = [id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]
		sorted_rules = self.env['hr.salary.rule'].browse(sorted_rule_ids)

		for contract in contracts:
			employee = contract.employee_id
			localdict = dict(baselocaldict, employee=employee, contract=contract)
			for rule in sorted_rules:
				key = rule.code + '-' + str(contract.id)
				localdict['result'] = None
				localdict['result_qty'] = 1.0
				localdict['result_rate'] = 100
				#check if the rule can be applied
				if rule._satisfy_condition(localdict) and rule.id not in blacklist:
					#compute the amount of the rule
					amount, qty, rate = rule._compute_rule(localdict)

					to_override = previous_data.filtered(lambda r: r.code == rule.code)

					if to_override.id != False and to_override.is_override == True and to_override.ignore_formula == True:
						amount_original	= amount
						amount 			= to_override.amount_correction
					else:
						amount_original = amount


					#check if there is already a rule computed with that code
					previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
					#set/overwrite the amount computed for this rule in the localdict
					tot_rule = contract.company_id.currency_id.round(amount * qty * rate / 100.0)
					localdict[rule.code] = tot_rule
					rules_dict[rule.code] = rule
					#sum the amount for its salary category
					localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
					#create/overwrite the rule in the temporary results
					result_dict[key] = {
						'salary_rule_id': rule.id,
						'contract_id': contract.id,
						'name': rule.name,
						'code': rule.code,
						'category_id': rule.category_id.id,
						'sequence': rule.sequence,
						'appears_on_payslip': rule.appears_on_payslip,
						'condition_select': rule.condition_select,
						'condition_python': rule.condition_python,
						'condition_range': rule.condition_range,
						'condition_range_min': rule.condition_range_min,
						'condition_range_max': rule.condition_range_max,
						'amount_select': rule.amount_select,
						'amount_fix': rule.amount_fix,
						'amount_python_compute': rule.amount_python_compute,
						'amount_percentage': rule.amount_percentage,
						'amount_percentage_base': rule.amount_percentage_base,
						'register_id': rule.register_id.id,
						'amount': amount,
						'amount_original': amount_original,
						'employee_id': contract.employee_id.id,
						'quantity': qty,
						'rate': rate,
						'id'	: to_override.id,
						'is_override' : to_override.is_override
					}
				else:
					#blacklist this rule and its children
					blacklist += [id for id, seq in rule._recursive_search_of_rules()]

		return list(result_dict.values())

	def sending_mail(self):
		for payslip in self:
			emp_info = self.env['hr.employee'].sudo().search([('id','=',payslip.employee_id.id)])

			emp_info.write({
				'send_mail'	: 'yes'
			})

	def unsend_mail(self):
		for payslip in self:
			emp_info = self.env['hr.employee'].sudo().search([('id','=',payslip.employee_id.id)])

			emp_info.write({
				'send_mail'	: 'no'
			})

	
	def action_dosend_email(self):
		for payslip in self:
			emp_info = self.env['hr.employee'].sudo().search([('id','=',payslip.employee_id.id)])

			emp_info.write({
				'send_mail'	: 'yes'
			})

			#self.env['mail.message'].create(
			#{
			#	'message_type'			:"notification",
            #    "subtype"				: self.env.ref("mail.mt_comment").id,
            #    'body'					: "Test Kirim Email",
            #    'subject'				: "Test Kirim Email",
            #    'needaction_partner_ids': [(4, self.env.user.partner_id.id)],
            #    'model'					: 'hr.employee',
            #    'res_id'				: payslip.id
            #})



	def action_unsend_email(self):
		for payslip in self:
			emp_info = self.env['hr.employee'].sudo().search([('id','=',payslip.employee_id.id)])

			emp_info.write({
				'send_mail'	: 'no'
			})

	send_email_status = fields.Selection([('not_sent', 'Belum Dikirim'), ('sent', 'Terkirim'), ('error', 'Error')], string='Status Kirim Email', default='not_sent', readonly=True)

	def action_send_email_from_wizard(self):
		if self.send_mail == 'yes':
			mail_template 	= self.env.ref('internal_memo.custom_mail_template_payslip')
			email_values 	= {'email_from' :'noreply.it@virtusway.co.id'}
			mail = mail_template.send_mail(self.id, force_send=True,email_values=email_values)
			mail_id = self.env['mail.mail'].sudo().search([('id','=',mail)])
			if mail_id.state == 'sent':
				self.write({'send_email_status': 'sent'})
			elif mail_id.state == 'exception':
				self.write({'send_email_status': 'error'})
			return mail_id
		else:
			return False

class HrPayslipSendEmailWizard(models.TransientModel):
	_name = "hr.payslip.send.email.wizard"

	def _get_default_bulan(self):
		payslip_id = self.env['hr.payslip'].sudo().search([], order="year desc, month desc", limit=1)
		return payslip_id.month

	def _get_default_tahun(self):
		payslip_id = self.env['hr.payslip'].sudo().search([], order="year desc, month desc", limit=1)
		return payslip_id.year

	period_id = fields.Many2one("hr.periode", string="Payroll Periode")
	year = fields.Integer(string='Tahun', default=_get_default_tahun)
	month = fields.Selection(
		[ 
			('01', 'Januari'),
			('02', 'Februari'),
			('03', 'Maret'),
			('04', 'April'),
			('05', 'Mei'),
			('06', 'Juni'),
			('07', 'Juli'),
			('08', 'Agustus'),
			('09', 'September'),
			('10', 'Oktober'),
			('11', 'November'),
			('12', 'Desember')
		], 
		string   = 'Bulan',    
		required =True, default=_get_default_bulan)
	send_email_status = fields.Selection([('not_sent', 'Belum Dikirim'), ('sent', 'Terkirim'), ('error', 'Error')], string='Status Kirim Email')
	employee_ids = fields.Many2many("hr.employee", string="Pegawai")
	employee_count = fields.Integer(string="Jumlah Pegawai")
	error_ids = fields.One2many("hr.payslip.send.email.error.wizard", "wizard_id", string="Error")

	@api.onchange('period_id', 'year', 'month', 'employee_ids', 'send_email_status')
	def _onchange_employee_count(self):
		domain = []
		if self.period_id:
			domain.append(('payroll_periode', '=', self.period_id.id))
		if self.month:
			domain.append(('month', '=', self.month))
		if self.year:
			domain.append(('year', '=', self.year))
		if self.send_email_status:
			domain.append(('send_email_status', '=', self.send_email_status))
		if domain:
			payslip_ids = self.env['hr.payslip'].sudo().search(domain)
			self.employee_count = len(payslip_ids.mapped('employee_id'))
			employee_ids_domain = [('id', 'in', payslip_ids.mapped('employee_id').ids)]
			return {'domain': {'employee_ids': employee_ids_domain}}

	def button_send_email(self):
		domain = []
		if self.period_id:
			domain.append(('payroll_periode', '=', self.period_id.id))
		if self.month:
			domain.append(('month', '=', self.month))
		if self.year:
			domain.append(('year', '=', self.year))
		if self.employee_ids:
			domain.append(('employee_id', 'in', self.employee_ids.ids))
		if self.send_email_status:
			domain.append(('send_email_status', '=', self.send_email_status))
		
		payslip_ids = self.env['hr.payslip'].sudo().search(domain)
		if self.error_ids:
			payslip_ids = payslip_ids.filtered(lambda r: r.id in self.error_ids.mapped('payslip_id').ids)

		for payslip in payslip_ids.with_progress(msg="Sending Email"):
			error_id = self.error_ids.filtered(lambda r: r.payslip_id.id == payslip.id)
			try:
				mail = payslip.action_send_email_from_wizard()
				if not mail:
					if not error_id:
						self.env['hr.payslip.send.email.error.wizard'].sudo().create({
							'wizard_id'	: self.id,
							'employee_id'	: payslip.employee_id.id,
							'payslip_id'	: payslip.id,
							'error'		: "Kolom 'Kirim Email Gaji' pada Payslip berisi 'Tidak'"
						})
					else:
						error_id.write({
							'error'		: "Kolom 'Kirim Email Gaji' pada Payslip berisi 'Tidak'"
						})
				elif mail.state == 'exception':
					if not error_id:
						self.env['hr.payslip.send.email.error.wizard'].sudo().create({
							'wizard_id'	: self.id,
							'employee_id'	: payslip.employee_id.id,
							'payslip_id'	: payslip.id,
							'error'		: mail.failure_reason
						})
					else:
						error_id.write({
							'error'		: mail.failure_reason
						})
			except Exception as e:
				if not error_id:
					self.env['hr.payslip.send.email.error.wizard'].sudo().create({
						'wizard_id'	: self.id,
						'employee_id'	: payslip.employee_id.id,
						'payslip_id'	: payslip.id,
						'error'		: str(e)
					})
				else:
					error_id.write({
						'error'		: str(e)
					})	
		if len(self.error_ids) > 0 :
			return { 
				'context'	: self.env.context, 
				'view_type'	: 'form', 
				'view_mode'	: 'form', 
				'res_model'	: 'hr.payslip.send.email.wizard', 
				'res_id'	: self.id, 
				'type'		: 'ir.actions.act_window', 
				'target'	: 'new' 
			}
		payslip_ids = self.env['hr.payslip'].sudo().search(domain)
		return {
			'type'			: 'ir.actions.act_window',
			'name'			: 'Payslip Send Email',
			'res_model'		: 'hr.payslip',
			'view_id'		: self.env.ref('internal_memo.hr_payslip_send_email_tree').id,
			'views'			: [(self.env.ref('internal_memo.hr_payslip_send_email_tree').id, 'tree')],
			'view_type' 	: 'tree',
			'view_mode' 	: 'tree',
			'target' 		: 'current',
			'domain'		: [('id', 'in', payslip_ids.ids)]
		}
	
class HrPayslipSendEmailErrorWizard(models.TransientModel):
	_name = "hr.payslip.send.email.error.wizard"

	wizard_id = fields.Many2one("hr.payslip.send.email.wizard", string="Wizard ID")
	employee_id = fields.Many2one("hr.employee", string="Pegawai")
	payslip_id = fields.Many2one("hr.payslip", string="Payslip")
	error = fields.Text(string="Error")


class HrPayslipBankTransferWizard(models.TransientModel):
	_name = "hr.payslip.bank.transfer.wizard"


	def _get_default_bulan(self):
		payslip_id = self.env['hr.payslip'].sudo().search([('state', '=', 'done')], order="year desc, month desc", limit=1)
		return payslip_id.month

	def _get_default_tahun(self):
		payslip_id = self.env['hr.payslip'].sudo().search([('state', '=', 'done')], order="year desc, month desc", limit=1)
		return payslip_id.year

	period_id = fields.Many2one("hr.periode", string="Payroll Periode")
	year = fields.Integer(string='Tahun', default=_get_default_tahun)
	month = fields.Selection(
		[ 
			('01', 'Januari'),
			('02', 'Februari'),
			('03', 'Maret'),
			('04', 'April'),
			('05', 'Mei'),
			('06', 'Juni'),
			('07', 'Juli'),
			('08', 'Agustus'),
			('09', 'September'),
			('10', 'Oktober'),
			('11', 'November'),
			('12', 'Desember')
		], 
		string   = 'Bulan',    
		required =True, default=_get_default_bulan)
	employee_count = fields.Integer(string="Pegawai Terhitung")
	employee_ids_count = fields.Many2many("hr.employee", "hr_payslip_bank_transfer_wizard_employee_ids_count_rel", string="Pegawai")
	all_employee = fields.Boolean(string="Semua Pegawai", default=False)
	employee_ids = fields.Many2many("hr.employee", string="Pegawai")
	error_ids = fields.One2many("hr.payslip.bank.transfer.error.wizard", "wizard_id", string="Error")
	excel_file = fields.Binary(string="File Excel")

	@api.onchange('period_id', 'year', 'month')
	def _onchange_employee_count(self):
		domain = [('state', '=', 'done')]
		if self.period_id:
			domain.append(('payroll_periode', '=', self.period_id.id))
		if self.month:
			domain.append(('month', '=', self.month))
		if self.year:
			domain.append(('year', '=', self.year))

		payslip_ids = self.env['hr.payslip'].sudo().search(domain)
		employee_ids = payslip_ids.mapped('employee_id')
		self.employee_count = len(employee_ids)
		self.employee_ids_count = [(6, 0, employee_ids.ids)]
		employee_ids_domain = [('id', 'in', employee_ids.ids)]
		return {'domain': {'employee_ids': employee_ids_domain}}
	
	def button_process(self):
		output 						= io.BytesIO()
		workbook 					= xlsxwriter.Workbook(output, {'in_memory': True})
		sheet 						= workbook.add_worksheet()

		cell_format 			= workbook.add_format({'font_size': 12, 'align': 'center'})
		head 					= workbook.add_format({'align': 'center', 'bold': True, 'font_size': 16})
		header 					= workbook.add_format({'align': 'center', 'bold': True, 'font_size': 10, 'border' : 1})
		cell_left 				= workbook.add_format({'font_size': 10, 'align': 'left', 'border' : 1})
		cell_center 			= workbook.add_format({'font_size': 10, 'align': 'center', 'border' : 1})
		cell_right 				= workbook.add_format({'font_size': 10, 'align': 'right', 'border' : 1})
		cell_right_number 		= workbook.add_format({'font_size': 10, 'align': 'right', 'border' : 1, 'num_format': '#,##0'})


		column_list = [
						'C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','AA','AB',
				 		'AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN','AO','AP','AQ','AR',
						'AS','AT','AU', 'AV','AW','AX', 'AY','AZ','BA','BB',
				 		'BC','BD','BE','BF','BG','BH','BI','BJ','BK','BL','BM','BN','BO','BP','BQ','BR',
						'BS','BT','BU', 'BV','BW','BX', 'BY','BZ'
					 ]
		#Payslip Domain
		domain = [('state', '=', 'done')]
		if self.period_id:
			domain.append(('payroll_periode', '=', self.period_id.id))
		if self.month:
			domain.append(('month', '=', self.month))
		if self.year:
			domain.append(('year', '=', self.year))

		sheet.set_column(0, 0, 5)
		sheet.set_column(1, 20, 20)
		sheet.write(0, 0, 'No.', header)
		sheet.write(0, 1, 'Nama Bank', header)
		sheet.write(0, 2, 'No. Rekening', header)
		sheet.write(0, 3, 'Rekening Atas Nama', header)
		sheet.write(0, 4, 'NIK', header)
		sheet.write(0, 5, 'Pegawai', header)
		sheet.write(0, 6, 'Nama Bank', header)
		sheet.write(0, 7, 'No. Rekening', header)
		sheet.write(0, 8, 'Rekening Atas Nama', header)
		sheet.write(0, 9, 'Kode', header)
		sheet.write(0, 10, 'Jumlah', header)

		#generate data
		if self.all_employee:
			employee_ids = self.employee_ids_count
		else:
			employee_ids = self.employee_ids
		domain.append(('employee_id', 'in', employee_ids.ids))
		payslip_ids = self.env['hr.payslip'].sudo().search(domain)


		current_row = 1
		no = 0
		total_net_pay = 0
		self.error_ids.unlink()
		for employee in employee_ids.with_progress(msg="Generating Data"):
			payslip_id = payslip_ids.filtered(lambda p: p.employee_id.id == employee.id)
			if payslip_id:
				net_pay = payslip_id[0].line_ids.filtered(lambda p: p.code == 'NETPAY').amount
				pembayaran_id = employee.pembayaran_ids.filtered(lambda p: p.category == self.period_id.category_id)
				if not pembayaran_id:
					self.env['hr.payslip.bank.transfer.error.wizard'].sudo().create({
						'wizard_id'	: self.id,
						'employee_id'	: employee.id,
						'nik'			: employee.nip,
						'error'			: "Pengaturan Pembayaran tidak ditemukan di Pegawai HR Settings"
					})
					rekening = False
				else:
					rekening = pembayaran_id[0].rekening
					if not rekening:
						self.env['hr.payslip.bank.transfer.error.wizard'].sudo().create({
							'wizard_id'	: self.id,
							'employee_id'	: employee.id,
							'nik'			: employee.nip,
							'error'			: "Rekening tidak ditemukan di Pengaturan Pembayaran Pegawai HR Settings"
						})
					
				no += 1
				sheet.write(current_row, 0, no, cell_left)
				sheet.write(current_row, 1, 'nama bank', cell_left)
				sheet.write(current_row, 2, 'no rekening', cell_left)
				sheet.write(current_row, 3, 'rekening atas nama', cell_left)
				sheet.write(current_row, 4, employee.nip, cell_left)
				sheet.write(current_row, 5, employee.name, cell_left)
				sheet.write(current_row, 6, rekening.bank_id.name if rekening else '', cell_left)
				sheet.write(current_row, 7, rekening.acc_number if rekening else '', cell_left)
				sheet.write(current_row, 8, rekening.acc_holder_name if rekening else '', cell_left)
				sheet.write(current_row, 9, self.period_id.currency_code or 'IDR', cell_right_number)
				sheet.write(current_row, 10, net_pay, cell_right_number)
				total_net_pay += net_pay
				current_row+=1
			else:
				self.env['hr.payslip.bank.transfer.error.wizard'].sudo().create({
					'wizard_id'	: self.id,
					'employee_id'	: employee.id,
					'nik'			: employee.nip,
					'error'			: "Payslip tidak ditemukan"
				})
			sheet.merge_range(current_row, 0, current_row, 8, 'Total', cell_right_number)
			sheet.write(current_row, 9, self.period_id.currency_code or 'IDR', cell_right_number)
			sheet.write(current_row, 10, total_net_pay, cell_right_number)
		
		workbook.close()
		output.seek(0)
		file_base64 = base64.b64encode(output.read())
		output.close()
		self.excel_file = file_base64
		return {
            'type': 'ir.actions.act_url',
            'url': 'web/content/?model=hr.payslip.bank.transfer.wizard&field=excel_file&download=true&id=%s&filename=%s' % (self.id, "Bank_Transfer_Data.xlsx"),
            'target': 'new'
        }


class HrPayslipBankTransferErrorWizard(models.TransientModel):
	_name = "hr.payslip.bank.transfer.error.wizard"

	wizard_id = fields.Many2one("hr.payslip.bank.transfer.wizard", string="Wizard ID")
	nik = fields.Char(string="NIK")
	employee_id = fields.Many2one("hr.employee", string="Pegawai")
	error = fields.Text(string="Error")