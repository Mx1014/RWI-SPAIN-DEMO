# -*- coding:utf-8 -*-

import base64
import logging
import requests
import json
import re

from datetime import datetime, timedelta
from pathlib import Path
from pprint import pprint as pp

from doc._extensions.html_domain import address
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import MissingError, UserError
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError
from datetime import timedelta

_logger = logging.getLogger(__name__)

REGEX_EMAIL = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'


class FullFabricServer(models.Model):
    _name = "sincro_data.server"
    _description = "Sincro Data Server"
    name = fields.Char(string="Name",
                       required=True)
    api_name = fields.Char(string="Request Name", related="api_id.name", readonly=True)
    api_base_url = fields.Char(string="Base URL", related="api_id.base_url", readonly=True)
    api_header_ids = fields.One2many(string="API headers", related="api_id.header_ids", readonly=True)
    model_id = fields.Many2one("ir.model", string="Model", required=True)
    api_id = fields.Many2one("sincro_data.api", string="API")
    path = fields.Char(string="Path")
    domain = fields.Char("Domain")
    test_item_model_id = fields.Integer('Item ID')
    parameter_ids = fields.One2many("sincro_data.parameter", "request_id", string="Parameters")
    computed_path = fields.Char(string="Computed path", compute="_compute_path", readonly=True)
    is_application_server_default = fields.Boolean("Is Application Server Default")
    is_reenrollment_server_default = fields.Boolean("Is Reenrollment Server Default")

    method = fields.Selection([
        ('get', "GET"),
        ('post', "POST"),
        ('put', "PUT"),
        ('delete', "DELETE"),
        ('patch', "PATCH"),
        ('head', "HEAD"),
        ('connect', "CONNECT"),
        ('options', "OPTIONS"),
        ('trace', "TRACE"),
        ('create_facts', "CREATE FACTS PERSON"),
    ],
        string="Method", default='get'
    )
    json_pretty = fields.Boolean("Pretty JSON", default=False)
    json_configuration_id = fields.Many2one('sincro_data.configuration_panel', string="JSON Configuration")
    json_example = fields.Char(string='JSON Example', compute="_compute_json", readonly=True)
    response_message = fields.Char(string='Response TEXT', compute="_clean_response", store=True, readonly=True)
    response_code = fields.Integer(string="Response code")
    # json_example = fields.Char(string='JSON Example')
    cron_id = fields.Many2one('ir.cron', string="Cron",
                              ondelete="cascade")

    cron_active = fields.Boolean(string="Active", related='cron_id.active')

    interval_minutes = fields.Integer(string="Interval minutes")

    retrieve_date = fields.Datetime(string="Last Retrieval Date",
                                    readonly=True)

    log_ids = fields.Many2many(string="Created Families",
                               comodel_name="sincro_data.log",
                               relation="sincro_data_log_rel")

    skip = fields.Integer(string="Skip")
    limit = fields.Integer(string="Limit",
                           default=100)

    @api.depends("path", "model_id", "test_item_model_id", "parameter_ids")
    def _compute_path(self):

        for record in self:
            try:
                env_aux = self.env[record.model_id.model]
                if not record.test_item_model_id or record.test_item_model_id == '' or record.test_item_model_id not in \
                        self.env[record.model_id.model].search([]).ids:
                    record.test_item_model_id = env_aux.search([])[0].id

                record.computed_path = record.api_base_url + record.path % tuple(
                    reversed(tuple(map(lambda value: env_aux.browse([record.test_item_model_id])[
                        value.field_value.name] if value.type != 'constant' else value.constant_value,
                                       record.parameter_ids))))
            except:
                record.computed_path = 'Problems with the configuration of request.'

    @api.depends("json_configuration_id", "model_id", "test_item_model_id", "json_pretty")
    def _clean_response(self):
        for record in self:
            record.response_message = ''

    @api.model
    def create(self, values):
        # values['sequence'] = next_order
        return super().create(values)

    @api.depends("json_configuration_id", "model_id", "test_item_model_id", "json_pretty")
    def _compute_json(self):
        for record in self:
            try:
                env_aux = self.env[record.model_id.model]
                if record.json_configuration_id and env_aux.browse([record.test_item_model_id]):
                    record.json_example = record.json_configuration_id.get_json(record.json_configuration_id,
                                                                                env_aux.browse(
                                                                                    [record.test_item_model_id]),
                                                                                record.json_pretty)
                else:
                    record.json_example = {}
            except:
                record.json_example = {}

    def action_delete_all_data(self):
        for server in self:
            server.move_ids.unlink()
            server.attachment_ids.unlink()
            server.test_ids.unlink()
            # server.program_pathway_ids.unlink()
            server.application_ids.unlink()
            server.student_ids.unlink()
            server.parent_ids.unlink()
            server.family_ids.unlink()
            server.retrieve_date = False

    # def _create_person_facts(self, server, headers):
    #     self.ensure_one()
    #     unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
    #     if len(json.loads(unknown_students.text)['results']) > 0:
    #         unk_std = json.loads(unknown_students.text)['results'][0]
    #         unk_std_id = unk_std['personId']
    #         env_aux = self.env[self.model_id.model]
    #         computed_path = self.api_base_url + '/People/' % tuple(
    #             reversed(tuple(map(lambda value: env_aux.browse([record.test_item_model_id])[
    #                 value.field_value.name] if value.type != 'constant' else value.constant_value,
    #                                record.parameter_ids))))
    #
    #         return self._send_request(server.computed_path, 'put', headers, self.json_example)
    #     else:
    #         raise ValidationError("No existe usuarios Unknown en FACTS")
    def _create_person_facts(self, server, headers):
        self.ensure_one()
        unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
        students = json.loads(unknown_students.text)['results']
        env_log = self.env['sincro_data.log']
        log_registers = env_log.search([('url', 'like', 'create_facts')])
        # log_registers = env_log.search([])

        created_students = log_registers.mapped(lambda x: x.item_id);
        new_students = list(filter(lambda x: x['personId'] not in created_students, students))

        # selected_students = students.filtered(
        #     lambda app: any(json.loads(app.text)['results']['personId'] not in log_registers))
        if len(new_students) > 0:
            unk_std_id = new_students[0]['personId']
            computed_path = self.api_base_url + '/People/%s' % unk_std_id
            created_res = self._send_request(computed_path, 'put', headers, self.json_example)
            created_log = env_log.create({
                'url': 'create_facts',
                'item_id': unk_std_id,
                'created_date': datetime.now(),
                'status_code': created_res.status_code,
                'request': str(created_res.request.body),
                'response': created_res.text
            })

            return created_res
        else:
            raise ValidationError("No existe usuarios Unknown en FACTS")

    def action_test_connection(self, *args):
        for server in self:
            error_msgs = {}
            headers = {}
            res = False
            for header in server.api_header_ids:
                headers[header.name] = header.value

            if self.method == 'create_facts':
                res = self._create_person_facts(server, headers)
            else:
                res = self._send_request(server.computed_path, server.method, headers, server.json_example)

                self.response_code = res.status_code
                self.response_message = res.text

                env_log = self.env['sincro_data.log']
                server.retrieve_date = datetime.now()

                created_log = env_log.create({
                    'url': server.computed_path,
                    'item_id': server.test_item_model_id,
                    'created_date': datetime.now(),
                    'model': str(server.model_id.model),
                    'server_id': self.id,
                    'status_code': res.status_code,
                    'request': str(server.json_example),
                    'response': res.text
                })
                self.log_ids = [(4, created_log.id)]

    def _update_user_defined_data(self, application, group_type, itm, headers):
        groups = self.api_id.ud_fields.filtered(lambda x: x.group_type == group_type).group_ids
        for g_item in groups.field_ids:
            check_path = 'https://api.factsmgt.com/UserDefinedData?filters=fieldId==%s,linkedId==%s' % (
                g_item.facts_id, itm.facts_id)

            field_body = {
                "fieldId": g_item.facts_id,
                "linkedId": itm.facts_id
                # "data": str(self.env['res.partner'].browse(itm.id)[g_item.odoo_field_id.name])
            }

            # reenrollment_year_id = (self.env['ir.config_parameter'].sudo()
            #                         .get_param('reenrollment_year_id', ''))
            # admission_year_id = (self.env['ir.config_parameter'].sudo()
            #                      .get_param('admission_year_id', ''))

            aux_data = 'default_data'
            if g_item.odoo_field_id.model == 'res.partner':
                if g_item.odoo_field_id.name not in self.env['res.partner'].browse(itm.id):
                    application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                        [('sequence', '=', application.status_id.sequence - 1)]).id})
                    self._cr.commit()
                    raise ValidationError("The field %s not exists in Contacts" % g_item.odoo_field_id.name)

                if self.env['res.partner'].browse(itm.id)[g_item.odoo_field_id.name]:
                    aux_data = self.env['res.partner'].browse(itm.id)[g_item.odoo_field_id.name]
                    if g_item.odoo_field_id.ttype == 'date':
                        aux_data = aux_data.strftime("%m-%d-%Y")
                    field_body['data'] = aux_data

            elif (g_item.odoo_field_id.model == 'adm.application' and self.model_id.model == 'adm.application') or (
                    g_item.odoo_field_id.model == 'adm.reenrollment' and self.model_id.model == 'adm.reenrollment'):
                aux_data = application[g_item.odoo_field_id.name]

            # TOMA LA INFO DE LA APPLICATION
            # elif g_item.odoo_field_id.model == 'adm.application' and self.model_id.model == 'adm.application' :
            #     aux_data = self.env['adm.application'].browse(application.id)[g_item.odoo_field_id.name]
            #     # aux_data = self.env['adm.application'].search(
            #     #     [('school_year.id', '=', admission_year_id), ('partner_id', '=', itm.id)])[
            #     #     g_item.odoo_field_id.name]
            #
            # # TOMA LA INFO DEL REENROLLMENT
            # elif g_item.odoo_field_id.model == 'adm.reenrollment' and self.model_id.model == 'adm.reenrollment':
            #     aux_data = self.env['adm.reenrollment'].browse(application.id)[g_item.odoo_field_id.name]
            #     # aux_data = self.env['adm.reenrollment'].search(
            #     #     [('school_year.id', '=', reenrollment_year_id), ('partner_id', '=', itm.id)])[
            #     #     g_item.odoo_field_id.name]

            if aux_data and isinstance(aux_data, dict) and aux_data and 'name' in aux_data:
                aux_data = aux_data['name']

            field_body['data'] = str(aux_data)

            # tenemos que revisar esto ya que se ejecuta mas de una vez y da problemas cuando realiza el get ya que llega vacio por el delay del webservice de facts (5-10 segundos)
            res = self._check_and_create_in_facts(check_path,
                                                  'https://api.factsmgt.com/UserDefinedData', headers,
                                                  field_body)

            _logger.info("============UD CREATE GROUP===============")
            _logger.info("check_path:%s" % check_path)
            _logger.info("field_body: %s" % str(field_body))
            _logger.info("res.text: %s" % str(res.text))
            _logger.info("res.text: %s" % str(res))
            _logger.info("===========================")

            if not res.ok:  # if 'results' not in json.loads(res.text) or len(json.loads(res.text)['results']) == 0:
                # application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                #     [('sequence', '=', application.status_id.sequence - 1)]).id})
                # self._cr.commit()
                # raise ValidationError("Cant create a record in UDData")
                _logger.info("Error cuando se intento ejecutar _check_and_create_in_facts().")
            else:
                _logger.info("============UD PUT USER DEFINEDS===============")
                if 'results' in json.loads(res.text):
                    facts_field_id = json.loads(res.text)['results'][0]['id']
                else:
                    facts_field_id = json.loads(res.text)['id']

                if 'data' in field_body:
                    res = self._send_request('https://api.factsmgt.com/UserDefinedData/%s' % facts_field_id, 'put',
                                             headers, json.dumps({'data': field_body['data']}))

    def check_create_person_facts(self, *args):
        for server in self:
            application = self.env[self.model_id.model].browse(args[0])
            if self.model_id.model == 'adm.application':
                application_grade_level = application.grade_level
            else:  # adm.reenrollment
                application_grade_level = application.grade_level_id

            env_res_partner = self.env['res.partner']
            headers = {}
            for header in server.api_header_ids:
                headers[header.name] = header.value

            unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
            students = json.loads(unknown_students.text)['results']
            env_log = self.env['sincro_data.log']
            log_registers = env_log.search([('url', 'like', 'create_facts')])

            adm_student = env_res_partner.browse([application.partner_id.id])
            adm_family = env_res_partner.browse([application.partner_id.get_families()[0].id])
            adm_relationships = application.relationship_ids
            is_warning, is_error, response_msg = False, False, ''
            adm_house_address = adm_family.home_address_id
            idx = 1

            # check the name family and email

            all_family_names = self._send_request(self.api_base_url + '/families?pageSize=2147483647',
                                                  'get',
                                                  headers, '{}')
            #
            # # # def _find_in_list(self, list_json, fields_to_check, value):
            family_id = self._find_in_list(application, json.loads(all_family_names.text)['results'],
                                           ['familyName'],
                                           {'familyName': str(self._clean_false_to_empty(
                                               adm_family, ['name'],
                                               'Family of %s' % adm_family.name))
                                           }, 'familyID')

            if family_id != -1 and adm_family and family_id != adm_family.facts_id:
                is_warning = True
                response_msg += '%s. The name of the family %s(%s) exists in FACTS --> Facts Family ID:(%s).\n' % (
                    idx, adm_family.name, adm_family.facts_id, family_id)
                idx += 1

            # CHECK EMAIL OF STUDENT
            if adm_student.email:
                res_check_student = self._send_request(
                    '%s/People?filters=email==%s' % (self.api_base_url, adm_student.email),
                    'get',
                    headers, '{}')

                for facts_student in json.loads(res_check_student.text)['results']:
                    is_error = True
                    response_msg += '%s. The student %s has the duplicate email (%s)  in FACTS --> Facts Student: %s(%s).\n' % (
                        idx, adm_student.name, adm_student.email,
                        '%s %s' % (facts_student['firstName'], facts_student['lastName']),
                        facts_student['personId'])
                    idx += 1

            # CHECK RELATIONSHIPS OF PARENTS
            for rel in adm_relationships:
                person = rel.partner_2
                if person.email:
                    res_check_parent = self._send_request(
                        '%s/People?filters=email==%s' % (self.api_base_url, person.email),
                        'get',
                        headers, '{}')

                    for facts_parent in json.loads(res_check_parent.text)['results']:
                        is_error = True
                        response_msg += '%s. The person %s has the duplicate email (%s) in FACTS --> Facts Person: %s(%s).\n' % (
                            idx, person.name, person.email,
                            '%s %s' % (facts_parent['firstName'], facts_parent['lastName']),
                            facts_parent['personId'])
                        idx += 1

            if len(adm_family.home_address_id) == 0:
                is_error = True
                response_msg += '%s. This student doesn´t have a home address linked.\n' % idx
                idx += 1
            #

            if adm_house_address:
                all_address_facts = self._send_request(self.api_base_url + '/people/Address?pageSize=2147483647',
                                                       'get',
                                                       headers, '{}')

                # # def _find_in_list(self, list_json, fields_to_check, value):
                address_facts_id = self._find_in_list(application, json.loads(all_address_facts.text)['results'],
                                                      ['address1', 'city', 'state', 'zip', 'country'],
                                                      {'address1': str(self._clean_false_to_empty(
                                                          adm_house_address, ['street'],
                                                          'Address of family %s' % adm_family.name)),
                                                          'city': str(self._clean_false_to_empty(
                                                              adm_house_address, ['city'], 'Default city')),
                                                          'state': str(self._clean_false_to_empty(
                                                              adm_house_address, ['state_id', 'name'],
                                                              'Default State')),
                                                          'zip': str(self._clean_false_to_empty(
                                                              adm_house_address, ['zip'], 'Default ZIP')),
                                                          'country': str(self._clean_false_to_empty(
                                                              adm_house_address, ['country_id', 'name'],
                                                              'Default Country'))
                                                      }, 'addressID')
                if address_facts_id != -1:
                    persons_with_same_address = self._send_request(
                        '%s/People?filters=addressID==%s' % (self.api_base_url, address_facts_id),
                        'get',
                        headers, '{}')
                    response_msg += '%s. The next persons has the same address in FACTS:\n' % idx
                    idx_inner = 1
                    for person in json.loads(persons_with_same_address.text)['results']:
                        response_msg += '%s.%s. %s %s(%s) \n' % (
                            idx, idx_inner, person['firstName'], person['lastName'], person['personId'])
                        idx_inner += 1

                    idx += 1
                    is_warning = True

        # check the name family and email

        if not is_warning and not is_error:
            response_msg = 'The application passed the tests!.'
        return {'is_success': True,
                'is_warning': is_warning,
                'is_error': is_error,
                'response_msg': response_msg}

    def action_create_person_facts(self, *args):
        for server in self:
            self.ensure_one()
            automation_env = self.env['base.automation']
            env_application_id = self.env['ir.model'].search([('model', '=', self.model_id.model)]).id

            automation_name = 'Cron of sincro_data: %s (%s) for %s' % (self.name, self.id, self.model_id.model)
            existed_automation = automation_env.search([('name', '=', automation_name)])
            if not existed_automation:
                existed_automation = automation_env.create({
                    'name': automation_name,
                    'model_id': env_application_id,
                    'trigger': 'on_write',
                    'state': 'code',
                    'last_run': datetime.now(),
                    # 'filter_pre_domain': '[["status_type","=","submitted"]]',
                    'filter_domain': '[["status_id.import_to_facts","=",True]]',
                    'code': 'env["sincro_data.server"].browse(%s).with_context(email_error=True)'
                            '.action_retrieve_data(record.id)' % self.id
                })
            # else:
            #     # ACTUALIZAMOS EL LAST_RUN
            #     if existed_automation.last_run >= datetime.now() - timedelta(minutes=1):
            #         _logger.info(
            #             "Possible parallel execution existed_automation.last_run >= datetime.now() - timedelta(minutes=1) --> %s >= %s -1minute: %s" % (
            #             existed_automation.last_run, datetime.now(),
            #             existed_automation.last_run >= datetime.now() - timedelta(minutes=1)))
            # #
            # existed_automation.write({'last_run': datetime.now()})
            # _logger.info("++++++++++++++++++++")
            # _logger.info("LAST RUN")
            # _logger.info(str(existed_automation[0].last_run))
            # _logger.info(" %s >= %s: %s" % (existed_automation.last_run, datetime.now() - timedelta(minutes=1),
            #                                 existed_automation.last_run >= datetime.now() - timedelta(minutes=1)))
            # _logger.info("++++++++++++++++++++")

            # viene como parametro el id de la aplication o del reenrollment
            if args[0]:

                application = self.env[self.model_id.model].browse(args[0])
                if self.model_id.model == 'adm.application':
                    application_grade_level = application.grade_level
                    application_school_year = application.school_year
                else:  # adm.reenrollment
                    application_grade_level = application.grade_level_id
                    application_school_year = application.school_year_id

                env_res_partner = self.env['res.partner']
                headers = {}
                for header in server.api_header_ids:
                    headers[header.name] = header.value

                unknown_students = self._send_request(server.computed_path, 'get', headers, '{}')
                students = json.loads(unknown_students.text)['results']
                env_log = self.env['sincro_data.log']
                log_registers = env_log.search([('url', 'like', 'create_facts')])

                adm_student = env_res_partner.browse([application.partner_id.id])
                adm_family = env_res_partner.browse([application.partner_id.get_families()[0].id])
                adm_relationships = application.relationship_ids

                if len(adm_family.home_address_id) == 0:
                    application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                        [('sequence', '=', application.status_id.sequence - 1)]).id})
                    self._cr.commit()
                    raise ValidationError("Not exists address linked to this student")

                adm_house_address = adm_family.home_address_id[0]

                # LA CREACION DE LOS GRUPOSschool_base
                # sincro_data UD EN FACTS SE HARA MANUAL YA QUE NO FUNCIONA
                # ESTO EN FACTS.
                student_groups = self.api_id.ud_fields.filtered(
                    lambda x: x.group_type in ('students', 'families', 'family_individual')).group_ids
                for std_group in student_groups:
                    if not std_group.facts_id or str(std_group.facts_id).strip() == '':
                        check_path = 'https://api.factsmgt.com/UserDefinedGroups?filters=groupName==%s' % std_group.name
                        if not std_group.district_wide:
                            check_path = check_path + ',schoolCode==%s' % application_grade_level.school_code_id.name

                        res = self._check_and_create_in_facts(check_path,
                                                              'https://api.factsmgt.com/UserDefinedGroups', headers,
                                                              json.dumps({}))
                        # se informa sobre el grupo que no se ha creado en facts
                        if 'results' not in json.loads(res.text) or len(json.loads(res.text)['results']) == 0:
                            group_path = '%s/%s' % (std_group.group_type_id.group_type, std_group.name)
                            application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                                [('sequence', '=', application.status_id.sequence - 1)]).id})
                            self._cr.commit()
                            raise ValidationError("Not found an UD group, please create it --> %s" % group_path)
                        # se crean los user defined  que sean necessarios en FACTS
                        else:
                            facts_group_id = json.loads(res.text)['results'][0]['id']
                            std_group.write({'facts_id': facts_group_id})

                    for group_field in std_group.field_ids:
                        if not group_field.facts_id or str(group_field.facts_id).strip() == '':
                            check_path = 'https://api.factsmgt.com/UserDefinedFields?filters=groupId==%s,fieldName==%s' % (
                                std_group.facts_id, group_field.name)

                            json_field_date = {
                                "groupId": std_group.facts_id,
                                "fieldName": group_field.name,
                                "fieldType": group_field.group_type
                            }

                            res = self._check_and_create_in_facts(check_path,
                                                                  'https://api.factsmgt.com/UserDefinedFields',
                                                                  headers, json_field_date)

                            # se informa sobre el grupo que no se ha creado en facts
                            if not res.ok:
                                group_field_path = '%s/%s/%s' % (
                                    std_group.group_type_id.group_type, std_group.name, group_field.name)
                                application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                                    [('sequence', '=', application.status_id.sequence - 1)]).id})
                                self._cr.commit()
                                raise ValidationError(
                                    "Not found an UD Field, please create it --> %s" % group_field_path)
                            else:
                                if 'results' in json.loads(res.text):
                                    facts_field_id = json.loads(res.text)['results'][0]['id']
                                else:
                                    facts_field_id = json.loads(res.text)['id']

                                group_field.write({'facts_id': facts_field_id})

                # SEARCH OR CREATE THE FAMILY IN FACTS FOR LINK IT WITH THE APPLICATIONS PERSON
                family_facts_id = adm_family.facts_id

                if not family_facts_id:
                    family_body = {
                        "familyName": env_res_partner.browse([application.family_id.id]).name,
                        "enableWeb": True,
                        "unlisted": 0,
                        "note": "",
                        "parentsWebFinancialBlock": False
                    }
                    family_body = json.dumps(family_body)

                    res_address = self._send_request(self.api_base_url + '/families', 'post', headers, family_body)
                    family_facts_id = json.loads(res_address.text)['familyID']
                    adm_family.write({'facts_id': family_facts_id})

                    # self._save_in_log(server, self.api_base_url + '/families', datetime.now(), server.id, 'res.partner',
                    #                   adm_family.id, res_address.status_code, str(res_address.request.body), str(res_address.text), 'post')

                # ACTUALIZAR UD FAMILY
                self._update_user_defined_data(application, 'families', adm_family, headers)

                # SEARCH OR CREATE THE ADDRESS IN FACTS FOR LINK IT WITH THE APPLICATIONS PERSON

                # SI EL HOME ADDRESS TIENE UN FACTS_ID ASOCIADO, ENTONCES TOMAMOS ESTE.
                if adm_house_address.facts_id:
                    address_facts_id = adm_house_address.facts_id
                else:
                    # SI NO EL HOMEADDRESS NO TIENE FACTS_ID PROCEDEMOS A BUSCARLO EN TODAS LAS DIRECCIONES
                    all_address_facts = self._send_request(self.api_base_url + '/people/Address?pageSize=2147483647',
                                                           'get',
                                                           headers, '{}')
                    # # def _find_in_list(self, list_json, fields_to_check, value):
                    address_facts_id = self._find_in_list(application, json.loads(all_address_facts.text)['results'],
                                                          ['address1', 'city', 'state', 'zip', 'country'],
                                                          {'address1': str(self._clean_false_to_empty(
                                                              adm_house_address, ['street'], '.')),
                                                              'city': str(self._clean_false_to_empty(
                                                                  adm_house_address, ['city'], '.')),
                                                              'state': str(self._clean_false_to_empty(
                                                                  adm_house_address, ['state_id', 'name'], '.')),
                                                              'zip': str(self._clean_false_to_empty(
                                                                  adm_house_address, ['zip'], '.')),
                                                              'country': str(self._clean_false_to_empty(
                                                                  adm_house_address, ['country_id', 'name'], '.'))
                                                          }, 'addressID')

                body_address = {
                    "addressID": address_facts_id,
                    "address1": str(self._clean_false_to_empty(
                        adm_house_address, ['street'], 'Address of family %s' % adm_family.name)),
                    "city": str(self._clean_false_to_empty(
                        adm_house_address, ['city'], 'Default city')),
                    "state": str(self._clean_false_to_empty(adm_house_address, ['state_id', 'name'], 'Default State')),
                    "zip": str(self._clean_false_to_empty(
                        adm_house_address, ['zip'], 'Default ZIP')),
                    "country": str(
                        self._clean_false_to_empty(adm_house_address, ['country_id', 'name'], 'Default Country')),
                }

                if address_facts_id == -1:
                    _logger.info("-1")
                    res_address = self._send_request(self.api_base_url + '/people/Address', 'post', headers,
                                                     json.dumps(body_address))
                    address_facts_id = json.loads(res_address.text)['addressID']
                    adm_house_address.write({'facts_id': address_facts_id})
                else:
                    _logger.info("else")
                    _logger.info(self.api_base_url + '/people/Address/%s')
                    _logger.info(json.dumps(body_address))

                    res_address = self._send_request(self.api_base_url + '/people/Address/%s' % address_facts_id, 'put',
                                                     headers,
                                                     json.dumps(body_address))

                    # self._save_in_log(server, self.api_base_url + '/people/Address/%s' % address_facts_id, datetime.now(), server.id,
                    #                   'adm.home_address',
                    #                   adm_house_address.id, res_address.status_code, str(res_address.request.body), str(res_address.text),
                    #                   'put')
                _logger.info(res_address.text)
                created_students = log_registers.mapped(lambda x: x.item_id)
                available_persons = list(filter(lambda x: x['personId'] not in created_students, students))

                # si hay estudiantes unkown en FACTS y no han sido utilizados anteriormente
                # (es decir no estan en el log de odoo)
                # se toman para ser usados en la creación de las personas
                # se comprueba que existan tantas personas disponibles como total a introducir + el student
                # de lo contrario se envia un mensaje al usuario indicando como incrementar este número
                if len(available_persons) > len(adm_relationships) + 1:
                    # compute_json_data = self.json_configuration_id.get_json(self.json_configuration_id,
                    #                                                         env_res_partner.browse(
                    #                                                             [application.partner_id.id]),
                    #                                                         self.json_pretty)

                    # student = application.partner_id

                    #
                    # self.env['res.partner'].browse([8223]).write(
                    #     {'suffix': int(self.env['res.partner'].browse([8223]).suffix) + 1})

                    # return {'type': 'ir.actions.act_window',
                    #         'name': _('Mark as Done'),
                    #         'res_model': 'sincro_data.server',
                    #         'target': 'new',
                    #         'view_id': self.env.ref('sincro_data.view_sincro_data_server_done_wizard').id,
                    #         'view_mode': 'form',
                    #         'context': {}
                    #         }
                    # application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                    #     [('sequence', '=', application.status_id.sequence - 1)]).id})
                    # self._cr.commit()
                    # raise ValidationError("Schoolcode %s not exists in FACTS.")

                    # sid ya existe en el sistema lo actualizamos, de lo contrario tomamos un unknow
                    student = application.partner_id
                    school_code_raw = self._send_request(
                        self.api_base_url + '/SchoolConfigurations?filters=schoolCode==%s' % application_grade_level.school_code_id.name,
                        'get', headers,
                        json.dumps({}))

                    if len(json.loads(school_code_raw.text)['results']) == 0:
                        application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                            [('sequence', '=', application.status_id.sequence - 1)]).id})
                        self._cr.commit()
                        raise ValidationError(
                            "Schoolcode %s not exists in FACTS." % application_grade_level.school_code_id.name)
                    else:
                        school_code_id = json.loads(school_code_raw.text)['results'][0]['configSchoolID']
                        next_year_id = json.loads(school_code_raw.text)['results'][0]['nextYearId']
                        # default_year_id = json.loads(school_code_raw.text)['results'][0]['defaultYearId']

                    if not student.facts_id:
                        # unk_person = available_persons.pop()
                        new_student_res = self._send_request(self.api_base_url + '/Students', 'post', headers,
                                                             json.dumps({"configSchoolId": school_code_id}))
                        student.write({'facts_id': json.loads(new_student_res.text)['studentId']})

                        # self._save_in_log(server, self.api_base_url + '/Students',
                        #                   datetime.now(), server.id,
                        #                   'res.partner',
                        #                   student.id, new_student_res.status_code, str(new_student_res.request.body), str(new_student_res.text),
                        #                   'post')
                    stud_person_facts_raw = self._send_request(
                        self.api_base_url + '/Students?filters=studentId==%s' % student.facts_id,
                        'get', headers,
                        json.dumps({}))

                    if len(json.loads(stud_person_facts_raw.text)['results']) == 0:
                        application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                            [('sequence', '=', application.status_id.sequence - 1)]).id})
                        self._cr.commit()
                        raise ValidationError(
                            "PersonID %s not exists in FACTS." % student.facts_id)

                    stud_person_facts_id = json.loads(stud_person_facts_raw.text)['results'][0]['personStudentId']

                    # AÑO ACTUAL POR DEFECTO
                    status_aux = str(
                        self._clean_false_to_empty(application, ['status_id', 'current_year_status_to_facts', 'key'],
                                                   ''))
                    grade_level_aux = str(self._clean_false_to_empty(application_grade_level, ['name'], ''))
                    next_status_aux = str(self._clean_false_to_empty(application,
                                                                     ['status_id',
                                                                      'current_year_next_status_to_facts',
                                                                      'key'],
                                                                     ''))
                    next_school_code = str(
                        self._clean_false_to_empty(application_grade_level,
                                                   ['next_grade_level_id', 'school_code_id', 'name'], ''))
                    next_grade_level = str(
                        self._clean_false_to_empty(application_grade_level,
                                                   ['next_grade_level_id', 'name'],
                                                   ''))

                    # Si fuera del año siguiente
                    _logger.info("application.school_year.facts_id == next_year_id --> %s == %s" % (
                        application_school_year.facts_id, next_year_id))
                    if application_school_year.facts_id == next_year_id:
                        status_aux = str(
                            self._clean_false_to_empty(application,
                                                       ['status_id', 'next_years_status_to_facts', 'key'], ''))

                        next_status_aux = str(self._clean_false_to_empty(application,
                                                                         ['status_id',
                                                                          'next_years_next_status_to_facts',
                                                                          'key'],
                                                                         ''))
                        next_school_code = str(
                            self._clean_false_to_empty(application_grade_level, ['school_code_id', 'name'], ''))
                        next_grade_level = str(self._clean_false_to_empty(application_grade_level, ['name'], ''))
                        grade_level_aux = ''

                    # reenrollment_status_to_facts, sub_status_to_facts NO SE ACTUALIZAN
                    body_student_json = {
                        "school": {
                            "status": status_aux,
                            "gradeLevel": grade_level_aux,
                            "nextStatus": next_status_aux,
                            "nextSchoolCode": next_school_code,
                            "nextGradeLevel": next_grade_level
                        },
                        "locker": []
                    }
                    _logger.info('student : %s' % self.api_base_url + '/Students/%s' % stud_person_facts_id)
                    _logger.info('GRADE LEVEL : %s' % json.dumps(body_student_json))
                    res_student = self._send_request(self.api_base_url + '/Students/%s' % stud_person_facts_id, 'put',
                                                     headers, json.dumps(body_student_json))

                    # self._save_in_log(server, self.api_base_url + '/Students/%s' % stud_person_facts_id,
                    #                   datetime.now(), server.id,
                    #                   'res.partner',
                    #                   student.id, res_student.status_code, str(res_student.request.body),
                    #                   str(res_student.text),
                    #                   'put')
                    body_person_json = {
                        "firstName": str(self._clean_false_to_empty(application, ['partner_id', 'first_name'], '')),
                        "lastName": str(self._clean_false_to_empty(application, ['partner_id', 'last_name'], '')),
                        "middleName": str(self._clean_false_to_empty(application, ['partner_id', 'middle_name'], '')),
                        # "email": email,
                        "homePhone": str(self._clean_false_to_empty(application, ['partner_id', 'phone'], '')).zfill(
                            10),
                        "cellPhone": str(self._clean_false_to_empty(application, ['partner_id', 'mobile'], '')).zfill(
                            10),
                        "addressID": address_facts_id,
                        "deceased": False,
                    }

                    email = str(self._clean_false_to_empty(application, ['partner_id', 'email'], ''))
                    if re.search(REGEX_EMAIL, email) and not re.search(REGEX_EMAIL, email) is None:
                        body_person_json['email'] = email

                    res_person = self._send_request(self.api_base_url + '/people/%s' % adm_student.facts_id, 'put',
                                                    headers, json.dumps(body_person_json))

                    # self._save_in_log(server, self.api_base_url + '/Students/%s' % stud_person_facts_id,
                    #                   datetime.now(), server.id,
                    #                   'res.partner',
                    #                   student.id, res_person.status_code, str(res_person.request.body),
                    #                   str(res_person.text),
                    #                   'put')
                    # ACTUALIZAMOS LA INFORMACIÓN DEMOGRAFICA DEL PERSON
                    # birth_country = adm_student.country_id
                    # if birth_country:
                    #     birth_country = birth_country.name
                    #
                    # person_gender = adm_student.gender
                    # if person_gender:
                    #     person_gender = person_gender.name

                    person_birthdate = adm_student.date_of_birth
                    if person_birthdate:
                        person_birthdate = person_birthdate.strftime("%m-%d-%Y")
                    person_demographic = {
                        "personId": adm_student.facts_id,
                        "gender": str(self._clean_false_to_empty(adm_student, ['gender', 'name'], '')),
                        "birthdate": str(self._clean_false_to_empty(person_birthdate, [], '')),
                        "ethnicity": str(self._clean_false_to_empty(adm_student, ['ethnicity'], '')),
                        "citizenship": str(self._clean_false_to_empty(adm_student, ['facts_citizenship'], '')),
                        "primaryLanguage": str(self._clean_false_to_empty(adm_student, ['primary_language'], '')),
                        "birthplace": str(self._clean_false_to_empty(adm_student, ['birth_city'], '')),
                        "birthCity": str(self._clean_false_to_empty(adm_student, ['birth_city'], '')),
                        "birthState": str(self._clean_false_to_empty(adm_student, ['birth_state'], '')),
                        "birthCountry": str(self._clean_false_to_empty(adm_student, ['country_id', 'name'], ''))
                    }
                    res_person = self._send_request(
                        'https://api.factsmgt.com/people/%s/Demographic' % adm_student.facts_id, 'put',
                        headers, json.dumps(person_demographic))

                    # ACTUALIZAMOS TODA LA INFORMACIÓN DEL ESTUDIANTE REFERENTE A LOS UD
                    self._update_user_defined_data(application, 'students', adm_student, headers)

                    # COMPRUEBO SI EXISTE LA RELACION ENTRE EL ESTUDIANTE Y LA FAMILIA
                    check_path = self.api_base_url + '/people/PersonFamily/family/%s/person/%s' % (
                        adm_family.facts_id, adm_student.facts_id)

                    res = self._send_request(check_path, 'get', headers, '{}')
                    # Si la direccion existe la tomamos del request anterior, de lo contrario la creamos en FACTS
                    if res.status_code != 200:
                        res = self._send_request(self.api_base_url + '/people/PersonFamily', 'post', headers,
                                                 json.dumps({
                                                     "personId": adm_student.facts_id,
                                                     "familyId": adm_family.facts_id,
                                                     "parent": False,
                                                     "student": True,
                                                 }))

                    for rel in application.relationship_ids:
                        person = rel.partner_2
                        body_person_json = {
                            "firstName": str(self._clean_false_to_empty(person, ['first_name'], '')),
                            "lastName": str(self._clean_false_to_empty(person, ['last_name'], '')),
                            "middleName": str(self._clean_false_to_empty(person, ['middle_name'], '')),
                            # "email": str(self._clean_false_to_empty(person, ['email'], '')),
                            "homePhone": str(self._clean_false_to_empty(person, ['phone'], '')).zfill(10),
                            "cellPhone": str(self._clean_false_to_empty(person, ['mobile'], '')).zfill(10),
                            "addressID": address_facts_id,
                            "deceased": False,
                        }

                        email = str(self._clean_false_to_empty(person, ['email'], ''))
                        if not re.search(REGEX_EMAIL, email):
                            body_person_json['email'] = email

                        rel_person_id = person.facts_id
                        if not rel_person_id:
                            unk_person = available_persons.pop()
                            rel_person_id = unk_person['personId']
                            person.write({'facts_id': unk_person['personId']})

                        res_person = self._send_request(self.api_base_url + '/people/%s' % person.facts_id, 'put',

                                                        headers, json.dumps(body_person_json))
                        created_log = env_log.create({
                            'url': 'create_facts',
                            'item_id': rel_person_id,
                            'created_date': datetime.now(),
                            'status_code': res_person.status_code,
                            'request': str(res_person.request.body),
                            'response': res_person.text
                        })

                        # ACTUALIZAMOS TODA LA INFORMACIÓN DEL ESTUDIANTE REFERENTE A LOS UD
                        self._update_user_defined_data(application, 'family_individual', person, headers)

                        # ACTUALIZAMOS LA INFORMACIÓN DEMOGRAFICA DEL PERSON member family
                        # birth_country = person.country_id
                        # if birth_country:
                        #     birth_country = birth_country.name
                        #
                        # person_gender = person.gender
                        # if person_gender:
                        #     person_gender = person_gender.name

                        person_birthdate = person.date_of_birth
                        if person_birthdate:
                            person_birthdate = person_birthdate.strftime("%m-%d-%Y")

                        person_demographic = {
                            "personId": person.facts_id,
                            "gender": str(self._clean_false_to_empty(person, ['gender', 'name'], '')),
                            "birthdate": str(self._clean_false_to_empty(person_birthdate, [], '')),
                            "ethnicity": str(self._clean_false_to_empty(person, ['ethnicity'], '')),
                            "citizenship": str(self._clean_false_to_empty(person, ['facts_citizenship'], '')),
                            "primaryLanguage": str(self._clean_false_to_empty(person, ['primary_language'], '')),
                            "birthplace": str(self._clean_false_to_empty(person, ['birth_city'], '')),
                            "birthCity": str(self._clean_false_to_empty(person, ['birth_city'], '')),
                            "birthState": str(self._clean_false_to_empty(person, ['birth_state'], '')),
                            "birthCountry": str(self._clean_false_to_empty(person, ['country_id', 'name'], ''))
                        }
                        res_person = self._send_request(
                            'https://api.factsmgt.com/people/%s/Demographic' % person.facts_id, 'put',
                            headers, json.dumps(person_demographic))

                        # CREAR/ACTUALIZAS ADD FAMILY
                        check_path = self.api_base_url + '/people/PersonFamily/family/%s/person/%s' % (
                            adm_family.facts_id, person.facts_id)

                        res = self._send_request(check_path, 'get', headers, '{}')
                        # Si la direccion existe la tomamos del request anterior, de lo contrario la creamos en FACTS
                        if res.status_code != 200:
                            res = self._send_request(self.api_base_url + '/people/PersonFamily', 'post', headers,
                                                     json.dumps({
                                                         "personId": person.facts_id,
                                                         "familyId": adm_family.facts_id,
                                                         "parent": True,
                                                         "student": False,
                                                         "financialResponsibility": adm_student.id in person.financial_res_ids.ids,
                                                         "familyOrder": 2,
                                                         "factsCustomer": False
                                                     }))

                        # CREAR  RELATIONSHIPS
                        check_path = self.api_base_url + '/people/ParentStudent?filters=parentID==%s,studentID==%s' % (
                            person.facts_id, adm_student.facts_id)

                        res = self._send_request(check_path, 'get', headers, '{}')
                        # Si la direccion existe la tomamos del request anterior, de lo contrario la creamos en FACTS
                        if len(json.loads(res.text)['results']) == 0:
                            res = self._send_request(self.api_base_url + '/people/ParentStudent', 'post', headers,
                                                     json.dumps({
                                                         "parentID": person.facts_id,
                                                         "studentID": adm_student.facts_id,
                                                         "custody": rel.custody,
                                                         "correspondence": rel.correspondence,
                                                         "relationship": rel.relationship_type_id.name,
                                                         "grandparent": rel.grand_parent,
                                                         "emergencyContact": rel.is_emergency_contact,
                                                         "reportCard": rel.grade_related,
                                                         "pickUp": False,
                                                         "parentsWeb": rel.family_portal
                                                     }))

                        res = self._send_request(self.api_base_url + '/people/ParentStudent/parent/%s/student/%s' % (
                            person.facts_id, adm_student.facts_id), 'put', headers,
                                                 json.dumps({
                                                     "parentID": person.facts_id,
                                                     "studentID": adm_student.facts_id,
                                                     "custody": rel.custody,
                                                     "correspondence": rel.correspondence,
                                                     "relationship": rel.relationship_type_id.name,
                                                     "grandparent": rel.grand_parent,
                                                     "emergencyContact": rel.is_emergency_contact,
                                                     "reportCard": rel.grade_related,
                                                     "pickUp": False,
                                                     "parentsWeb": rel.family_portal
                                                 }))
                        # self._cr.commit()
                        # raise ValidationError(
                        #     "The Student was imported correctly!.")
                else:
                    application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                        [('sequence', '=', application.status_id.sequence - 1)]).id})
                    self._cr.commit()
                    raise ValidationError(
                        "Please run the report in the next path: Report Manager/Custom/Create Students For Admissions Odoo.")

    def _find_in_list(self, application, list_json, fields_to_check, value, field_return_name):
        if len(list_json) == 0:
            application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                [('sequence', '=', application.status_id.sequence - 1)]).id})
            self._cr.commit()
            raise ValidationError("Problems with the connected to FACTS")
        for field in fields_to_check:
            if field not in list_json[0]:
                application.write({'status_id': self.env['%s.status' % self.model_id.model].search(
                    [('sequence', '=', application.status_id.sequence - 1)]).id})
                self._cr.commit()
                raise ValidationError("A field to checked not exists in the list_json[0]")
        for item in list_json:
            i = 0
            for checked_field in fields_to_check:
                if checked_field in item and str(item[checked_field]) == str(value[checked_field]):
                    i += 1

            if i == len(fields_to_check):
                return item[field_return_name]

        return -1

    # FUNCION QUE COMPRUEBA SI ES False devuelve vacio, el booleano recur determina si es un objeto y comprueba de izquierda a derecha si es vacio para devolver el vacio
    def _clean_false_to_empty(self, value, chain, default_value):
        if not value:
            return default_value
        recur_val = value
        for inner_itm in chain:
            if inner_itm not in recur_val or (inner_itm in recur_val and not recur_val[inner_itm]):
                return default_value
            recur_val = recur_val[inner_itm]

        return recur_val

    def _check_and_create_in_facts(self, check_path, insert_path, headers, json_data):
        res = self._send_request(check_path, 'get', headers, '{}')

        # Si la direccion existe la tomamos del request anterior, de lo contrario la creamos en FACTS
        if 'results' not in json.loads(res.text) or len(json.loads(res.text)['results']) == 0:
            res = self._send_request(insert_path, 'post', headers, json.dumps(json_data))

        return res

    def action_retrieve_data(self, *args):
        _logger.info("___________________")
        _logger.info("ACTION SELF")
        _logger.info("___________________")
        for server in self:
            _logger.info("++++++++++++++++++++")
            _logger.info("ACTION RETRIEVE DATA")
            _logger.info(str(server.name))
            _logger.info("++++++++++++++++++++")
            self.ensure_one()
            if self.method == 'create_facts':
                return self.action_create_person_facts(args)
            cron_env = self.env['ir.cron']
            env_id = self.env['ir.model'].search([('model', '=', 'sincro_data.server')]).id
            cron_name = 'Cron of sincro_data: %s (%s)' % (self.name, self.id)
            existed_cron = cron_env.search(
                ['|', ('active', '=', False), ('active', '=', True), ('name', '=', cron_name)])

            if not existed_cron:
                existed_cron = existed_cron.create({
                    'name': cron_name,
                    'model_id': env_id,
                    'interval_number': self.interval_minutes,
                    'interval_type': 'minutes',
                    'numbercall': -1,
                    'state': 'code',
                    'active': True,
                    # 'code': 'model.search([]).with_context(email_error=True).action_retrieve_data'
                    'code': 'model.browse(%s).with_context(email_error=True).action_retrieve_data()' % self.id
                })
            error_msgs = {}
            headers = {}
            for header in server.api_header_ids:
                headers[header.name] = header.value

            aux_domain = safe_eval(self.domain or "[]")
            env_aux = self.env[self.model_id.model]

            filtered_items = env_aux.search(aux_domain)

            for item in filtered_items:
                computed_path = self.api_base_url + self.path % tuple(
                    reversed(tuple(map(lambda value: env_aux.browse([item.id])[
                        value.field_value.name] if value.type != 'constant' else value.constant_value,
                                       self.parameter_ids))))

                compute_json_data = self.json_configuration_id.get_json(self.json_configuration_id,
                                                                        env_aux.browse(
                                                                            [item.id]),
                                                                        self.json_pretty)

                res = self._send_request(computed_path, server.method, headers, compute_json_data)

                env_log = self.env['sincro_data.log']
                server.retrieve_date = datetime.now()

                # response_code = res.status_code
                created_log = env_log.create({
                    'url': computed_path,
                    'item_id': item.id,
                    'created_date': datetime.now(),
                    'model': str(env_id),
                    'status_code': res.status_code,
                    'server_id': self.id,
                    'request': str(res.request.body),
                    'response': res.text
                })
                self.log_ids = [(4, created_log.id)]

    def _send_request(self, url, method, headers, body):
        self.ensure_one()
        return requests.request(method, url, headers=headers, json=json.loads(body))

    def _save_in_log(self, server, url, created_date, server_id, model='', item_id=-1, status_code='', request='',
                     response='', method=''):
        env_log = self.env['sincro_data.log']
        server.retrieve_date = datetime.now()
        created_log = env_log.create({
            'url': url,
            'item_id': item_id,
            'created_date': created_date,
            'model': str(model),
            'method': method,
            'server_id': server_id,
            'status_code': status_code,
            'request': str(request),
            'response': str(response)
        })
        self.log_ids = [(4, created_log.id)]

    def action_done(self):
        f = 2
        return {}

    # def _send_request(self, url, method, headers):
    #     self.ensure_one()
    #     return requests.request(method, url, headers=headers)
