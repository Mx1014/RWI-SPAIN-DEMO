# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError
from odoo import exceptions
import logging
import json

_logger = logging.getLogger(__name__)

SELECT_STATUS_TYPES = [
    ("admissions", "Admissions"),
    ("enrolled", "Enrolled"),
    ("graduate", "Graduate"),
    ("inactive", "Inactive"),
    ("pre-enrolled", "Pre-Enrolled"),
    ("withdrawn", "Withdrawn"),
]


# clase encargada de linkear las familia con un estudiante apra en la creaciond el registro de reenrollment se asigne un familyid y de esta
# manera poder crear información relacionado con ese campo en el modelo mencionado anteriormente.
class StudentAuxInfo(models.Model):
    _name = "adm.application.question"
    student_id = fields.Many2one(string="Question")
    family_id = fields.Many2one(string="Answer")


class ExportDataWizard(models.Model):
    _name = 'sincro_data.export_data_wizard'

    def get_all_reenrollments(self):
        return self.env['adm.reenrollment'].search([]).partner_id.ids
        # return str(self.env['res.partner'].search([]).ids)

    def get_open_students(self):
        # return self.env['res.partner'].search(
        #     [('person_type', '=', 'student'), ('reenrollment_status_id', '=', 'open')]).filtered(
        #     lambda open_stud: open_stud.id not in self.env['adm.reenrollment'].search([]).partner_id.ids)
        return self.env['res.partner'].search([])

    def get_items(self):
        # return self.env['res.partner'].search(
        #     [('person_type', '=', 'student'), ('reenrollment_status_id', '=', 'open')]).filtered(
        #     lambda open_stud: open_stud.id not in self.env['adm.reenrollment'].search([]).partner_id.ids)
        return self.env['sincro_data.export_data'].search([])

    example_1 = fields.Char()
    example_2 = fields.Char()

    items = fields.One2many("sincro_data.export_data", "export_data_wizard_id", "Items",default=get_items)

    def import_all_students(self):
        HouseAddressEnv = self.env["adm.house_address"].sudo()
        PartnerEnv = self.env["res.partner"].sudo()
        RelationshipEnv = self.env["school_base.relationship"].sudo()
        all_students = self.env['res.partner'].search(
            [('person_type', '=', 'student'), ('reenrollment_status_id', '=', 'open')]).filtered(
            lambda open_stud: open_stud.id not in self.env['adm.reenrollment'].search([]).partner_id.ids)

        for student in all_students:

            country_aux_id = student.country_id.id
            if not country_aux_id:
                country_aux_id = self.env['ir.config_parameter'].sudo().get_param('default_country_id', '')

            ReenrollmentEnv = self.env['adm.reenrollment']
            if len(ReenrollmentEnv.search([('partner_id', '=', student.id)])) == 0:
                houseInfoReenrollment = {
                    "name": "House",
                    "country_id": country_aux_id,
                    "state_id": student.state_id.id,
                    "city": student.city,
                    "zip": student.zip,
                    "street": student.street,
                    "phone": student.phone,
                    "family_id": student.family_ids[0].id
                }

                house_id_facts = PartnerEnv.browse(student.family_ids[0].id).house_address_ids.filtered(
                    lambda house_addres: house_addres.name == "House")

                if len(house_id_facts) > 0:
                    HouseAddressEnv.sudo().browse(house_id_facts[0].id).write(houseInfoReenrollment)
                    facts_family_house = house_id_facts[0]
                else:
                    facts_family_house = HouseAddressEnv.sudo().create(houseInfoReenrollment)

                updateFamilyId = PartnerEnv.browse([student.family_ids[0].id]).sudo().write(
                    {'house_address_ids': [(4, facts_family_house.id)]})

                # 'house_address_ids': [(4, new_house.id)]}
                params = {
                    'partner_id': student.id,
                    'first_name': student.first_name,
                    'middle_name': student.middle_name,
                    'last_name': student.last_name,
                    'school_year_id': student.reenrollment_school_year_id.id,
                    'grade_level_id': student.next_grade_level_id.id,
                    'family_id': student.family_ids[0].id
                }
                new_reenrollment = ReenrollmentEnv.create(params)

                # Añadimos los medical conditions por defecto, si no existieran
                default_medical_conditions = ['Ambientales (Hongo,ácaros, humedad, polvo,etc).', 'Alimenticias',
                                              'Dieta Especial', 'Antecedentes médico e importancia',
                                              '¿Que procedimientos quirúrgicos ha sido sometido?',
                                              '¿En algún momento ha presentado desmayo o perdida de conocimiento?',
                                              'Acude con algún especialista a control regularmente, favor anotar nombre y teléfono del (los) especialista(s)']

                medical_base = []

                for def_med in default_medical_conditions:
                    if def_med not in list(map(lambda elem: elem.name, student.medical_conditions_ids)):
                        medical_base.append((0, 0, {
                            'name': def_med,
                            'comment': '',
                        }))

                student.write({
                    "medical_conditions_ids": medical_base,
                })

                # Añadimos como followers a los usuarios que pertenezcan la grupo correspondiente
                FollowerEnv = self.env["mail.followers"].sudo()

                # BORRAMOS LOS FOLLOWERS POR DEFECTO DEL APPLICATION
                FollowerEnv.search(
                    [('res_model', '=', 'adm.reenrollment'), ('res_id', '=', new_reenrollment.id)]).unlink()

                # COPIA LOS FOLLOWERS DEL INQUIRY AL APPLCIATION
                school_code_config = self.env['adm.general_settings'].search(
                    [("school_code_id", "=", new_reenrollment.grade_level_id.school_code_id.id)])
                member_admission_group_ids = school_code_config.default_follower_reenrollment_group_id.users.partner_id.ids

                for member_id in member_admission_group_ids:
                    new_followers = FollowerEnv.sudo().create({
                        'res_model': "adm.reenrollment",
                        'partner_id': member_id,
                        'res_id': new_reenrollment.id,
                        'subtype_ids': [(6, False, [1, 3, 2])],
                    })

                for data in PartnerEnv.sudo().browse([student.family_ids[0].id]).relationship_members_ids:
                    if data.partner_2.id == student.id:
                        aux_data = data.copy_data()[0]
                        related_family_parent_student = RelationshipEnv.search(
                            [("partner_1", "=", aux_data['partner_2']), ("partner_2", "=", aux_data['partner_1']),
                             ("family_id", "=", aux_data['family_id']),
                             ("relationship_type_id", "=", aux_data['relationship_type_id']),
                             ("reenrollment_id", "=", new_reenrollment.id)])

                        if len(related_family_parent_student) < 1:
                            aux_data['reenrollment_id'] = new_reenrollment.id
                            aux_partner = aux_data['partner_1']
                            aux_data['partner_1'] = aux_data['partner_2']
                            aux_data['partner_2'] = aux_partner
                            RelationshipEnv.create(aux_data)

                        PartnerEnv.browse(aux_data['partner_1']).write(
                            {"house_address_reenrollment_id": facts_family_house.id})

                        pass

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def import_students(self):
        HouseAddressEnv = self.env["adm.house_address"].sudo()
        PartnerEnv = self.env["res.partner"].sudo()
        RelationshipEnv = self.env["school_base.relationship"].sudo()

        for student in self.reenrollment_open_students:

            country_aux_id = student.country_id.id
            if not country_aux_id:
                country_aux_id = self.env['ir.config_parameter'].sudo().get_param('default_country_id', '')

            ReenrollmentEnv = self.env['adm.reenrollment']
            if len(ReenrollmentEnv.search([('partner_id', '=', student.id)])) == 0:
                houseInfoReenrollment = {
                    "name": "House",
                    "country_id": country_aux_id,
                    "state_id": student.state_id.id,
                    "city": student.city,
                    "zip": student.zip,
                    "street": student.street,
                    "phone": student.phone,
                    "family_id": student.family_ids[0].id
                }

                house_id_facts = PartnerEnv.browse(student.family_ids[0].id).house_address_ids.filtered(
                    lambda house_addres: house_addres.name == "House")

                if len(house_id_facts) > 0:
                    HouseAddressEnv.sudo().browse(house_id_facts[0].id).write(houseInfoReenrollment)
                    facts_family_house = house_id_facts[0]
                else:
                    facts_family_house = HouseAddressEnv.sudo().create(houseInfoReenrollment)

                updateFamilyId = PartnerEnv.browse([student.family_ids[0].id]).sudo().write(
                    {'house_address_ids': [(4, facts_family_house.id)]})

                # 'house_address_ids': [(4, new_house.id)]}
                params = {
                    'partner_id': student.id,
                    'first_name': student.first_name,
                    'middle_name': student.middle_name,
                    'last_name': student.last_name,
                    'school_year_id': student.reenrollment_school_year_id.id,
                    'grade_level_id': student.next_grade_level_id.id,
                    'family_id': student.family_ids[0].id
                }
                new_reenrollment = ReenrollmentEnv.create(params)

                # Añadimos los medical conditions por defecto, si no existieran
                default_medical_conditions = ['Ambientales (Hongo,ácaros, humedad, polvo,etc).', 'Alimenticias',
                                              'Dieta Especial', 'Antecedentes médico e importancia',
                                              '¿Que procedimientos quirúrgicos ha sido sometido?',
                                              '¿En algún momento ha presentado desmayo o perdida de conocimiento?',
                                              'Acude con algún especialista a control regularmente, favor anotar nombre y teléfono del (los) especialista(s)']

                medical_base = []

                for def_med in default_medical_conditions:
                    if def_med not in list(map(lambda elem: elem.name, student.medical_conditions_ids)):
                        medical_base.append((0, 0, {
                            'name': def_med,
                            'comment': '',
                        }))

                student.write({
                    "medical_conditions_ids": medical_base,
                })

                # Añadimos como followers a los usuarios que pertenezcan la grupo correspondiente
                FollowerEnv = self.env["mail.followers"].sudo()

                # BORRAMOS LOS FOLLOWERS POR DEFECTO DEL APPLICATION
                FollowerEnv.search(
                    [('res_model', '=', 'adm.reenrollment'), ('res_id', '=', new_reenrollment.id)]).unlink()

                # COPIA LOS FOLLOWERS DEL INQUIRY AL APPLCIATION
                school_code_config = self.env['adm.general_settings'].search(
                    [("school_code_id", "=", new_reenrollment.grade_level_id.school_code_id.id)])
                member_admission_group_ids = school_code_config.default_follower_reenrollment_group_id.users.partner_id.ids

                for member_id in member_admission_group_ids:
                    new_followers = FollowerEnv.sudo().create({
                        'res_model': "adm.reenrollment",
                        'partner_id': member_id,
                        'res_id': new_reenrollment.id,
                        'subtype_ids': [(6, False, [1, 3, 2])],
                    })

                for data in PartnerEnv.sudo().browse([student.family_ids[0].id]).relationship_members_ids:
                    if data.partner_2.id == student.id:
                        aux_data = data.copy_data()[0]
                        related_family_parent_student = RelationshipEnv.search(
                            [("partner_1", "=", aux_data['partner_2']), ("partner_2", "=", aux_data['partner_1']),
                             ("family_id", "=", aux_data['family_id']),
                             ("relationship_type_id", "=", aux_data['relationship_type_id']),
                             ("reenrollment_id", "=", new_reenrollment.id)])

                        if len(related_family_parent_student) < 1:
                            aux_data['reenrollment_id'] = new_reenrollment.id
                            aux_partner = aux_data['partner_1']
                            aux_data['partner_1'] = aux_data['partner_2']
                            aux_data['partner_2'] = aux_partner
                            RelationshipEnv.create(aux_data)

                        PartnerEnv.browse(aux_data['partner_1']).write(
                            {"house_address_reenrollment_id": facts_family_house.id})

                        pass

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def agent_exceed_limit(self):
        _logger.debug(' \n\n \t We can do some actions here\n\n\n')
