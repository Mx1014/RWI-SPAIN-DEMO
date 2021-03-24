# -*- coding: utf-8 -*-

from odoo.addons.auth_signup.controllers.main import AuthSignupHome

from odoo import _
from odoo.exceptions import UserError
from odoo.http import request


class AdmAisjAuthSignupHome(AuthSignupHome):

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        first_name = qcontext.get('first_name', False)
        last_name = qcontext.get('last_name', False)

        full_name = request.env['res.partner'].format_name(first_name, '', last_name)

        qcontext['name'] = qcontext.get('name', full_name)
        super(AdmAisjAuthSignupHome, self).do_signup(qcontext)
        request.env.user.write({
            'first_name': first_name,
            'last_name': last_name,
            })

    def _signup_with_values(self, token, values):
        super(AdmAisjAuthSignupHome, self)._signup_with_values(token, values)
        print('hola')
