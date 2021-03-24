# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class ResGroups(models.Model):
    _inherit = "res.groups"

    hide_menu_access = fields.Many2many(string="Show Only",
        comodel_name="ir.ui.menu",
        relation="ir_ui_menu_hide_group_rel")
    limit_menu_access = fields.Many2many(string="Hidden",
        comodel_name="ir.ui.menu",
        relation="ir_ui_menu_limit_group_rel")