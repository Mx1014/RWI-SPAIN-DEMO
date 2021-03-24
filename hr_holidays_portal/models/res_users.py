#-*- coding:utf-8 -*-

from odoo import models, fields, api, tools

class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def has_group(self, group_ext_id):
        if self._context.get("has_group_return_true") and group_ext_id == "hr_holidays.group_hr_holidays_user":
            return True
        else:
            return super(ResUsers, self).has_group(group_ext_id)

    @api.model
    @tools.ormcache('self._uid', 'group_ext_id')
    def _has_group(self, group_ext_id):
        return super(ResUsers, self)._has_group(group_ext_id)

    has_group.clear_cache = _has_group.clear_cache