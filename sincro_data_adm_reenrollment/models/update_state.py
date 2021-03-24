from setuptools.command.alias import alias

from odoo import fields, models, _
from odoo.exceptions import ValidationError


class ChangeState(models.Model):
    _name = 'update.state'
    _description = 'Change the state of a application/reenrollment'

    def get_country(self):
        # return self.env['res.partner'].search(
        #     [('person_type', '=', 'student'), ('reenrollment_status_id', '=', 'open')]).filtered(
        #     lambda open_stud: open_stud.id not in self.env['adm.reenrollment'].search([]).partner_id.ids)
        return self.env['res.country'].search([])[0].id

    def get_applications(self):
        all_applications = self.env['adm.application'].search([])
        export_data_env = self.env['sincro_data.export_data']
        res = []

        for app in all_applications:
            res.append(export_data_env.create({
                'application_id': app.id,
                'result': True,
                'comment': 't <b>is</b><strong> a long </strong>established fact that a reader will be distracted by the readable content of a page when looking at its layout.'
            }))

        return res

    def get_default_applications(self):
        active_ids = []
        if self._context.get('active_model') == 'adm.application':
            active_ids = (self._context.get('active_ids', [])) or []
        server_id = self.env['sincro_data.server'].search([('is_application_server_default', '=', True)])
        res = {'is_success': False,
               'is_warning': False,
               'is_error': False,
               'response_msg': 'Not found a sincro data server by default for applications.'}
        for item in active_ids:
            if server_id:
                res = server_id.check_create_person_facts(item)

            self.env['adm.application'].browse(item).with_context({'forcing': True}).write(
                {
                    'is_success': res['is_success'],
                    'is_warning': res['is_warning'],
                    'is_error': res['is_error'],
                    'comment': res['response_msg']
                })

        # self.env['adm.application'].browse(active_ids[0]).with_context({'forcing': True}).write({'check_err': True, 'comment': '<b>is</b><strong> a long </strong>hed fact that a reader will be distracted by the readable content of a page when looking at its layout.'})
        # self.env['adm.application'].browse(active_ids[1]).with_context({'forcing': True}).write({'check_err': False, 'comment': 'Correct!'})

        return self.env['adm.application'].browse(active_ids)

    def _check_reenrollment_data(self, itm):
        is_warning, is_error, response_msg = False, False, ''
        idx = 1

        # comprobacion del facts_id
        if not itm.partner_id.facts_id:
            is_error = True
            response_msg += '%s. The student %s doesn´t have to assign a facts_id.\n' % (idx, str(itm.partner_id.name))
            idx += 1

        # comprobacion de grade_level,family_id  como error
        for checked_field in ['grade_level_id', 'family_id']:
            if checked_field not in itm or not itm[checked_field] or itm[checked_field] == '':
                is_error = True
                response_msg += '%s. The student %s doesn´t have to assign a %s.\n' % (idx,
                                                                                       str(itm.partner_id.name),
                                                                                       checked_field)
                idx += 1

        required_fields_raw = itm.get_required_fields()
        required_fields = required_fields_raw.mapped(lambda x: x.name) or []
        # comprobacion del facts_id de otros campos como warning
        for checked_field in required_fields:
            if checked_field not in itm or not itm[checked_field] or itm[checked_field] == '':
                is_warning = True
                response_msg += '%s. The student %s doesn´t have to assign a %s.\n' % (idx,
                                                                                       str(itm.partner_id.name),
                                                                                       checked_field)
                idx += 1

        if not is_warning and not is_error:
            response_msg = 'The application passed the tests!.'

        return {'is_success': True,
                'is_warning': is_warning,
                'is_error': is_error,
                'response_msg': response_msg}

    def get_default_reenrollments(self):
        active_ids = []
        if self._context.get('active_model') == 'adm.reenrollment':
            active_ids = (self._context.get('active_ids', [])) or []

        re_enrollment_env = self.env['adm.reenrollment']
        for item in active_ids:
            re_enrollment = re_enrollment_env.browse(item)
            res = self._check_reenrollment_data(re_enrollment)

            re_enrollment.with_context({'forcing': True}).write(
                {
                    'is_success': res['is_success'],
                    'is_warning': res['is_warning'],
                    'is_error': res['is_error'],
                    'comment': res['response_msg']
                })

        return re_enrollment_env.browse(active_ids)

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status')
    logo = fields.Char()
    country = fields.Many2one("res.country", String="country", default=get_country)
    applications = fields.One2many('sincro_data.export_data', 'update_state_id', "Applications")

    default_applications = fields.One2many('adm.application', 'update_state_id', "Applications",
                                           default=get_default_applications)
    default_reenrollments = fields.One2many('adm.reenrollment', 'update_state_id', "Reenrollments",
                                            default=get_default_reenrollments)

    def update_state_application(self):
        active_ids = self._context.get('active_ids', []) or []
        state_import = self.env['adm.application.status'].search([('import_to_facts', '=', True)])

        if not state_import:
            raise ValidationError(
                "Not found stage with the option import_to_facts activated..")

        for record in self.env['adm.application'].browse(active_ids):
            record.with_context({'forcing': True}).write({'status_id': state_import[0].id})

    def update_state_reenrollment(self):
        active_ids = self._context.get('active_ids', []) or []
        export_state = self.env['adm.reenrollment.status'].search([('import_to_facts', '=', True)])

        if not export_state:
            raise ValidationError(
                "Not found stage with the option import_to_facts activated..")

        for record in self.env['adm.reenrollment'].browse(active_ids):
            if record.partner_id.facts_id:
                record.with_context({'forcing': True}).write({'status_id': export_state[0].id})

    def read(self, values):
        return super().read(values)
