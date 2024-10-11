import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta, time

import requests

_logger = logging.getLogger(__name__)


class HrPayrollPresensi(models.Model):
	_name           = 'hr.payroll.presensi'
	_description    = "Presensi Smart Presence"
	
	name            = fields.Char(string = 'Name')
	start           = fields.Date(string='Tanggal Awal', required = True, index = True)
	end           	= fields.Date(string='Tanggal Akhir', required = True, index = True)
	target			= fields.Integer(string='Jumlah Pegawai')
	processed		= fields.Integer(string='Terproses', default = 0)
	is_end			= fields.Boolean(string='Selesai ?', default=False)

	line_ids       = fields.One2many('hr.payroll.presensi.employee',inverse_name='presensi_id',string='Pegawai')
	result_ids     = fields.One2many('hr.payroll.presensi.line',inverse_name='presensi_id',string='Hasil API')

	def schedule_presensi(self):
		#headers 	= {
		#				"Content-Type"	: "text/plain", 
		#				"Accept"		: "*/*", 
		#				"Catch-Control"	: "no-cache",
		#				"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
		#		}

		#url 		= "https://api.smartpresence.id/v1/customrequest/virtusabsence?startdate=2024-01-21&enddate=2024-02-20"
		#response 	= requests.get(url, headers=headers)

		

		#json_response = response.json()
	
		#_logger.error('MULAI INSERT PEGAWAI ')
		#_logger.error(json_response['status'])

		#if json_response['status'] == 'OK':
			#_logger.error('INSERT PEGAWAI ')
		#	if len(json_response['data']) > 0:
				
		#		for resp in json_response['data']:
					# check employee
					#_logger.error(resp)
		#			emp_info = self.env['hr.employee'].sudo().search([('nip','=',resp['employee_number'])])
					#_logger.error(str(emp_info.id))

		#			if emp_info.id == False:
		#				result = self.env['hr.employee'].create(
		#					{
		#						'name' 					: resp['employee_name'],
		#						'code'					: str(resp['employee_id']),
		#						'company_id'			: 1,
		#						'resource_calendar_id' 	: 1,
		#						'color' 				: 0,
		#						'department_id' 		: 2,
		#						'job_id'				: 10,
		#						'address_id'			: 1,
		#						'work_location_id'		: 1,
		#						'job_title'				: 'HOUSEKEEPING LEADER',
		#						'work_phone'			: '081390106050',
		#						'employee_type'			: 'employee',
		#						'first_contract_date'	: '2024-01-01',
		#						'leave_manager_id'		: 2,
		#						'salary_type'			: 'daily',
		#						'salary_amount'			: 100,
		#						'mother_name'			: 'A',
		#						'no_kk'					: 'A',
		#						'nip'					: resp['employee_number'],
		#						'master_id'				: 4,
		#						'religion_id'			: 1
		#					}
		#				)

		#return True
	
		presensi_belum = self.env['hr.payroll.presensi'].sudo().search([('is_end','=', False)], limit=1)

		if len(presensi_belum) > 0:
			for presensi in presensi_belum:
				number_processed 	= 0
				#line 				= self.line_ids.filtered(lambda linex: linex.processed == False)
				line = self.env['hr.payroll.presensi.employee'].sudo().search([('presensi_id','=', presensi.id),('processed','=', False)], limit = 20)

				if len(line) > 0:
					# finding data
					headers 	= {
							"Content-Type"	: "text/plain", 
							"Accept"		: "*/*", 
							"Catch-Control"	: "no-cache",
							"apikey" 		: "ms3Rko81bTrbO85ZCpk691PBaItghIyEbCvw0Ex"
					}

					for lin in line:
						url 		= "https://api.smartpresence.id/v1/customrequest/presensiharian?date_start="+datetime.strftime(presensi.start, "%Y%m%d")+"&date_end="+datetime.strftime(presensi.end, "%Y%m%d")+"&empno="+lin.name.nip
						response 	= requests.get(url, headers=headers)

						#_logger.error('TEST WORK DAYS')
						#_logger.error(url)
						
						json_response = response.json()
						#_logger.error(json_response)

						

						if json_response['status'] == 200:
							#_logger.error('TEST WORK DAYS')
							#_logger.error(json_response['data'])

							# berhasil, delete data dulu
							to_delete = self.env['hr.payroll.presensi.line'].sudo().search([('name','=', lin.name.id),('date','>=', presensi.start),('date','<=', presensi.end)])

							if len(to_delete) > 0:
								for dele in to_delete:
									dele.unlink()
							
							
							
							if len(json_response['data']) > 0:
								for item in json_response['data']:
									if item['in'] != '':
										#raise UserError(item['in'])
										result = self.env['hr.payroll.presensi.line'].sudo().create(
											{
												'presensi_id' 	: presensi.id,
												'name'		  	: lin.name.id,
												'date'			: item['date'],
												'presence_in'	: item['in'],
												'presence_out'	: item['out'],
												'shift'			: item['shift']
											}
										)

							number_processed = number_processed + 1

							line.write(
								{
									'processed' : True
								}
							)

							presensi.write(
								{
									'processed' : presensi.processed + 1
								}
							)

							self.env.cr.commit()
				else:
					presensi.sudo().write(
						{
							'is_end' : True
						}
					)

				if presensi.target == presensi.processed:
					presensi.sudo().write(
						{
							'is_end'	: True
						}
					)

				# update presensi
				#if presensi.target == presensi.processed + number_processed:
				#	presensi.sudo().write(
				#		{
				#			'processed' : presensi.processed + number_processed,
				#			'is_end'	: True
				#		}
				#	)
				#else:
				#	presensi.write(
				#		{
				#			'processed' : presensi.processed + number_processed
				#		}
				#)
					

	@api.model_create_multi
	def create(self, values_list):
		for values in values_list:
			# generate employee data based on active employee
			if len(values['line_ids']) == 0:
				# tidak diinput
				employee = self.env['hr.employee'].sudo().search([])

				lineids = []

				if len(employee) > 0:
					for emp in employee:
						new_data = (0, 0,  {'name' : emp.id })
						lineids.append(new_data)

					values['line_ids'] 	= lineids
					values['target']	= len(lineids)

		return super(HrPayrollPresensi, self).create(values_list)

	@api.onchange('start','end')
	def _onchange_start_end(self):
		if self.start != False and self.end != False:
			string = 'Periode '

			if self.start.month == 1:
				string = string + str(self.start.day)+' Januari '+str(self.start.year)
			elif self.start.month == 2:
				string = string + str(self.start.day)+' Februari '+str(self.start.year)
			elif self.start.month == 3:
				string = string + str(self.start.day)+' Maret '+str(self.start.year)
			elif self.start.month == 4:
				string = string + str(self.start.day)+' April '+str(self.start.year)
			elif self.start.month == 5:
				string = string + str(self.start.day)+' Mei '+str(self.start.year)
			elif self.start.month == 6:
				string = string + str(self.start.day)+' Juni '+str(self.start.year)
			elif self.start.month == 7:
				string = string + str(self.start.day)+' Juli '+str(self.start.year)
			elif self.start.month == 8:
				string = string + str(self.start.day)+' Agustus '+str(self.start.year)
			elif self.start.month == 9:
				string = string + str(self.start.day)+' September '+str(self.start.year)
			elif self.start.month == 10:
				string = string + str(self.start.day)+' Oktober '+str(self.start.year)
			elif self.start.month == 11:
				string = string + str(self.start.day)+' November '+str(self.start.year)
			elif self.start.month == 12:
				string = string + str(self.start.day)+' Desember '+str(self.start.year)

			string = string + ' s.d. '

			if self.end.month == 1:
				string = string + str(self.end.day)+' Januari '+str(self.end.year)
			elif self.end.month == 2:
				string = string + str(self.end.day)+' Februari '+str(self.end.year)
			elif self.end.month == 3:
				string = string + str(self.end.day)+' Maret '+str(self.end.year)
			elif self.end.month == 4:
				string = string + str(self.end.day)+' April '+str(self.end.year)
			elif self.end.month == 5:
				string = string + str(self.end.day)+' Mei '+str(self.end.year)
			elif self.end.month == 6:
				string = string + str(self.end.day)+' Juni '+str(self.end.year)
			elif self.end.month == 7:
				string = string + str(self.end.day)+' Juli '+str(self.end.year)
			elif self.end.month == 8:
				string = string + str(self.end.day)+' Agustus '+str(self.end.year)
			elif self.end.month == 9:
				string = string + str(self.end.day)+' September '+str(self.end.year)
			elif self.end.month == 10:
				string = string + str(self.end.day)+' Oktober '+str(self.end.year)
			elif self.end.month == 11:
				string = string + str(self.end.day)+' November '+str(self.end.year)
			elif self.end.month == 12:
				string = string + str(self.end.day)+' Desember '+str(self.end.year)

			self.name = string
			#raise UserError(str(self.start.month)+' '+str(self.start.year))

class HrPayrollPresensiEmployee(models.Model):
	_name           = 'hr.payroll.presensi.employee'
	_description    = "Presensi Smart Presence Pegawai"

	presensi_id     = fields.Many2one(string="ID Master" ,comodel_name = "hr.payroll.presensi")
	name            = fields.Many2one(string="Pegawai" ,comodel_name = "hr.employee")
	processed		= fields.Boolean(string='Terproses', default = False, index = True)

class HrPayrollPresensiLine(models.Model):
	_name           = 'hr.payroll.presensi.line'
	_description    = "Presensi Smart Presence Pegawai"

	presensi_id     = fields.Many2one(string="ID Master" ,comodel_name = "hr.payroll.presensi")
	name            = fields.Many2one(string="Pegawai" ,comodel_name = "hr.employee")
	date			= fields.Date(string='Tanggal Presensi', index = True)
	presence_in		= fields.Char(string='Awal Presensi')
	presence_out	= fields.Char(string='Akhir Presensi')
	shift			= fields.Integer(string='Shift')
	

	