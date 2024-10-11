# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CustomState(models.Model):
	_inherit = "res.country.state"
	
	ump   = fields.Integer(string='UMP', required = True)
