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

_logger = logging.getLogger(__name__)


class HrPayslipLineCustom(models.Model):
	_inherit 		= "hr.payslip.line"
	
	name 					= fields.Char(string="Payroll Component")
	amount_original			= fields.Float(string='Calculated Amount')
	payfied_input 			= fields.Char(string="Payfield Input")
	amount_correction		= fields.Float(string='Correction Amount')
	is_override				= fields.Boolean(string='Override', default = False)
	can_override			= fields.Boolean(string='Can Override', related ='salary_rule_id.can_override')
	nik						= fields.Char(string='NIK', related='employee_id.nip')
	batch					= fields.Many2one('hr.payslip.run',string="Kelompok Penggajian", related="slip_id.payslip_run_id")				
	employee_status_id 		= fields.Many2one("hr.employee.status", string="Employee Status", related="employee_id.employee_status_id")
	employee_status_code 	= fields.Char(string='Status Code', related="employee_id.employee_status_id.code")



	@api.depends('quantity', 'amount', 'rate')
	def _compute_total(self):
		for line in self:
			if line.is_override == False:
				line.total = float(line.quantity) * line.amount * line.rate / 100
			else:
				line.total	= line.amount_correction


	# on change is_override
	@api.onchange('is_override')
	def onchange_is_override(self):
		for line in self:
			if self.is_override == False:
				line.write({'is_override' : False, 'amount' : line.amount_original})
				#raise UserError('Batalkan Override')
				lines = [(1, line.id,{'is_override' : False, 'amount' : line.amount_original})]
			else:
				line.write({'is_override' : True, 'amount' : line.amount_correction})
				lines = [(1, line.id,{'is_override' : True, 'amount' : line.amount_correction})]
				#raise UserError('Override')
			payslip_id = self.env['hr.payslip'].sudo().search([('id','=', line.slip_id.id)])
			
			payslip_id.write({'line_ids': lines})
			#_logger.error('KOREKSI DATA')
			#_logger.error(lines)
			payslip_id.compute_sheet_update()
			
	# cara hitung per line
	def correction_confirm(self):
		for line in self:
			line.write({'is_override' : True, 'amount' : line.amount_correction})

		payslip_id = self.env['hr.payslip'].sudo().search([('id','=', line.slip_id.id)])
		payslip_id.compute_sheet_update()
		#_logger.error('KOREKSI DATA')

	def correction_cancel(self):
		for line in self:
			line.write({'is_override' : False, 'amount' : line.amount_original})

		payslip_id = self.env['hr.payslip'].sudo().search([('id','=', line.slip_id.id)])
		payslip_id.compute_sheet_update()
		#_logger.error('KOREKSI DATA')


class HrSalaryRuleCustom(models.Model):
	_inherit 		= "hr.salary.rule"

	# detect override
	can_override 	= fields.Boolean(string='Can Override', default=True)


