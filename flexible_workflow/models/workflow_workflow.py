# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class WorkflowWorkflow(models.Model):
    _name = "workflow.workflow"
    _description = "Workflow"
    _rec_name = "model_id"

    model_id = fields.Many2one(string="Model",
        comodel_name="ir.model",
        required=True,
        readonly=True)
    stage_ids = fields.One2many(string="Stages",
        comodel_name="workflow.stage",
        inverse_name="workflow_id")
    
    _sql_constraints = [
        ("model_uniq", "unique (model_id)", "The model must be unique!")
    ]