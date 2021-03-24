#-*- coding:utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import MissingError

class FormioAutomationMapping(models.Model):
    _name = "formio.automation.mapping"
    _description = "Formio Automation Mapping"

    form_field_key = fields.Char(string="Form Field Key",
        required=True)
    object_field_name = fields.Char(string="Object Field Name",
        required=True)
    automation_id = fields.Many2one(string="Formio Automation",
        required=True,
        ondelete="cascade")