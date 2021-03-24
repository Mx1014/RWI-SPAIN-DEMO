# -*- coding:utf-8 -*-

from odoo import models, fields, api


class SincroDataParameter(models.Model):
    _name = "sincro_data.parameter"
    _order = "sequence"

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(readonly=True, default=-1)
    type = fields.Selection([
        ('constant', "CONSTANT"),
        ('dinamyc', 'Variable')],string="Type", required=True)
    constant_value = fields.Char(string="Name")
    request_id = fields.Many2one('sincro_data.server', string='Request')
    field_value = fields.Many2one('ir.model.fields', string='Field')

