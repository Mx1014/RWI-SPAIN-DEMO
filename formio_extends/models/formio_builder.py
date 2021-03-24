#-*- coding:utf-8 -*-

from odoo import models, fields, api

class FormioBuilder(models.Model):
    _inherit = "formio.builder"

    public_access_expire_on_submit = fields.Boolean(string="Expire on Submit")