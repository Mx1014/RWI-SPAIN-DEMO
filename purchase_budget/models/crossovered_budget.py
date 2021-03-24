# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CrossoveredBudget(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "crossovered.budget"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    purchase_user_ids = fields.Many2many(string="Purchase Requestors",
        comodel_name="res.users",
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
