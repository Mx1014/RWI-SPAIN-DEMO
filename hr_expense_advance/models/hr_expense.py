# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, MissingError, ValidationError

class HrExpense(models.Model):
    _inherit = "hr.expense"

    advance_id = fields.Many2one(string="Advance",
        comodel_name="hr.expense.advance",
        domain="[('employee_id','=',employee_id),('payment_state','=','to_close')]")
    payment_mode = fields.Selection(selection_add=[("company_account", "Company or Advance")])
    supplier_id = fields.Many2one(string="Vendor",
        comodel_name="res.partner")
    advance_expense_bill_id = fields.Many2one(string="Expense Bill",
        comodel_name="account.move",
        readonly=True)

    @api.onchange("advance_id")
    def _onchange_advance_id(self):
        for expense in self:
            expense.account_id = expense.advance_id.journal_id.default_debit_account_id.id

    @api.constrains("total_amount", "advance_id")
    def _check_advance_total_amount(self):
        for expense in self:
            if expense.advance_id and expense.total_amount >= 0:
                raise UserError("Amount should be negative if paid by an Advance")

    @api.onchange("employee_id")
    def _onchange_reset_advance_id(self):
        self.advance_id = False

    def _create_sheet_from_expenses(self):
        sheet = super(HrExpense, self)._create_sheet_from_expenses()
        if sheet.expense_line_ids and sheet.expense_line_ids[0].advance_id:
            if not sheet.company_id.advance_bank_journal_id:
                raise MissingError("Cannot find default bank journal to use for Advances. Set in Expense settings")
            sheet.bank_journal_id = sheet.company_id.advance_bank_journal_id.id
        return sheet

    def action_create_advance_expense_bill(self):
        move_obj = self.env["account.move"]
        created_bills = move_obj
        for expense in self:
            if not expense.advance_id:
                raise ValidationError("Cannot create bill for expenses not related to an Advance")
            if expense.state not in ["approved", "done"]:
                raise ValidationError("Cannot create bill for expenses not in approved or paid status")
            if not expense.supplier_id:
                raise MissingError("Missing vendor")

            bill = move_obj.create({
                "type": "in_invoice",
                "partner_id": expense.supplier_id.id,
                "currency_id": expense.currency_id.id,
                "invoice_line_ids": [(0,0,{
                    "product_id": expense.product_id.id,
                    "quantity": expense.quantity,
                    "price_unit": -expense.unit_amount,
                })]
            })
            expense.advance_expense_bill_id = bill.id
            created_bills |= bill
        action = self.env.ref('account.action_move_in_invoice_type').read()[0]
        if len(created_bills) == 1:
            action.update({
                "view_mode": "form",
                "view_id": False,
                "views": [(False, "form")],
                "res_id": created_bills.id,
            })
        elif len(created_bills) > 1:
            action["domain"] = [("id","in",created_bills.ids)]
        else:
            return
        return action