# -*- coding: utf-8 -*-

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

from odoo.http import request


class AdmReenrollmentSignupController(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        super(AdmReenrollmentSignupController, self).do_signup(qcontext)

        user_id = request.env.user
        email = user_id.email
        enrollment_partner = request.env['adm.reenrollment'].sudo().search([
            ('custody_partner_ids.email', 'ilike', email)
            ]).mapped('custody_partner_ids').filtered_domain([('email', 'ilike', email)])[:1]
        if enrollment_partner:
            user_id.write({
                'partner_id': enrollment_partner.id
                })
        request.env.cr.commit()

    def _signup_with_values(self, token, values):
        super(AdmReenrollmentSignupController, self)._signup_with_values(token, values)