# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class HrExpenseAdvanceLine(models.Model):
    _name = "hr.expense.advance.line"
    _description = "Expense Advance Line"

    name = fields.Char(string="Description",
        required=True)
    advance_id = fields.Many2one(string="Advance Reference",
        comodel_name="hr.expense.advance",
        required=True,
        ondelete="cascade")
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        related="advance_id.currency_id",
        store=True)
    estimated_amount = fields.Monetary(string="Estimated Amount")