# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmAisjApplicantPrograms(models.Model):
    _name = 'adm_aisj.applicant.programs'
    _description = "Applicant programs"

    name = fields.Char(string="Name", required=True)
