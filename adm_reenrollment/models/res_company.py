# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def_ren_enrollment_status_id = fields.Many2one('school_base.enrollment.status')
    def_ren_next_enrollment_status_id = fields.Many2one('school_base.enrollment.status')
