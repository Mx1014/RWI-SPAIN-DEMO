# -*- coding:utf-8 -*-

from odoo import models, fields, api


class FullFabricClass(models.Model):
    _name = "sincro_data.class"
    _description = "Full Fabric Class"

    name = fields.Char(string="ID",
                       required=True)
    program_id = fields.Many2one(string="Degree Program",
                                 comodel_name="adm.degree_program",
                                 required=True)
