import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class InternalSetting(models.Model):
	_name           = 'internal.memo.setting'
	_description    = "Setting"

	code            = fields.Char(string = 'Code')
	name            = fields.Char(string = 'Name')
	value           = fields.Char(string = 'Value')

class Company(models.Model):
    _inherit = 'res.company'
    
    recruitment_email = fields.Char(string="Recruitment E-mail")

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    recruitment_email = fields.Char(related="company_id.recruitment_email", readonly=False, string="Recruitment E-mail")
