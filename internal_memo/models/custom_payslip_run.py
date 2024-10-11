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

class HrPayslipRunCustom(models.Model):
	_inherit = "hr.payslip.run"
	
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
	
	contract_id = fields.Many2one('hr.contract.type', string='Contract Type')
	struktur_id = fields.Many2one('hr.payroll.structure', string='Struktur Gaji')

	# will be no longer used contract and struckture, but based on hr_periode_categori
	periode_id 		= fields.Many2one('hr.periode.category', string='Salary Type')

	invalid_ids 	= fields.One2many('hr.payslip.run.invalid', 'batch', string='Gaji Belum Diproses', readonly=True)


	

	@api.onchange('month', 'year','contract_id')
	def onchange_periode(self):
		if self.month != False and self.year != False and self.contract_id != False:
			start_periode    = self.contract_id.periode.start
			end_periode      = self.contract_id.periode.end
			model_periode	 = self.contract_id.periode.periode

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

				self.date_start = tanggal_awal
				self.date_end 	= tanggal_akhir
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

				self.date_start = tanggal_awal
				self.date_end 	= tanggal_akhir


	class HrPayslipLineCustom(models.Model):
		_name           = 'hr.payslip.run.invalid'
		_description    = "Not Processed Data"

		name			= fields.Many2one('hr.employee', string='Pegawai')
		batch			= fields.Many2one('hr.payslip.run', string='Payslip Batch')
		payslip			= fields.Many2one('hr.payslip', string='Slip Gaji')

		position_id = fields.Many2one(
			'master.job',
			string="Job Position"
		)

		location_id = fields.Many2one(
			'hr.work.location',
			string="Work Location"
		)

		area_id = fields.Many2one(
			'area',
			string="Cost Centre"
		)
		

		



					