import logging
import pytz
import math

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InternalDeduction(models.Model):
	_name           = 'internal.deduction'
	_description    = "Jenis Potongan"

	name            = fields.Char(string = 'Nama')
	nilai           = fields.Float(string = 'Nilai')
	multiplier   	= fields.Selection([('none','Tidak Ada'),('wage','Gaji Pokok')], string ='Pengali')
	master_id 		= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job") 
	
class InternalLongShift(models.Model):
	_name           = 'internal.long.shift'
	_description    = "Long Shift"

	name            = fields.Char(string = 'Nama')
	nilai           = fields.Float(string = 'Nilai Pengali')
	master_id 		= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job") 
	
class InternalBackup(models.Model):
	_name           = 'internal.backup'
	_description    = "All Backup"

	name            = fields.Char(string = 'Nama')
	nilai           = fields.Float(string = 'Nilai Pengali')
	master_id 		= fields.Many2one(string = "Master Jabatan" ,comodel_name = "master.job")
	
class InternalMemoType(models.Model):
	_name           = 'internal.memo.type'
	_description    = "Jenis Internal Memo"
	
	code            = fields.Char(string = 'Kode')
	name            = fields.Char(string = 'Nama')
	type   			= fields.Selection([('overtime','Lembur'),('rapel','Potongan Rapel'),('shift','Long Shift'),('backup','All Backup'),('other','Lainnya')], string ='Jenis')
	condition   	= fields.Selection([('plus','Penambah'),('minus','Pengurangan')], string ='Kondisi')

