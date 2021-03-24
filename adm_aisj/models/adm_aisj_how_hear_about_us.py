# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmAisjHowHearAboutUs(models.Model):
    _name = 'adm_aisj.how.hear.about.us'
    _description = "How about us"

    name = fields.Char(string="Name", required=True)
