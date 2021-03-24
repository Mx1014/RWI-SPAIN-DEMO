# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataHeader(models.Model):
    _name = "sincro_data.header"

    name = fields.Char(string="Name")
    value = fields.Char(string="Value")
    api_id = fields.Many2one('sincro_data.api', string="Related API")
