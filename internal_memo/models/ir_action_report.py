# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from markupsafe import Markup

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval, time
from odoo.tools.misc import find_in_path, ustr
from odoo.tools import check_barcode_encoding, config, is_html_empty, parse_version
from odoo.http import request
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS, FALSE_DOMAIN

import io
import logging
import os
import lxml.html
import tempfile
import subprocess
import re
import json
from io import BytesIO

from lxml import etree
from contextlib import closing
from reportlab.graphics.barcode import createBarcodeDrawing
from PyPDF2 import PdfFileWriter, PdfFileReader
from collections import OrderedDict
from collections.abc import Iterable
from PIL import Image, ImageFile

import time
import datetime
from datetime import date
from datetime import datetime, date, time

# Allow truncated images
ImageFile.LOAD_TRUNCATED_IMAGES = True

try:
	from PyPDF2.errors import PdfReadError
except ImportError:
	from PyPDF2.utils import PdfReadError

_logger = logging.getLogger(__name__)

class IrActionsReport(models.Model):
	_inherit = "ir.actions.report"

	def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
		document, ttype = super()._render_qweb_pdf(
			report_ref, res_ids=res_ids, data=data
		)
		report = self._get_report(report_ref)
		if res_ids:
			#_logger.error('CHECK RESOURCE')
			#_logger.error(res_ids)
			encrypt_password = False
			#raise UserError(report.report_name)

			if report.report_name == 'internal_memo.report_payslip_custom_id3_internal':
				encrypt_password 	= True
				
				report 				= self._get_report_from_name(report.report_name).with_context(
					encrypt_password=encrypt_password
				)
				# password is from payslip
				payslip_info = self.env['hr.payslip'].sudo().search([('id','in',res_ids)])

				password = '1234'

				if len(payslip_info) > 0:
					for pays in payslip_info:
						nip 		= pays.employee_id.nip
						birthday 	= pays.employee_id.birthday

						d = birthday.strftime('%Y-%m-%d')

						date = datetime.strptime(d,"%Y-%m-%d")
						day = date.day
						
						#raise UserError(str(day))
						# password dua digit akhir NIP dan tgl lahir
						string_length 	= len(nip)
						last_two_digit 	= string_length - 2

						if pays.employee_id.pin !='' and pays.employee_id.pin != False:
							password 		= pays.employee_id.pin
						


				#password = report._get_pdf_password(res_ids[:1])
				
				document = self._encrypt_pdf(document, password)
		return document, ttype
	
	def _encrypt_pdf(self, data, password):
		if not password:
			return data
		
		output_pdf = PdfFileWriter()
		in_buff = BytesIO(data)
		pdf = PdfFileReader(in_buff)
		output_pdf.appendPagesFromReader(pdf)
		output_pdf.encrypt(password)
		buff = BytesIO()
		output_pdf.write(buff)
		return buff.getvalue()
