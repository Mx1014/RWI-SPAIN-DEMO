#-*- coding:utf-8 -*-

from odoo import models, fields, api

class CrossoveredBudgetLines(models.Model):
    _inherit = "crossovered.budget.lines"

    variance_amount = fields.Monetary(string="Variance Amount",
        compute="_compute_variance")
    variance_percentage = fields.Float(string="Variance %",
        compute="_compute_variance")
    enable_variance_warning = fields.Boolean(string="Enable Variance Warning")
    variance_percentage_warning = fields.Float(string="Variance % Warning",
        help="Creates an activity for the resposible user if the")
    variance_warning_sent = fields.Boolean(string="Variance Warning Sent")

    def _compute_variance(self):
        for line in self:
            line.variance_amount = line.planned_amount - line.practical_amount
            if line.planned_amount != 0:
                line.variance_percentage = line.variance_amount / line.planned_amount
            else:
                line.variance_percentage = 0
