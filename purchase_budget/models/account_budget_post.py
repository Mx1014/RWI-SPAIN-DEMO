# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountBudgetPost(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "account.budget.post"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################

    ##############################
    # Compute and search methods #
    ##############################
    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if "product_id" in self.env.context and "budget_id" in self.env.context:
            product_id = self.env.context["product_id"]
            budget_id = self.env.context["budget_id"]
            if not product_id or not budget_id:
                args = [("id","=",False)]
            else:
                product_obj = self.env["product.product"]
                budget_obj = self.env["crossovered.budget"]
                product = product_obj.browse(product_id)
                account = product.product_tmpl_id.get_product_accounts()["expense"]
                budget = budget_obj.browse(budget_id)
                budget_posts = budget.crossovered_budget_line.filtered(lambda x: x.general_budget_id).mapped("general_budget_id")
                budget_posts = budget_posts.filtered(lambda x: account in x.account_ids)
                if budget_posts:
                    args = [("id","in",budget_posts.ids)]
                else:
                    args = [("id","=",False)]
        return super(AccountBudgetPost, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

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
