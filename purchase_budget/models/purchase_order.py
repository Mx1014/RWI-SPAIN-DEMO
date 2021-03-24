# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    ######################
    # Private attributes #
    ######################
    _inherit = "purchase.order"

    ###################
    # Default methods #
    ###################

    ######################
    # Fields declaration #
    ######################
    budget_id = fields.Many2one(string="Budget",
        comodel_name="crossovered.budget")
    require_budget = fields.Boolean(string="Require Budget",
        related="user_id.purchase_require_budget")
    budget_warning_message = fields.Html(string="Budget Warning Message",
        compute="_compute_budget_warning")

    ##############################
    # Compute and search methods #
    ##############################
    def _compute_budget_warning(self):
        for order in self:
            budget_warning_message = ""
            for budget_line in order.budget_id.crossovered_budget_line:
                remaining_budget = -budget_line.planned_amount + budget_line.practical_amount
                purchase_lines = order.order_line.filtered(lambda x: budget_line.general_budget_id == x.budget_post_id)
                total = remaining_budget - sum(purchase_lines.mapped("price_subtotal"))
                if total < 0:
                    budget_warning_message += """
                        <tr>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                            <td>%s</td>
                        </tr>
                    """ % (
                        budget_line.general_budget_id.name,
                        budget_line.date_from,
                        budget_line.date_to,
                        budget_line.planned_amount,
                        budget_line.practical_amount,
                    )
            if budget_warning_message:
                budget_warning_message = """
                    <div class="alert alert-danger" role="alert">
                        <i class="fa fa-exclamation-triangle"/>
                        <span>The following budget lines will be exceeded when this purchase is pushed through</span>
                        <table class="table table-bordered table-sm">
                            <tr>
                                <th>Position</th>
                                <th>Start Date</th>
                                <th>End Date Date</th>
                                <th>Planned Amount</th>
                                <th>Practical Amount</th>
                            </tr>
                            %s
                        </table>
                    </div>
                """ % budget_warning_message
            order.budget_warning_message = budget_warning_message

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
