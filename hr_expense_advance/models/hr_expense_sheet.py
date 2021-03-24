# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, MissingError, ValidationError

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.onchange("expense_line_ids")
    def _onchange_expense_line_ids(self):
        for sheet in self:
            if sheet.expense_line_ids and sheet.expense_line_ids[0].advance_id:
                if not sheet.company_id.advance_bank_journal_id:
                    raise MissingError("Cannot find default bank journal to use for Advances. Set in Expense settings")
                sheet.bank_journal_id = sheet.company_id.advance_bank_journal_id.id

    @api.constrains("expense_line_ids")
    def _check_expense_line_ids_for_advance(self):
        for sheet in self:
            if any(expense.advance_id for expense in sheet.expense_line_ids) and \
                not all(expense.advance_id for expense in sheet.expense_line_ids):
                raise UserError("You cannot report expenses linked with Advance with those that are not")