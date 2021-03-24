# See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Users(models.Model):
    _inherit = "res.users"

    reenrollment_ids = fields.One2many('adm.reenrollment', compute='compute_reenrollment_ids')

    def compute_reenrollment_ids(self):
        for user in self:
            user.reenrollment_ids = self.env['adm.reenrollment'].search([
                '|',
                ('custody_user_ids', '=', user.id),
                ('custody_partner_ids', '=', user.partner_id.id),
                ])