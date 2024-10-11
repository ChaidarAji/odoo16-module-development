import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrEmployeeSalary(models.Model):
	_inherit = "hr.employee"

	salary_type    = fields.Selection(
		[ ('daily', 'Harian'),('monthly', 'Bulanan')], 
		string   = 'Model Gaji',    
		required =False, 
		Default  = 'monthly')
	
	#employee_number   = fields.Char(string = 'Nomor Karyawan')
	salary_amount	  = fields.Integer(string = 'Persen Gaji', default = 100)