class InternalMemo(models.Model):
	_name           = 'internal.memo'
	_description    = "Internal Memo"

	name            = fields.Char(string = 'Nama')
	type_id 		= fields.Many2one(string = "Jenis Memo" ,comodel_name = "internal.memo.type")
	
	description		= fields.Text(string ='Keterangan')
	
	date_memo       = fields.Date(string = 'Tanggal', default=datetime.today())
	creator_id      = fields.Many2one('res.users',"Pemohon")
	attachment      = fields.Binary(string='Attachment', required=False)
	action1_id   	= fields.Selection([('approve','Setujui'),('reject','Tolak')], string ='Persetujuan Ops Manager')
	date_approve1   = fields.Datetime(string = 'Tanggal Persetujuan Ops Manager')
	approve1_id     = fields.Many2one('res.users',"Nama Ops Manager")
	description1	= fields.Text(string ='Keterangan Persetujuan Ops Manager')
	action2_id   	= fields.Selection([('approve','Setujui'),('reject','Tolak')], string ='Persetujuan General Manager CFS')
	date_approve2   = fields.Datetime(string = 'Tanggal Persetujuan General Manager CFS')
	approve2_id     = fields.Many2one('res.users',"Persetujuan General Manager CFS")
	description2	= fields.Text(string ='Keterangan Persetujuan General Manager CFS')
	
	action3_id   	= fields.Selection([('approve','Setujui'),('reject','Tolak')], string ='Persetujuan Direktur of HRM')
	date_approve3   = fields.Datetime(string = 'Tanggal Persetujuan Direktur of HRM')
	approve3_id     = fields.Many2one('res.users',"Persetujuan Direktur of HRM")
	description3	= fields.Text(string ='Keterangan Persetujuan Direktur of HRM')
	

	master_id 		= fields.Many2one(string = "Jabatan" ,comodel_name = "master.job")
	date_start      = fields.Datetime(string = 'Waktu Mulai')
	date_end       	= fields.Datetime(string = 'Waktu Selesai')
	duration		= fields.Float(string= 'Durasi')
	rapel_id      	= fields.Many2one('internal.deduction',"Jenis Rapel")
	shift_id      	= fields.Many2one('internal.long.shift',"Jenis Shift")
	backup_id      	= fields.Many2one('internal.backup',"Jenis Backup")
	overtime_id     = fields.Many2one('overtime.type',"Jenis Lembur")
	duration_name   = fields.Char(string = 'Durasi')
	status   		= fields.Selection([('submit','Submitted'),('validate1','Approved By Ops Manager'),('rejected1','Rejected By Ops Manager'),('validate2','Approved By General Manager CFS'),('rejected2','Rejected By General Manager CFS'),('validate','Approved By Direktur of HRM'),('rejected','Rejected By Direktur of HRM')], String ='Status', default ='submit')
	
	hide_overtime 	= fields.Boolean(string='Hide Overtime')
	hide_rapel 		= fields.Boolean(string='Hide Rapel')
	hide_shift 		= fields.Boolean(string='Hide Shift')
	hide_backup     = fields.Boolean(string='Hide Backup')
	hide_total      = fields.Boolean(string='Hide Total')

	employee_ids 	= fields.One2many(comodel_name='internal.memo.employee',inverse_name='memo_id',string='Pegawai')

	@api.onchange('action1_id')
	def _onchange_action1(self):
		if self.action1_id == 'approve':
			self.status = 'validate1'
		else:
			self.status = 'rejected1'

	@api.onchange('action2_id')
	def _onchange_action2(self):
		if self.action2_id == 'approve':
			self.status = 'validate2'
		else:
			self.status = 'rejected2'

	@api.onchange('action3_id')
	def _onchange_action3(self):
		if self.action3_id == 'approve':
			self.status = 'validate'
		else:
			self.status = 'rejected'

	def write(self, values):
		_logger = logging.getLogger(__name__)
		current_datetime 	= datetime.today()

		user_id   = self.env.uid
		#_logger.error('TEST HALO')
		#_logger.error(values)
		#_logger.error(self.action3_id)
		#raise UserError(str(self.action1_id)+' '+str(self.action2_id)+' '+str(self.action3_id))

		if str(values.get('action3_id')) != 'None' and str(values.get('action3_id')) != 'False':
			if values.get('action3_id') == 'approve':
				values['status'] = 'validate'
			else:
				values['status'] = 'rejected'

			values['approve3_id'] 	=  user_id
			values['date_approve3'] =  current_datetime
		elif str(self.action3_id) != 'None' and str(self.action3_id) != 'False':
			if self.action3_id == 'approve':
				values['status'] = 'validate'
			else:
				values['status'] = 'rejected'

			values['approve3_id'] 	=  user_id
			values['date_approve3'] =  current_datetime
		elif str(values.get('action2_id')) != 'None' and str(values.get('action2_id')) != 'False':
			if values.get('action2_id') == 'approve':
				values['status'] = 'validate2'
			else:
				values['status'] = 'rejected2'

			values['approve2_id'] =  user_id
			values['date_approve2'] =  current_datetime
		elif str(self.action2_id) != 'None' and str(self.action2_id) != 'False':
			if self.action2_id == 'approve':
				values['status'] = 'validate2'
			else:
				values['status'] = 'rejected2'

			values['approve2_id'] 	=  user_id
			values['date_approve2'] =  current_datetime
		elif str(values.get('action1_id')) != 'None' and str(values.get('action1_id')) != 'False':
			if values.get('action1_id') == 'approve':
				values['status'] = 'validate1'
			else:
				values['status'] = 'rejected1'

			values['approve1_id'] =  user_id
			values['date_approve1'] =  current_datetime
		elif str(self.action1_id) != 'None' and str(self.action1_id) != 'False':
			
			if self.action1_id == 'approve':
				values['status'] = 'validate1'
			else:
				values['status'] = 'rejected1'

			values['approve1_id'] 	=  user_id
			values['date_approve1'] =  current_datetime


		return super(InternalMemo, self).write(values)
	
	def unlink(self):
		for record in self:
			if record.status != 'submit':
				raise UserError('Tidak dapat menghapus data yang statusnya bukan diajukan pemohon')
	
	@api.onchange('date_start')
	def _onchange_date_start(self):
		if self.overtime_id.id != False:
			type_info = self.env['overtime.type'].sudo().search_read([('id','=', self.overtime_id.id)],['code','name','overtime_tipe'])

			if len(type_info) > 0:
				for typ in type_info:
					type_type = typ['overtime_tipe']

			# duration based on type info
			if type_type == 'hour':
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_hours				= self.date_end - self.date_start
					overtime_div_hours 			= (overtime_hours.days*24) + (overtime_hours.seconds / 3600)

					self.duration 		= math.floor(overtime_div_hours)
					self.duration_name	= str(self.duration)+' jam'
			else:
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_days				= self.date_end.date() - self.date_start.date() 
					self.duration				= overtime_days.days + 1
					self.duration_name			= str(self.duration)+' hari'

	@api.onchange('date_end')
	def _onchange_date_end(self):
		if self.overtime_id.id != False:
			type_info = self.env['overtime.type'].sudo().search_read([('id','=', self.overtime_id.id)],['code','name','overtime_tipe'])

			if len(type_info) > 0:
				for typ in type_info:
					type_type = typ['overtime_tipe']

			# duration based on type info
			if type_type == 'hour':
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_hours				= self.date_end - self.date_start
					overtime_div_hours 			= (overtime_hours.days*24) + (overtime_hours.seconds / 3600)

					self.duration 		= math.floor(overtime_div_hours)
					self.duration_name	= str(self.duration)+' jam'
			else:
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_days				= self.date_end.date() - self.date_start.date() 
					self.duration				= overtime_days.days + 1
					self.duration_name			= str(self.duration)+' hari'

	@api.onchange('overtime_id')
	def _onchange_overtime_id(self):
		if self.overtime_id.id != False:
			type_info = self.env['overtime.type'].sudo().search_read([('id','=', self.overtime_id.id)],['code','name','overtime_tipe'])

			if len(type_info) > 0:
				for typ in type_info:
					type_type = typ['overtime_tipe']

			# duration based on type info
			if type_type == 'hour':
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_hours				= self.date_end - self.date_start
					overtime_div_hours 			= (overtime_hours.days*24) + (overtime_hours.seconds / 3600)

					self.duration 		= math.floor(overtime_div_hours)
					self.duration_name	= str(self.duration)+' jam'
			else:
				if str(self.date_start) != 'False' and str(self.date_end) != 'False': 
					overtime_days				= self.date_end.date() - self.date_start.date() 
					self.duration				= overtime_days.days + 1
					self.duration_name			= str(self.duration)+' hari'

			 

	@api.onchange('type_id')
	def _onchange_type_id(self):
		if self.type_id.type == 'overtime':
			self.hide_overtime 	= False
			self.hide_rapel 	= True
			self.hide_shift 	= True
			self.hide_backup 	= True
			self.hide_total 	= True
		elif self.type_id.type == 'rapel':
			self.hide_overtime 	= True
			self.hide_rapel 	= False
			self.hide_shift 	= True
			self.hide_backup 	= True
			self.hide_total 	= False
		elif self.type_id.type == 'shift':
			self.hide_overtime 	= True
			self.hide_rapel 	= True
			self.hide_shift 	= False
			self.hide_backup 	= True
			self.hide_total 	= True
		elif self.type_id.type == 'backup':
			self.hide_overtime 	= True
			self.hide_rapel 	= True
			self.hide_shift 	= True
			self.hide_backup 	= False
			self.hide_total 	= True
		else:
			self.hide_overtime = True
			self.hide_rapel 	= True
			self.hide_shift 	= True
			self.hide_backup 	= True
			self.hide_total 	= False

	# base on create user
	@api.model_create_multi
	def create(self, values):
		_logger = logging.getLogger(__name__)

		# struktur id harus di set ulang
		for val in values:
			val['creator_id'] = self.env.user.id

		return super(InternalMemo, self).create(values)


class InternalMemoEmployee(models.Model):
	_name           = 'internal.memo.employee'
	_description    = "Internal Memo Employee"

	name            = fields.Char(string = 'Info Tambahan', default='-')
	memo_id 		= fields.Many2one(string = "Internal Memo" ,comodel_name = "internal.memo")
	employee_id 	= fields.Many2one(string = "Pegawai" ,comodel_name = "hr.employee", required = True)
	unit_id      	= fields.Many2one('hr.work.location',"Lokasi Kerja")
	position_id     = fields.Many2one('master.job',"Jabatan")
	total_amount	= fields.Integer(string= 'Total Nilai')