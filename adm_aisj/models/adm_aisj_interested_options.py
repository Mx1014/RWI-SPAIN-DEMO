# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmAisjInterestedOptions(models.Model):
    _name = 'adm_aisj.interested.options'
    _description = "Interested options"

    name = fields.Char(string="Name", required=True)
