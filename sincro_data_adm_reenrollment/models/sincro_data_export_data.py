# -*- coding:utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta


# ESTO OCASINADA QUE SE COPLE ESTA API AL MODULO DE SCHOOL ADMISSIONS
class ExportData(models.Model):
    _name = "sincro_data.export_data"
    _description = "Export Data"

    application_id = fields.Many2one('adm.application', String="Application")
    update_state_id = fields.Many2one('update.state', String="Update State")
    result = fields.Boolean()
    comment = fields.Char()

    # imported = fields.Boolean()
    # item = fields.Reference(string='Item data',
    #                         selection=[('adm.application', 'Application'), ('adm.reenrollment', 'Reenrollment')])
    #
    # first_imported_date = fields.Datetime(String="First imported date")
    # export_data_wizard_id = fields.Many2one("sincro_data.export_data_wizard", string="Export data wizard ID")
    #
    # status_type = fields.Selection([
    #     ("stage", "Stage"),
    #     ("done", "Done"),
    #     ("return", "Return To Parents"),
    #     ("started", "Application Started"),
    #     ("submitted", "Submitted"),
    #     ("cancelled", "Cancelled")
    # ], string="Type", default='stage')
    #
    # stage = fields.Char(String="Stage")
    #
    # def write(self, values):
    #     super().write(values)
    #
    # def read(self, values):
    #     # self.env['sincro_data.export_data'].search([]).unlink()
    #     # self._cr.commit()
    #     #
    #     all_items = self.env['sincro_data.export_data'].search([])
    #     created_adm, created_ree = [], []
    #     for itm in all_items:
    #         if itm.item and itm.item._name == 'adm.application':
    #             created_adm.append(itm.item.id)
    #         elif itm.item and itm.item._name == 'adm.reenrollment':
    #             created_ree.append(itm.item.id)
    #
    #     # update or create admission and reenrollment data
    #     for model, created_records in ['adm.application', created_adm], ['adm.reenrollment', created_ree]:
    #         self.env[model].search([('id', 'not in', created_records)]).filtered(
    #             lambda x: self.env['sincro_data.export_data'].create(
    #                 {'id': x.id, 'imported': False, 'item': '%s,%s' % (model, x.id),
    #                  'first_imported_date': datetime.now(), 'status_type': x.status_id.type_id,
    #                  'stage': x.status_id.name}))
    #
    #         self.env[model].search([('id', 'in', created_records)]).filtered(
    #             lambda x: self.env['sincro_data.export_data'].search([('item', '=', '%s,%s' % (model, x.id))]).write(
    #                 {'imported': False, 'item': '%s,%s' % (model, x.id),
    #                  'first_imported_date': datetime.now(), 'status_type': x.status_id.type_id,
    #                  'stage': x.status_id.name}))
    #
    #     # reenrollement data update or create
    #     # self.env['adm.reenrollment'].search([('id', 'not in', created_ree)]).filtered(
    #     #     lambda x: self.env['sincro_data.export_data'].create(
    #     #         {'id': x.id, 'imported': False, 'item': 'adm.reenrollment,%s' % x.id,
    #     #          'first_imported_date': datetime.now(),
    #     #          'export_data_wizard_id': 1, 'status_type': x.status_id.type_id}))
    #     #
    #     # self.env['adm.reenrollment'].search([('id', 'in', created_ree)]).filtered(
    #     #     lambda x: self.env['sincro_data.export_data'].search([('item', '=', 'adm.reenrollment,%s' % x.id)]).write(
    #     #         {'imported': False, 'item': 'adm.reenrollment,%s' % x.id,
    #     #          'first_imported_date': datetime.now(),
    #     #          'export_data_wizard_id': 1, 'status_type': x.status_id.type_id}))
    #
    #     self._cr.commit()
    #
    #     res = super().read(values)
    #
    #     # res = [res[0], res[1]]
    #     return res
    #
    # def import_all_students(self,**params):
    #     f =2
    #     return {}
