# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    advance_journal_id = fields.Many2one(string="Advance Journal",
        related="company_id.advance_journal_id",
        comodel_name="account.journal",
        readonly=False)
    advance_bank_journal_id = fields.Many2one(string="Advance Bank Journal",
        related="company_id.advance_bank_journal_id",
        comodel_name="account.journal",
        readonly=False)
    advance_product_id = fields.Many2one(string="Advance Product",
        related="company_id.advance_product_id",
        comodel_name="product.product",
        readonly=False)