# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdmReenrollment(models.Model):
    _inherit = 'adm.reenrollment'

    student_iqama_document = fields.Binary(related='partner_id.iqama_document_file', string="Copy of the Student's Iqama", readonly=False)
    student_iqama_document_name = fields.Char(related='partner_id.iqama_document_file_name', readonly=False)

    guardian_iqama_document = fields.Binary(related='responsible_user_id.iqama_document_file', string="Copy of the Guardian's Iqama", readonly=False)
    guardian_iqama_document_name = fields.Char(related='responsible_user_id.iqama_document_file_name', readonly=False)
