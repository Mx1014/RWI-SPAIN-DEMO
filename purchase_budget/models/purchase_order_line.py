# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "purchase.order.line"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    budget_post_id = fields.Many2one(string="Budget Position",
        comodel_name="account.budget.post")

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################
    @api.onchange("product_id")
    def _onchange_unset_budget_post_id(self):
        self.budget_post_id = False

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
