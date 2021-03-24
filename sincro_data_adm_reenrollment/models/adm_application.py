# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError

from ..utils.commons import switch_statement


class Admission(models.Model):
    """ We inherit to enable School features for contacts """
    _inherit = "adm.application"

    update_state_id = fields.Many2one('update.state', String="Update State")
    is_success = fields.Boolean()
    is_warning = fields.Boolean()
    is_error = fields.Boolean()
    comment = fields.Char()
