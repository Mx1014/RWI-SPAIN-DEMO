# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Main(models.Model):
    _name = 'sincro_data.main'

    api_list = fields.Many2one("sincro_data.server", string="APIs")