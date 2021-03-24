# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    location = fields.Char(string="Location")
    employee_id = fields.Many2one(string="Employee",
        comodel_name="hr.employee",
        compute="_compute_employee",
        store=True)
    department_id = fields.Many2one(string="Department",
        comodel_name="hr.department",
        compute="_compute_employee",
        store=True)
    
    @api.depends("partner_id")
    def _compute_employee(self):
        for ticket in self:
            employee_id = False
            department_id = False
            if ticket.partner_id and ticket.partner_id.user_ids and ticket.partner_id.user_ids.mapped("employee_id"):
                employee = ticket.partner_id.user_ids.mapped("employee_id")[0]
                employee_id = employee.id
                department_id = employee.department_id.id
            ticket.employee_id = employee_id
            ticket.department_id = department_id