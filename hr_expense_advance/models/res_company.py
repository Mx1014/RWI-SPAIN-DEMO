# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = "res.company"

    advance_journal_id = fields.Many2one(string="Advance Journal",
        comodel_name="account.journal")
    advance_bank_journal_id = fields.Many2one(string="Advance Bank Journal",
        comodel_name="account.journal")
    advance_product_id = fields.Many2one(string="Advance Product",
        comodel_name="product.product")