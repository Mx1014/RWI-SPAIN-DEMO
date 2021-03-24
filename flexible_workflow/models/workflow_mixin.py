# -*- coding: utf-8 -*-

from odoo import models, api, fields
from odoo.exceptions import UserError, AccessError

class WorkflowMixin(models.AbstractModel):
    _name = "workflow.mixin"
    _description = "Workflow Mixin"

    workflow_stage_id = fields.Many2one(string="Workflow Stage",
        comodel_name="workflow.stage",
        tracking=True)
    prev_workflow_stage_id = fields.Many2one(string="Previous Workflow Stage",
        comodel_name="workflow.stage",
        compute="_compute_prev_workflow_stage_id")
    next_workflow_stage_id = fields.Many2one(string="Next Workflow Stage",
        comodel_name="workflow.stage",
        compute="_compute_next_workflow_stage_id")
    is_workflow_stage_user = fields.Boolean(string="Is Workflow Stage User",
        compute="_compute_is_workflow_stage_user",
        search="_search_is_workflow_stage_user")

    def _compute_prev_workflow_stage_id(self):
        for rec in self:
            result = False
            if rec.workflow_stage_id:
                stage_ids = rec.workflow_stage_id.workflow_id.stage_ids.ids
                current_stage_index = stage_ids.index(rec.workflow_stage_id.id)
                if current_stage_index > 0:
                    stage_obj = self.env["workflow.stage"]
                    prev_stage_index = current_stage_index - 1
                    prev_stage = stage_obj.browse(stage_ids[prev_stage_index])
                    if prev_stage.check_skip(rec):
                        if prev_stage_index > 0:
                            prev_stage_index -= 1
                        else:
                            rec.prev_workflow_stage_id = False
                            continue
                    result = stage_ids[prev_stage_index]
            rec.prev_workflow_stage_id = result

    def _compute_next_workflow_stage_id(self):
        for rec in self:
            result = False
            if rec.workflow_stage_id:
                stage_ids = rec.workflow_stage_id.workflow_id.stage_ids.ids
                current_stage_index = stage_ids.index(rec.workflow_stage_id.id)
                if current_stage_index < (len(stage_ids) - 1):
                    stage_obj = self.env["workflow.stage"]
                    next_stage_index = current_stage_index + 1
                    next_stage = stage_obj.browse(stage_ids[next_stage_index])
                    if next_stage.check_skip(rec):
                        if next_stage_index < (len(stage_ids) - 1):
                            next_stage_index += 1
                        else:
                            rec.next_workflow_stage_id = False
                            continue
                    result = next_stage_index and stage_ids[next_stage_index]
            rec.next_workflow_stage_id = result

    def _compute_is_workflow_stage_user(self):
        for rec in self:
            result = True
            group_allow = False
            user_allow = False
            if rec.workflow_stage_id.group_ids:
                group_allow = bool(rec.workflow_stage_id.group_ids & self.env.user.groups_id)
            if rec.workflow_stage_id.user_ids:
                user_allow = bool(rec.workflow_stage_id.user_ids & self.env.user)
            if not ((not rec.workflow_stage_id.group_ids and not rec.workflow_stage_id.user_ids) or group_allow or user_allow):
                result = False
            if not rec.workflow_stage_id.group_ids and not rec.workflow_stage_id.user_ids:
                result = False
            rec.is_workflow_stage_user = result

    def _search_is_workflow_stage_user(self, operator, value):
        ids = self.sudo().search([]).filtered(lambda x: x.is_workflow_stage_user == value).ids
        domain_operator = "in" if operator == "=" else "not in"
        return [("id", domain_operator, ids)]

    def action_next_workflow_stage(self):
        self.ensure_one()
        if not self.workflow_stage_id:
            raise UserError("Record is currently not in any stage")
        if not self.next_workflow_stage_id:
            raise UserError("This is already in the last stage of the workflow")
        self._check_access()
        self.workflow_stage_id = self.next_workflow_stage_id.id

    def action_prev_workflow_stage(self):
        self.ensure_one()
        if not self.workflow_stage_id:
            raise UserError("Record is currently not in any stage")
        if not self.prev_workflow_stage_id:
            raise UserError("This is already in the first stage of the workflow")
        self._check_access()
        self.workflow_stage_id = self.prev_workflow_stage_id.id
    
    def _check_access(self):
        self.ensure_one()
        group_allow = False
        user_allow = False
        message = ""
        if self.workflow_stage_id.group_ids:
            group_allow = bool(self.workflow_stage_id.group_ids & self.env.user.groups_id)
            message += "\nGroups: " + ", ".join(self.workflow_stage_id.group_ids.mapped("full_name"))
        if self.workflow_stage_id.user_ids:
            user_allow = bool(self.workflow_stage_id.user_ids & self.env.user)
            message += "\nUsers: " + ", ".join(self.workflow_stage_id.user_ids.mapped("name"))
        if not ((not self.workflow_stage_id.group_ids and not self.workflow_stage_id.user_ids) or group_allow or user_allow):
            raise AccessError("Only the following can change stage from the current stage:" + message)

    @api.model
    def default_get(self, fields):
        res = super(WorkflowMixin, self).default_get(fields)
        workflow = self.env["workflow.workflow"].search([("model_id","=",self.env["ir.model"]._get(self._name).id)])
        if workflow:
            res["workflow_stage_id"] = workflow.stage_ids and workflow.stage_ids[0].id or False
        return res