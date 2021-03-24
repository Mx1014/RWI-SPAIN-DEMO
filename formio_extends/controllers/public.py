#-*- coding:utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.addons.formio.controllers.public import FormioPublicController

class FormioPublicController(FormioPublicController):

    @http.route('/formio/public/form/<string:uuid>', type='http', auth='public', website=True)
    def public_form_root(self, uuid, **kwargs):
        form = self._get_public_form(uuid, self._check_public_form())
        if form and form.builder_id.public_access_expire_on_submit and form.state == "COMPLETE":
            return request.redirect("/form-submission-thankyou")
        return super(FormioPublicController, self).public_form_root(uuid, **kwargs)