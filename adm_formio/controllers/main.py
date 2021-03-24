# -*- coding: utf-8 -*-
import logging
from datetime import datetime
import base64
import itertools
import re
import json
from odoo import http, _
from odoo.http import request, Response
from odoo.addons.adm.controllers.application\
    .admission_application_controller import \
    AdmissionController
from odoo.exceptions import MissingError, ValidationError

_logger = logging.getLogger(__name__)


class Admission(AdmissionController):

    @http.route("/admission/applications/"
                "<model(adm.application):application_id>/formio/email",
                auth="public", methods=["POST"], website=True, csrf=True,
                type='json')
    def send_formio_email(self, application_id, **params):
        try:
            json_request = request.jsonrequest
            email = json_request.get("email", False)
            if not email:
                raise ValidationError(_("Email shouldn't be empty!"))

            application_id.sudo().formio_sent_to_email = email
            # template_id = request.env.ref(
            # 'adm_formio.adm_application_mail_template_reference_form').id
            # request.env['adm.application'].sudo(
            # ).message_post_with_template(template_id,
            # res_id=application_id.id)
        except Exception as e:
            Response.status = "400 Bad Request"
            return e

        return "Ok"
