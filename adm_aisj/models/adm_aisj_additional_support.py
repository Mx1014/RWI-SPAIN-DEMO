# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmAisjAdditionalSupport(models.Model):
    _name = 'adm_aisj.additional.support'
    _description = "Additional support"

    name = fields.Char(string="Name", required=True)
