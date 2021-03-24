# -*- coding: utf-8 -*-

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class ReenrollmentPortal(CustomerPortal):

    def _prepare_home_portal_values(self):
        values = super(ReenrollmentPortal, self)._prepare_home_portal_values()

        values.update({
            'reenrollment_count': len(request.env.user.reenrollment_ids)
            })
        return values
