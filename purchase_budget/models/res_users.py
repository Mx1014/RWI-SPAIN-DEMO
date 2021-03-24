# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResUsers(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "res.users"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    purchase_require_budget = fields.Boolean(string="Require Budget on Purchase")
    purchase_budget_ids = fields.Many2many(string="Purchase Budgets",
        comodel_name="crossovered.budget",
        relation="crossovered_budget_res_users_rel")

    ##############################
    # Compute and search methods #
    ##############################

    ############################
    # Constrains and onchanges #
    ############################

    #########################
    # CRUD method overrides #
    #########################

    ##################
    # Action methods #
    ##################

    ####################
    # Business methods #
    ####################
