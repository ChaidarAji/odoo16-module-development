# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Channel(models.Model):
    _inherit = 'mail.channel'

    pos_categ_ids = fields.Many2many("pos.category", string="Category")