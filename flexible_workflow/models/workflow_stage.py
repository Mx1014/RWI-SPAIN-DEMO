# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

class WorkflowStage(models.Model):
    _name = "workflow.stage"
    _description = "Workflow Stage"
    _order = "sequence"

    name = fields.Char(string="Name",
        required=True)
    sequence = fields.Integer(string="Sequence")
    workflow_id = fields.Many2one(string="Workflow",
        comodel_name="workflow.workflow",
        required=True,
        ondelete="cascade")
    group_ids = fields.Many2many(string="Groups",
        comodel_name="res.groups")
    user_ids = fields.Many2many(string="Users",
        comodel_name="res.users")
    attribute_ids = fields.One2many(string="Attributes",
        comodel_name="workflow.attribute",
        inverse_name="stage_id")
    skip_check = fields.Text(string="Skip Check")

    def check_skip(self, record):
        self.ensure_one()
        result = False
        if self.skip_check:
            localdict = {"record": record.sudo()}
            try:
                safe_eval(self.skip_check, localdict, mode="exec", nocopy=True)
                result = localdict["result"] or False
            except:
                raise UserError("Error in python code for stage: " + self.name)
        return result
