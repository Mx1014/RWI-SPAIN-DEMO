# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import json

from ..utils.commons import switch_statement


class Admission(models.Model):
    """ We inherit to enable School features for contacts """
    _inherit = "adm.application"

    update_state_id = fields.Many2one('update.state', String="Update State")
    is_success = fields.Boolean()
    is_warning = fields.Boolean()
    is_error = fields.Boolean()
    comment = fields.Char()
    fixed_msg = fields.Char()
    fixed_data = fields.Char()

    @api.depends('fixed_data')
    def _count_fixed_data(self):
        for application_id in self:
            if application_id.fixed_data:
                application_id.count_fixed_data = len(json.loads(application_id.fixed_data))
            else:
                application_id.count_fixed_data = 0

    # contador encargado de indicarme cuantas poosibles soluciones se pueden dar en la aplicacion
    count_fixed_data = fields.Integer(compute=_count_fixed_data)

    # boolenos que permiten forzar el onchange para que se actualice la informacion en el momento sin necesidad de actualizar el wizard
    fixed_1 = fields.Boolean()
    fixed_2 = fields.Boolean()
    fixed_3 = fields.Boolean()
    fixed_4 = fields.Boolean()
    fixed_5 = fields.Boolean()
    fixed_6 = fields.Boolean()
    fixed_7 = fields.Boolean()
    fixed_8 = fields.Boolean()
    fixed_9 = fields.Boolean()

    # booleanpos que comprueban todas las fixed data para saber cuales columnas deben ser invisibles
    column_available_adm = fields.Integer()

    def fixed_application(self):
        active_ids = (self._context.get('active_ids', [])) or []
        application_env = self.env['adm.application']
        for item_id in active_ids:
            application_id = application_env.browse(item_id)
            data_changes = json.loads(application_id.fixed_data)
            for change in data_changes:
                self.env[change['model']].browse(change['item_id']).write({change['field']: change['new_data']})

    def one_fixed_application(self):
        active_ids = (self._context.get('active_ids', [])) or []
        application_env = self.env['adm.application']
        btn_id = self._context.get('btn_id') or -1
        self.fixed_data = False
        # for item_id in active_ids:
        #     application_id = application_env.browse(item_id)
        #     data_changes = json.loads(application_id.fixed_data)
        #     if btn_id != -1 and btn_id - 1 in range(len(data_changes)):
        #         change = data_changes[btn_id - 1]
        #         self.env[change['model']].browse(change['item_id']).write({change['field']: change['new_data']})
        #         application_id.write({'fixed_data': json.dumps(data_changes.pop(btn_id - 1))})
        #         application_id.write({'fixed_data': False})
        # return {'type': 'ir.actions.act_close_wizard_and_reload_view'}
        return {
            'name': _('Export to FACTS (Applications)'),
            'view_mode': 'form',
            'res_model': 'update.state',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'delete': False},
            'domain': [('id', 'in', active_ids)],
            'target': 'new',
        }

    @api.onchange("fixed_1", "fixed_2", "fixed_3", "fixed_4", "fixed_5", "fixed_6", "fixed_7", "fixed_8")
    def _onchange_fixed_1(self):
        idx_error = self._context.get('btn_id')
        data_changes = json.loads(self.fixed_data)
        if idx_error in range(len(data_changes)):
            change = data_changes[idx_error]
            self.env[change['model']].browse(change['item_id']).write({change['field']: change['new_data']})

            server_id = self.env['sincro_data.server'].search([('is_application_server_default', '=', True)])
            if server_id:
                res = server_id.check_create_person_facts(self.id.origin)
                self.is_success = res['is_success']
                self.is_warning = res['is_warning']
                self.is_error = res['is_error']
                self.comment = res['response_msg']
                self.fixed_msg = res['fixed_msg']
                self.fixed_data = json.dumps(res['fixed_data'])
                # self.fixed_data = json.dumps(data_changes.pop(idx_error))

    # def read(self, values):
    #     return super().read(values)
