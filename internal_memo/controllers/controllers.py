# -*- coding: utf-8 -*-
import json
from odoo import http
from odoo.http import content_disposition, request
from odoo.tools import html_escape

class ExcelReportController(http.Controller):
	@http.route('/excel_payslip_reports', type='http', auth='user', methods=['POST'], csrf=False)
	def get_excel_payslip_reports(self, model, options, output_format, report_name, **kw):
		uid 			= request.session.uid
		report_obj 		= request.env[model].with_user(uid)
		options 		= json.loads(options)
		token 			= 'hellovirtus'

		try:
			if output_format == 'xlsx':
				response = request.make_response(
				   None,
				   headers=[
					   ('Content-Type', 'application/vnd.ms-excel'),
					   ('Content-Disposition',
						content_disposition(report_name + '.xlsx'))
				   ]
			   	)

				report_obj.get_payslip_excel(options, response)

			
			response.set_cookie('fileToken', token)
			return response	
		except Exception as e:
			se = http.serialize_exception(e)	

			error = {
			   'code': 200,
			   'message': 'Odoo Server Error',
			   'data': se
		   	}
			   
			return request.make_response(html_escape(json.dumps(error)))
		
	@http.route('/excel_pre_payroll_reports', type='http', auth='user', methods=['POST'], csrf=False)
	def get_excel_pre_payroll_reports(self, model, options, output_format, report_name, **kw):
		uid 			= request.session.uid
		report_obj 		= request.env[model].with_user(uid)
		options 		= json.loads(options)
		token 			= 'hellovirtus'

		try:
			if output_format == 'xlsx':
				response = request.make_response(
				   None,
				   headers=[
					   ('Content-Type', 'application/vnd.ms-excel'),
					   ('Content-Disposition',
						content_disposition(report_name + '.xlsx'))
				   ]
			   	)

				report_obj.get_pre_payroll_excel(options, response)

			
			response.set_cookie('fileToken', token)
			return response	
		except Exception as e:
			se = http.serialize_exception(e)	

			error = {
			   'code': 200,
			   'message': 'Odoo Server Error',
			   'data': se
		   	}
			   
			return request.make_response(html_escape(json.dumps(error)))
		
	@http.route('/excel_payroll_monthly_reports', type='http', auth='user', methods=['POST'], csrf=False)
	def get_excel_payroll_monthly_reports(self, model, options, output_format, report_name, **kw):
		uid 			= request.session.uid
		report_obj 		= request.env[model].with_user(uid)
		options 		= json.loads(options)
		token 			= 'hellovirtus'

		try:
			if output_format == 'xlsx':
				response = request.make_response(
				   None,
				   headers=[
					   ('Content-Type', 'application/vnd.ms-excel'),
					   ('Content-Disposition',
						content_disposition(report_name + '.xlsx'))
				   ]
			   	)

				report_obj.get_excel_payroll_monthly_reports(options, response)

			
			response.set_cookie('fileToken', token)
			return response	
		except Exception as e:
			se = http.serialize_exception(e)	

			error = {
			   'code': 200,
			   'message': 'Odoo Server Error',
			   'data': se
		   	}
			   
			return request.make_response(html_escape(json.dumps(error)))
		

	@http.route('/excel_payroll_cash_reports', type='http', auth='user', methods=['POST'], csrf=False)
	def get_excel_payroll_cash_reports(self, model, options, output_format, report_name, **kw):
		uid 			= request.session.uid
		report_obj 		= request.env[model].with_user(uid)
		options 		= json.loads(options)
		token 			= 'hellovirtus'

		try:
			if output_format == 'xlsx':
				response = request.make_response(
				   None,
				   headers=[
					   ('Content-Type', 'application/vnd.ms-excel'),
					   ('Content-Disposition',
						content_disposition(report_name + '.xlsx'))
				   ]
			   	)

				report_obj.get_excel_payroll_cash_reports(options, response)

			
			response.set_cookie('fileToken', token)
			return response	
		except Exception as e:
			se = http.serialize_exception(e)	

			error = {
			   'code': 200,
			   'message': 'Odoo Server Error',
			   'data': se
		   	}
			   
			return request.make_response(html_escape(json.dumps(error)))
		
	@http.route('/excel_payroll_employee_data_reports', type='http', auth='user', methods=['POST'], csrf=False)
	def get_excel_payroll_employee_data_reports(self, model, options, output_format, report_name, **kw):
		uid 			= request.session.uid
		report_obj 		= request.env[model].with_user(uid)
		options 		= json.loads(options)
		token 			= 'hellovirtus'

		try:
			if output_format == 'xlsx':
				response = request.make_response(
				   None,
				   headers=[
					   ('Content-Type', 'application/vnd.ms-excel'),
					   ('Content-Disposition',
						content_disposition(report_name + '.xlsx'))
				   ]
			   	)

				report_obj.get_excel_payroll_employee_data_reports(options, response)

			
			response.set_cookie('fileToken', token)
			return response	
		except Exception as e:
			se = http.serialize_exception(e)	

			error = {
			   'code': 200,
			   'message': 'Odoo Server Error',
			   'data': se
		   	}
			   
			return request.make_response(html_escape(json.dumps(error)))