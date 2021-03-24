# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataLog(models.Model):
    _name = "sincro_data.log"

    url = fields.Char(string="URL", readonly=True)
    status_code = fields.Char(string="Status code", readonly=True)
    item_id = fields.Integer(string="Item ID", readonly=True)
    created_date = fields.Datetime(string="Created date", readonly=True)
    model = fields.Char(string="Model", readonly=True)
    method = fields.Char(string="Method", readonly=True)
    server_id = fields.Many2one("sincro_data.server", readonly=True)
    request = fields.Text(string="Request", readonly=True)
    response = fields.Text(string="Response", readonly=True)
