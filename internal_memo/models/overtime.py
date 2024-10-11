# -*- coding: utf-8 -*-
import logging
import pytz
import math

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CustomOvertime(models.Model):
	_name           = 'overtime.type'
	_description    = "Tipe Lembur"

	code            = fields.Char(string = 'Kode Lembur')
	name            = fields.Char(string = 'Jenis Lembur')
	overtime_tipe   = fields.Selection([('daily','Harian'),('hour','Jam')], String ='Tipe')
	overtime_schema = fields.Selection([('opsional','Pilihan'),('stage','Bertingkat')], String ='Opsi Perhitungan')
	
class CustomOvertimePay(models.Model):
	_name           = 'overtime.type.pay'
	_description    = "Nilai Pembayaran Lembur"

	name            = fields.Char(string = 'Jenis Lembur')
	type_id         = fields.Many2one('overtime.type', string='Tipe Lembur', Required = False)
	libur   		= fields.Selection([('normal','Hari Normal'),('holiday','Hari Minggu/Libur'),('all','Semua Hari')], String ='jenis Hari')
	urutan           = fields.Integer(string = 'Urutan')
	operator   		= fields.Selection([('none','Tidak Ada'),('<','<'),('<=','<='),('>','>'),('>=','>=')], String ='Operator')
	duration        = fields.Float(string = 'Hari/jam')
	value        	= fields.Float(string = 'Nilai')
	multiplier   	= fields.Selection([('none','Tidak Ada'),('wage','Gaji Pokok')], String ='Pengali')
	master_id 		= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job") 


	@api.onchange('type_id')
	def _onchange_type_id(self):
		if str(self.type_id) != 'None':
			type_info = self.env['overtime.type'].search_read([('id','=',self.type_id.id)])

			for tipe in type_info:
				self.name = tipe['name']

	@api.model_create_multi
	def create(self, values):
		_logger = logging.getLogger(__name__)

		# struktur id harus di set ulang
		for val in values:
			type_info = self.env['overtime.type'].search_read([('id','=',val['type_id'])])

			for tipe in type_info:
				val['name'] = tipe['name'] 

		return super(CustomOvertimePay, self).create(values)

	def write(self, values):
		_logger = logging.getLogger(__name__)

		# struktur id harus di set ulang
		if str(values.get('type_id')) != 'None':
			type_info = self.env['overtime.type'].search_read([('id','=',values.get('type_id'))])
		else:
			type_info = self.env['overtime.type'].search_read([('id','=',self.type_id.id)])

		for tipe in type_info:
			values['name'] = tipe['name']

		return super(CustomOvertimePay, self).write(values)