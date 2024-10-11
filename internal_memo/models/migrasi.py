import logging
import pytz
import math

from collections import namedtuple, defaultdict

from datetime import datetime, timedelta, time
from pytz import timezone, UTC
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MigrasiProses(models.Model):
	_name           = 'migrasi.proses'
	_description    = "Proses Migrasi"

	name            = fields.Char(string = 'Proses')
	code            = fields.Char(string = 'Kode')
	ordering        = fields.Integer(string='Order', index = True)
	status          = fields.Selection([('idle','Idle'),('progress','On Progress'),('done','Done')])
	

class MigrasiProsesLog(models.Model):
	_name           = 'migrasi.proses.log'
	_description    = "Log Proses Migrasi"
	
	name            = fields.Char(string='Description')