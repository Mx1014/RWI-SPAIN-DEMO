#-*- coding:utf-8 -*-

from odoo import models, fields, api

class HrLeave(models.Model):
    _inherit = "hr.leave"

    pullback_comment = fields.Text(string="Pullback Comment")

    def write(self, vals):
        return super(HrLeave, self.with_context(has_group_return_true=True)).write(vals)