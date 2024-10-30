import logging
import pytz
import math

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import openpyxl
import base64
from io import BytesIO

from dateutil.relativedelta import relativedelta
from odoo.tools import float_is_zero
from odoo.tools import date_utils
import io
import json

import requests

try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter


_logger = logging.getLogger(__name__)

class PayslipGenerateWizard(models.TransientModel):
	_name 			= "hr.payslip.generate.wizard"
	_description    = "Generate Payslip"
	
	name 				= fields.Many2one(string = "Payroll Periode" ,comodel_name = "hr.periode") 
	periode_label 		= fields.Char(string='Periode Tanggal')
	area_id 			= fields.Many2one(string = "Cost Center" ,comodel_name = "area") 
	employee_number		= fields.Integer(string='Jumlah Pegawai', readonly=True)
	employee_ids 		= fields.One2many('hr.payslip.generate.employee.wizard', 'name', string='Pegawai Terpilih', readonly=False)
	error_ids 			= fields.One2many('hr.payslip.generate.error.wizard', 'name', string='Error', readonly=False)
	is_error_visible	= fields.Boolean(string='Error Visible', default = False)
	choose_employee		= fields.Boolean(string='Pilih Pegawai', default = False)
	show_employee		= fields.Boolean(string='Tampilkan List Pegawai', default = False)
	processed			= fields.Integer(string='Terproses')
	employee_list 		= fields.One2many('hr.payslip.generate.list.wizard', 'name', string='Daftar Pegawai', readonly=False)


	@api.onchange('show_employee')
	def onchange_show_employee(self):
		# find IDS based on selected 
		if self.name.id != False:
			periode_info = self.env['hr.periode'].sudo().search([('id','=', self.name.id)])

			year 		= periode_info.salaryenddate.year
			month		= str(periode_info.salaryenddate.month).zfill(2)

			query 		= "select a.id, a.name, a.nip, a.contract_id, a.company_id from hr_employee AS a left join hr_payslip as b ON b.employee_id = a.id AND b.year = "+str(year)+" AND b.month = '"+str(month)+"' and b.state not IN ('verify','cancel') WHERE a.employee_status_id = "+str(periode_info.status_id.id)+" AND a.active = True AND b.id IS NULL"
					
			if self.area_id.id != False:
				query = query + ' AND a.area = '+str(self.area_id.id)

			self.env.cr.execute(query)
			data_result 			= self.env.cr.fetchall()
			
			
			# populate IDS
			arr_ids = [(5,0,0)]
			counter = 0
			for tup in data_result:
				counter = counter + 1
				arr_ids.append((0,0,{'employee_id' : tup[0], 'nik' : str(tup[2])}))

			self.employee_number 	= counter

			#res = self.write({
			#	'name' 					: self.name.id,
			#	'periode_label'			: self.periode_label,
			#	'area_id'				: self.area_id.id,
			#	'employee_number'		: self.employee_number,
			#	'employee_ids'			: self.employee_ids,
			#	'error_ids'				: self.error_ids,
			#	'is_error_visible'		: self.is_error_visible,
			#	'choose_employee'		: self.choose_employee,
			#	'show_employee'			: self.show_employee,
			#	'processed'				: self.processed,
			#	'employee_list' 		: arr_ids
			#})

			self.write({
				'employee_list' 	: arr_ids,
				'employee_number'	: counter
			})	

			



	@api.onchange('name','area_id')
	def onchange_name(self):
		if self.name.id != False:
			periode_info = self.env['hr.periode'].sudo().search([('id','=', self.name.id)])

			# converting to date label
			bulan_list = {
				'1' : 'Januari',
				'2' : 'Februari',
				'3' : 'Maret',
				'4' : 'April',
				'5' : 'Mei',
				'6' : 'Juni',
				'7' : 'Juli',
				'8' : 'Agustus',
				'9' : 'September',
				'10' : 'Oktober',
				'11' : 'November',
				'12' : 'Desember'
			}

			self.periode_label = str(periode_info.salarystartdate.day) +' '+ bulan_list[str(periode_info.salarystartdate.month)] + ' '+ str(periode_info.salarystartdate.year) +' s.d. '+str(periode_info.salaryenddate.day) +' '+ bulan_list[str(periode_info.salaryenddate.month)] + ' '+ str(periode_info.salaryenddate.year)

			# ambil tahun
			year 		= periode_info.salaryenddate.year
			month		= str(periode_info.salaryenddate.month).zfill(2)

			#query 		= "select a.id, a.name, a.nip from hr_employee AS a left join hr_payslip as b ON b.employee_id = a.id AND b.year = "+str(year)+" AND b.month = '"+str(month)+"' and b.state not IN ('verify','cancel') WHERE a.employee_status_id = "+str(periode_info.status_id.id)+" AND a.active = True AND b.id IS NULL"
			query 		= "select COUNT(a.id) as jumlah from hr_employee AS a left join hr_payslip as b ON b.employee_id = a.id AND b.year = "+str(year)+" AND b.month = '"+str(month)+"' and b.state not IN ('verify','cancel') WHERE a.employee_status_id = "+str(periode_info.status_id.id)+" AND a.active = True AND b.id IS NULL"
			
			if self.area_id.id != False:
				query = query + ' AND a.area = '+str(self.area_id.id)

			self.env.cr.execute(query)
			data_result = self.env.cr.fetchall()


			self.employee_number = data_result[0][0]
			
			#data_dict	= {}

			#for tup in data_result:
			#	data_dict[tup[0]] = {'id' : tup[0], 'name' : tup[1], 'nip' : tup[2]}
			
			#data_result = dict(data_result)


			#_logger.error('DATA RESULT')
			#_logger.error(data_dict)

	def button_generate_payslip(self):
		# find role
		periode_info = self.env['hr.periode'].sudo().search([('id','=', self.name.id)])

		year 		= periode_info.salaryenddate.year
		month		= str(periode_info.salaryenddate.month).zfill(2)

		self.processed = 0


		emp_ids = []
		if len(self.employee_ids) > 0:
			for emp in self.employee_ids:
				emp_ids.append(emp.employee_id.id)
			
			data_result = self.env['hr.employee'].sudo().search([('id','in', emp_ids)])  #"select a.id, a.name, a.nip, a.contract_id, a.company_id from hr_employee AS a WHERE a.id IN("
			
			# change to dict
			data_dict	= {}
			for dat in data_result:
				data_dict[dat.nip] = {'id' : dat.id, 'name' : dat.name, 'nip' : dat.nip,'contract_id' : dat.contract_id.id, 'company_id' : dat.company_id.id}
		else:
			query 		= "select a.id, a.name, a.nip, a.contract_id, a.company_id from hr_employee AS a left join hr_payslip as b ON b.employee_id = a.id AND b.year = "+str(year)+" AND b.month = '"+str(month)+"' and b.state not IN ('verify','cancel') WHERE a.employee_status_id = "+str(periode_info.status_id.id)+" AND a.active = True AND b.id IS NULL"
				
			if self.area_id.id != False:
				query = query + ' AND a.area = '+str(self.area_id.id)

			self.env.cr.execute(query)
			data_result 			= self.env.cr.fetchall()
			self.employee_number 	= data_result[0][0]

			data_dict	= {}

			for tup in data_result:
				data_dict[str(tup[2])] = {'id' : tup[0], 'name' : tup[1], 'nip' : str(tup[2]),'contract_id' : tup[3], 'company_id' : tup[4]}
				
		#data_result = dict(data_result)
		#if 'DO1913034' in data_dict.keys():
		#	raise UserError('ADA')


		if periode_info.useattend == True:
			# call presence
			headers = {
				"Content-Type"	: "text/plain", 
				"Accept"		: "*/*", 
				"Catch-Control"	: "no-cache",
				"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
			}

			url 		= "https://api.smartpresence.id/v1/customrequest/virtusabsence?startdate="+datetime.strftime(periode_info.attendstartdate, "%Y-%m-%d")+"&enddate="+datetime.strftime(periode_info.attendenddate, "%Y-%m-%d")
			response 	= requests.get(url, headers=headers)

			json_response = response.json()

			counter_response = 0

			if json_response['status'] == 'OK':
				if len(json_response['data']) > 0 :
					response_dict = {}
					for resp in json_response['data']:
						response_dict[str(resp['employee_number'])] = {'employee_id' : resp['employee_id'], 'employee_number' : str(resp['employee_number']), 'employee_name' : resp['employee_name'], 'workday_count' : resp['workday_count'], 'presence_count' : resp['presence_count']}

					for resp2 in self.web_progress_iter(response_dict, "Pengambilan Presensi"):
						# check if element object exist
						if resp2 in data_dict.keys():
							schedule_info = self.env['hr.payroll.presensi.bulanan'].sudo().search([('name','=', data_dict[resp2]['id']),('year','=', year),('month','=', month)])
							# insert/update to database
							if schedule_info.id == False:
								self.env['hr.payroll.presensi.bulanan'].create({
									'name' 			: data_dict[resp2]['id'],
									'nik'			: response_dict[resp2]['employee_number'],
									'start'			: periode_info.attendstartdate,
									'end'			: periode_info.attendenddate,
									'year'			: year,
									'month'			: month,
									'work_days'		: response_dict[resp2]['workday_count'],
									'work_shift'	: response_dict[resp2]['presence_count']
								})
							else:
								for sche in schedule_info:
									sche.write({
										'name' 			: data_dict[resp2]['id'],
										'nik'			: response_dict[resp2]['employee_number'],
										'start'			: periode_info.attendstartdate,
										'end'			: periode_info.attendenddate,
										'year'			: year,
										'month'			: month,
										'work_days'		: response_dict[resp2]['workday_count'],
										'work_shift'	: response_dict[resp2]['presence_count']
									})

							#total_hari 	= json_response['data'][0]['presence_count']
							#total_shift	= json_response['data'][0]['presence_count']
			else:
				raise UserError('Pengambilan data smart presence gagal')
		

		arr_invalid 	= [(5, 0, 0)]
		error_visible 	= False
		for res in self.web_progress_iter(data_dict,"Generate Payslip"):
			# create payslip
			employee 			= self.env['hr.employee'].browse(data_dict[res]['id'])

			if employee.employment_status.id == False:
				# to error
				error_visible = True
				arr_invalid.append((0,0,{'nik' : employee.nip, 'employee_id' : employee.id, 'description' : 'Employment status belum di set'}))
			elif employee.contract_id.id == False:
				error_visible = True
				arr_invalid.append((0,0,{'nik' : employee.nip, 'employee_id' : employee.id, 'description' : 'Tidak ada kontrak berjalan'}))
			else:
				slip_name 			= employee.nip +' '+employee.name+' '+employee.master_id.name + ' '+employee.area.name
				try:
					struktur_info 		= self.env['hr.payroll.structure'].sudo().search([('periode_id','=',periode_info.id)])

					if len(struktur_info) > 0:
						for stru in struktur_info:
							struct_id = stru.id

					# calculate worked days based on presence saved

					payslip = self.env['hr.payslip'].create({
						'employee_id'           : data_dict[res]['id'],
						'name'                  : slip_name,
						'periode_id'			: periode_info.id,
						'struct_id'             : struct_id,
						'contract_id'           : employee.contract_id.id,
						'payslip_run_id'        : False,
						'input_line_ids'        : [],
						'worked_days_line_ids'  : [],
						'date_from'             : periode_info.salarystartdate,
						'date_to'               : periode_info.salaryenddate,
						'credit_note'           : '',
						'company_id'            : employee.company_id.id,
						'year'                  : year,
						'month'                 : month,
						'attend_start'          : periode_info.attendstartdate,
						'attend_end'            : periode_info.attendenddate,
						'tax'                   : periode_info.taxdate,
						'paydate'               : periode_info.paydate,
						'parent_id'             : False,
						'is_active'				: True
					})

					self.processed = self.processed  + 1

					contracts = self.env['hr.contract'].browse(employee.contract_id.id)
					worked_days_line_ids 	= payslip.get_worked_day_lines(contracts, periode_info.attendstartdate, periode_info.attendenddate)
					input_line_ids 			= payslip.get_inputs(contracts, periode_info.salarystartdate, periode_info.salaryenddate)



					payslip.write({
						'worked_days_line_ids'	: [(0, 0, x) for x in worked_days_line_ids],
						'input_line_ids'		: [(0, 0, x) for x in input_line_ids]
					})

					payslip.compute_sheet()
				except:
					error_visible = True
					arr_invalid.append((0,0,{'nik' : employee.nip, 'employee_id' : employee.id, 'description' : 'Error sistem : Tidak diketahui'}))

					#raise UserError('Ada error perhitungan pada pegawai '+employee.name+' ('+employee.nip+')')

		self.error_ids 			= arr_invalid
		self.is_error_visible 	= error_visible	
		#raise UserError('HALOO')


