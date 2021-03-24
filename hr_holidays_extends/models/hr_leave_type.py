#-*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api

class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    consecutive_restriction = fields.Selection(string="Cannot be Consecutive With",
        selection=[
            ("same","Same Type"),
            ("other","Other Type"),
            ("any","Any Type")])
    prior_notice = fields.Integer(string="Prior Notice",
        help="Latest date to request leave is: leave date - prior notice (e.g. 1 means day before)")
    
    def _get_minimum_date_from(self, datetime=False):
        self.ensure_one()
        result = False
        if self.prior_notice:
            result = fields.Datetime.now() + relativedelta(days=self.prior_notice)
        if result and not datetime:
            result = fields.Date.context_today(self, result)
        return result
    
    def _get_maximum_date_to(self, date_from, datetime=False):
        self.ensure_one()

        if type(date_from) == str:
            date_from = fields.Datetime.from_string(date_from)

        result = False
        if self.consecutive_restriction in ["same", "any"]:
            result = date_from
        if result and not datetime:
            result = fields.Date.context_today(self, result)
        return result