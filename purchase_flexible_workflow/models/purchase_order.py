# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["purchase.order", "workflow.mixin"]