class PayslipGenerateEmployeeWizard(models.TransientModel):
	_name 			= "hr.payslip.generate.employee.wizard"
	_description    = "Generate Payslip"

	name 			= fields.Many2one(string = "Payslip Wizard" ,comodel_name = "hr.payslip.generate.wizard") 
	employee_id		= fields.Many2one(string = "nama Pegawai" ,comodel_name = "hr.employee")
	nik				= fields.Char(string='NIK', default=lambda self: self.employee_id.nip)

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		if self.employee_id.id != False:
			self.nik	= self.employee_id.nip
	 

class PayslipGenerateErrorWizard(models.TransientModel):
	_name 			= "hr.payslip.generate.error.wizard"
	_description    = "Generate Payslip"

	name 			= fields.Many2one(string = "Payslip Wizard" ,comodel_name = "hr.payslip.generate.wizard") 
	employee_id		= fields.Many2one(string = "nama Pegawai" ,comodel_name = "hr.employee") 
	nik				= fields.Char(string='NIK', default=lambda self: self.employee_id.nip)
	description		= fields.Char(string='Keterangan')

class PayslipGenerateListWizard(models.TransientModel):
	_name 			= "hr.payslip.generate.list.wizard"
	_description    = "Generate Payslip"

	name 			= fields.Many2one(string = "Payslip Wizard" ,comodel_name = "hr.payslip.generate.wizard") 
	employee_id		= fields.Many2one(string = "nama Pegawai" ,comodel_name = "hr.employee")
	nik				= fields.Char(string='NIK', default=lambda self: self.employee_id.nip)
	employee_name	= fields.Char(string='Pegawai', related="employee_id.name")


	def button_selected_employee(self):
		# get wizard parent
		wizard_info = self.env['hr.payslip.generate.wizard'].sudo().search([('id','=', self.name.id)])

		wizard_info.write({
			'employee_ids' : [(0,0,{'employee_id' : self.employee_id.id, 'nik' : self.employee_id.nip})]
		})
