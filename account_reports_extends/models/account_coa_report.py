# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountCoaReport(models.AbstractModel):
    _inherit = "account.coa.report"

    filter_show_empty_accounts = False

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super(AccountCoaReport, self)._get_lines(options, line_id=line_id)
        new_lines = []
        if options.get("show_empty_accounts"):
            extra_periods = len(options.get("comparison", {}).get("periods") or [])
            filler_base_vals = {
                "caret_options": "account.account",
                "columns": []
            }
            for i in range((3 + extra_periods) * 2):
                filler_base_vals["columns"].append({"class": "number", "name": "", "no_format_name": 0.0})

            lines_dict = {}
            for line in lines:
                lines_dict[line["id"]] = line

            all_accounts = self.env["account.account"].search([])
            for account in all_accounts:
                if account.id in lines_dict:
                    new_lines.append(lines_dict[account.id])
                else:
                    filler_vals = dict(filler_base_vals)
                    filler_vals.update({
                        "id": account.id,
                        "name": account.display_name,
                        "title_hover": account.display_name,
                        "unfoldable": False,
                    })
                    new_lines.append(filler_vals)

            if lines:
                new_lines.append(lines.pop())

        return new_lines or lines