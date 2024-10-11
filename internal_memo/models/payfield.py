# -*- coding: utf-8 -*-
import logging
import pytz
import math

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrPayfield(models.Model):
	_name           = 'hr.payfield'
	_description    = "Payfield"
	
	name 			= fields.Char(string="Payfield Name")
	code			= fields.Char(string='Payfield No')

class HrPayfieldInput(models.Model):
	_name           = 'hr.payfield.input'
	_description    = "Payfield Input"
	
	employee_id 	= fields.Many2one("hr.employee", string="Pegawai")
	nik 			= fields.Char(string="NIK", related='employee_id.nip')
	master_job_id 	= fields.Many2one("master.job", string="Jabatan", related='employee_id.master_id')
	line_ids 		= fields.One2many("hr.payfield.input.line", 'payfield_input_id')

class HrPayfieldInputLine(models.Model):
	_name           = 'hr.payfield.input.line'
	_description    = "Payfield Input"

	payfield_input_id 	= fields.Many2one("hr.payfield.input")
	payfield_id 		= fields.Many2one("hr.payfield")
	value 				= fields.Char(string="Value")
	#employee_id		= fields.Many2one("hr.employee", string="Pegawai", related="payfield_input_id.employee_id")
	employee_id			= fields.Many2one("hr.employee", string="Pegawai")
	employee_nik		= fields.Char(string='NIP', related="employee_id.nip")

	# def create and write to insert employee_id
	@api.model_create_multi
	def create(self, values):
		_logger = logging.getLogger(__name__)

		# struktur id harus di set ulang
		for val in values:
			_logger.error('CHECK EMPLOYEE')
			_logger.error(val)

			if 'employee_id' in val.keys(): 
				# jika payfield input kosong, insert baru, kasus input dari massal
				check_input = self.env['hr.payfield.input'].sudo().search([('employee_id','=', val['employee_id'])])

				is_empty = True
				if len(check_input) > 0:
					for cek in check_input:
						is_empty = False
				else:
					is_empty = True
				
				if is_empty == True:
					res_input = self.env['hr.payfield.input'].sudo().create({
						'employee_id' : val['employee_id']
					})

					val['payfield_input_id'] = res_input.id
				else:
					for cek in check_input:
						val['payfield_input_id'] = cek.id
			else:
				# find payfield input
				check_input = self.env['hr.payfield.input'].sudo().search([('id','=', val['payfield_input_id'])])

				#raise UserError(str(self.payfield_input_id.employee_id.id))
				val['employee_id']	= check_input.employee_id.id
				

		return super(HrPayfieldInputLine, self).create(values)

	def write(self, values):
		_logger = logging.getLogger(__name__)

		if str(values.get('employee_id')) != 'None':
			# input dari massal, bisa geser
			check_input = self.env['hr.payfield.input'].sudo().search([('employee_id','=', values.get('employee_id'))])

			is_empty = True
			if len(check_input) > 0:
				for cek in check_input:
					is_empty = False
			else:
				is_empty = True

			if is_empty == True:
				res_input = self.env['hr.payfield.input'].sudo().create({
					'employee_id' : values.get('employee_id')
				})

				values['payfield_input_id'] = res_input.id
			else:
				values['payfield_input_id'] = check_input.id

		return super(HrPayfieldInputLine, self).write(values)
	
