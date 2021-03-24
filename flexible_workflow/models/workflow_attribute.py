# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class WorkflowAttribute(models.Model):
    _name = "workflow.attribute"
    _description = "Workflow Attribute"

    def name_get(self):
        result = []
        for attribute in self:
            name = attribute.type + " " + attribute.expression
            result.append((attribute.id, name))
        return result

    type = fields.Selection(string="Type",
        required=True,
        selection=[
            ("invisible", "Invisible")],
        default="invisible")
    expression = fields.Char(string="Expression",
        required=True)
    stage_id = fields.Many2one(string="Stage",
        comodel_name="workflow.stage",
        required=True,
        ondelete="cascade")