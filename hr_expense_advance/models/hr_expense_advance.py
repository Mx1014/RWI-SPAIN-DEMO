# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, MissingError, UserError

class HrExpenseAdvance(models.Model):
    _name = "hr.expense.advance"
    _description = "Expense Advance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _check_company_auto = True

    name = fields.Char(string="Description",
        required=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        })
    employee_id = fields.Many2one(string="Employee",
        comodel_name="hr.employee",
        required=True,
        default=lambda self: self.env.user.employee_id,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        })
    company_id = fields.Many2one(string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        })
    journal_id = fields.Many2one(string="Journal",
        comodel_name="account.journal",
        required=True,
        default=lambda self: self.env.company.advance_journal_id)
    product_id = fields.Many2one(string="Product",
        comodel_name="product.product",
        required=True,
        default=lambda self: self.env.company.advance_product_id)
    currency_id = fields.Many2one(string="Currency",
        comodel_name="res.currency",
        default=lambda self: self.env.company.advance_journal_id.currency_id or self.env.company.currency_id,
        required=True,
        readonly=True,
        states={
            "draft": [("readonly", False)],
        })
    line_ids = fields.One2many(string="Lines",
        comodel_name="hr.expense.advance.line",
        inverse_name="advance_id",
        readonly=True,
        states={
            "draft": [("readonly", False)],
        })
    state = fields.Selection(string="Status",
        selection=[
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("approve", "Approved"),
            ("cancel", "Refused")],
        default="draft",
        required=True,
        tracking=True,
        readonly=True)
    payment_state = fields.Selection(string="Payment Status",
        selection=[
            ("waiting", "Waiting Approval"),
            ("to_release", "To Release"),
            ("to_close", "To Close"),
            ("close", "Closed")],
        compute="_compute_payment_state",
        store=True,
        tracking=True,)
    release_bill_id = fields.Many2one(string="Releasing Bill",
        comodel_name="account.move",
        readonly=True)
    close_bill_id = fields.Many2one(string="Closing Bill",
        comodel_name="account.move",
        readonly=True)
    expense_ids = fields.One2many(string="Expenses",
        comodel_name="hr.expense",
        inverse_name="advance_id",
        readonly=True)
    total_estimated_amount = fields.Monetary(string="Estimated",
        compute="_compute_total_estimated_amount",
        store=True)
    total_expensed_amount = fields.Monetary(string="Approved Expense",
        compute="_compute_total_expensed_amount",
        store=True)
    total_remaining_amount = fields.Monetary(string="Remaining",
        compute="_compute_total_remaining_amount",
        store=True)
    user_id = fields.Many2one(string="Manager",
        comodel_name="res.users",
        compute="_compute_user_id",
        store=True,
        readonly=False)
    department_id = fields.Many2one(string="Department",
        comodel_name="hr.department",
        compute="_compute_department_id",
        store=True)
    can_reset = fields.Boolean(string="Can Reset",
        compute="_compute_can_reset")

    @api.depends("line_ids", "line_ids.estimated_amount")
    def _compute_total_estimated_amount(self):
        for advance in self:
            advance.total_estimated_amount = sum(advance.line_ids.mapped("estimated_amount"))

    @api.depends("expense_ids", "expense_ids.total_amount", "expense_ids.state")
    def _compute_total_expensed_amount(self):
        for advance in self:
            advance.total_expensed_amount = sum(
                advance.expense_ids.filtered(lambda x: x.state in ["approved", "done"]).mapped("total_amount"))

    @api.depends("total_estimated_amount", "total_expensed_amount")
    def _compute_total_remaining_amount(self):
        for advance in self:
            advance.total_remaining_amount = advance.total_estimated_amount + advance.total_expensed_amount

    @api.depends("state", "release_bill_id.invoice_payment_state", "close_bill_id.invoice_payment_state")
    def _compute_payment_state(self):
        for advance in self:
            if advance.close_bill_id.invoice_payment_state in ["in_payment", "paid"]:
                advance.payment_state = "close"
            elif advance.release_bill_id.invoice_payment_state in ["in_payment", "paid"]:
                advance.payment_state = "to_close"
            elif advance.state == "approve":
                advance.payment_state = "to_release"
            else:
                advance.payment_state = "waiting"
    
    @api.depends("employee_id")
    def _compute_department_id(self):
        for advance in self:
            advance.department_id = advance.employee_id.department_id

    @api.depends("employee_id")
    def _compute_user_id(self):
        for advance in self:
            advance.user_id = advance.employee_id.expense_manager_id or advance.employee_id.parent_id.user_id

    def _compute_can_reset(self):
        is_expense_user = self.user_has_groups("hr_expense.group_hr_expense_team_approver")
        for advance in self:
            advance.can_reset = is_expense_user if is_expense_user else advance.employee_id.user_id == self.env.user

    def action_submit(self):
        self.write({"state": "submit"})
        self.activity_update()

    def action_approve(self):
        if not self.user_has_groups("hr_expense.group_hr_expense_team_approver"):
            raise UserError(_("Only Managers and HR Officers can approve advances"))
        elif not self.user_has_groups("hr_expense.group_hr_expense_manager"):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own advances"))

            if not self.env.user in current_managers and not self.user_has_groups("hr_expense.group_hr_expense_user") and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only approve your department advances"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({"state": "approve", "user_id": responsible_id})
        self.activity_update()

    def action_cancel(self):
        if not self.user_has_groups("hr_expense.group_hr_expense_team_approver"):
            raise UserError(_("Only Managers and HR Officers can approve advances"))
        elif not self.user_has_groups("hr_expense.group_hr_expense_manager"):
            current_managers = self.employee_id.expense_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own advances"))

            if not self.env.user in current_managers and not self.user_has_groups("hr_expense.group_hr_expense_user") and self.employee_id.expense_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department advances"))
        if self.filtered(lambda x: x.release_bill_id):
            raise UserError("Cannot refuse/cancel advances with a releasing bill. Remove first")

        self.write({"state": "cancel"})
        self.activity_update()
    
    def action_draft(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.write({"state": "draft"})
        self.activity_update()
        return True

    def action_create_release_bill(self):
        move_obj = self.env["account.move"]
        created_bills = move_obj
        for advance in self:
            if advance.state != "approve":
                raise ValidationError("Cannot create release bill for advances not in approved status")
            if advance.release_bill_id:
                raise ValidationError("Releasing bill already exists")
            if not advance.employee_id.address_home_id:
                raise MissingError("Cannot find contact record for employee. Set Address under Private Information")

            bill = move_obj.create({
                "type": "in_invoice",
                "partner_id": advance.employee_id.address_home_id.id,
                "journal_id": advance.journal_id.id,
                "currency_id": advance.currency_id.id,
                "invoice_line_ids": [(0,0,{
                    "product_id": advance.product_id.id,
                    "quantity": 1,
                    "price_unit": advance.total_estimated_amount,
                })]
            })
            advance.release_bill_id = bill.id
            created_bills |= bill
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
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
            return True
        return action

    def action_create_close_bill(self):
        move_obj = self.env["account.move"]
        created_bills = move_obj
        for advance in self:
            if advance.state != "approve":
                raise ValidationError("Cannot create closing bill for advances not in approved status")
            if not advance.payment_state == "to_close":
                raise ValidationError("Not in the valid state to close")
            if advance.expense_ids.filtered(lambda x: x.state in ["draft", "reported"]):
                raise ValidationError("Some expenses are still for approval")
            if any(not expense.advance_expense_bill_id.invoice_payment_state in ["in_payment", "paid"] for expense in
                advance.expense_ids.filtered(lambda x: x.state in ["approved", "done"])):
                raise ValidationError("All related approved/paid expenses should have a paid expense bill")

            bill = move_obj.create({
                "type": "in_refund",
                "partner_id": advance.release_bill_id.partner_id.id,
                "journal_id": advance.journal_id.id,
                "currency_id": advance.currency_id.id,
                "invoice_line_ids": [(0,0,{
                    "product_id": advance.product_id.id,
                    "quantity": 1,
                    "price_unit": advance.total_remaining_amount,
                })]
            })
            advance.close_bill_id = bill.id
            created_bills |= bill
        action = self.env.ref("account.action_move_in_refund_type").read()[0]
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
            return True
        return action

    def activity_update(self):
        for advance in self.filtered(lambda x: x.state == "submit"):
            self.activity_schedule(
                "hr_expense.mail_act_expense_approval",
                user_id=advance.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda x: x.state == "approve").activity_feedback(["hr_expense.mail_act_expense_approval"])
        self.filtered(lambda x: x.state in ("draft", "cancel")).activity_unlink(["hr_expense.mail_act_expense_approval"])
    
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env["res.users"]

    def unlink(self):
        for advance in self:
            if advance.release_bill_id:
                raise UserError(_('You cannot delete an advance with a releasing bill'))
        super(HrExpenseAdvance, self).unlink()