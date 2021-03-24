#-*- coding:utf-8 -*-

from odoo import models, fields, api

class FormioForm(models.Model):
    _inherit = "formio.form"

    reference = fields.Reference(string="Reference",
        selection=[])
