# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import safe_eval

class AdmReenrollmentSettingsField(models.Model):
    _name = 'adm_reenrollment.fields.settings'
    _description = "Reenrollment field"
    _rec_name = 'field_id'

    field_id = fields.Many2one('ir.model.fields', "Field", required=True)
    relational_model = fields.Char(related='field_id.relation', store=True)

    name = fields.Char(related='field_id.name')

    parent_id = fields.Many2one('adm_reenrollment.fields.settings', string="Parent")
    parent_relational_model = fields.Char(related='parent_id.relational_model')

    child_ids = fields.One2many('adm_reenrollment.fields.settings', 'parent_id', string="Childs")
    long_name = fields.Char(compute="_compute_long_name", store=True)

    domain = fields.Char('Domain filter')

    def _generate_long_name(self):
        return self.name if not self.parent_id else '%s.%s' % (self.parent_id._generate_long_name(), self.name)

    @api.depends('name', 'field_id', 'parent_id')
    def _compute_long_name(self):
        for field in self:
            field.long_name = field._generate_long_name()

    def apply_domain_in_records(self, records):
        self.ensure_one()
        domain = safe_eval(self.domain or '[]')
        return records.filtered_domain(domain)

    def get_as_list_of_names(self):
        name_list = []

        for field in self:
            name_list.append(field.long_name)
            if field.child_ids:
                name_list.extend(field.child_ids.get_as_list_of_names())
        return name_list


class ResConfigSettings(models.TransientModel):
    """  Settings for school base module """
    _inherit = "res.config.settings"

    reenrollment_announcement_mail_template_id = fields.Many2one(
        'mail.template',
        config_parameter='adm_reenrollment.reenrollment_announcement_mail_template_id',
        string="Reenrollment annoucement email template")

    adm_reenrollment_required_field_ids = fields.Many2many(
        'adm_reenrollment.fields.settings',
        string="Reenrollment required fields")

    adm_reenrollment_optional_field_ids = fields.Many2many(
        'adm_reenrollment.fields.settings',
        relation='adm_reen_optional_field_settings',
        string="Reenrollment optional fields")

    def_ren_enrollment_status_id = fields.Many2one('school_base.enrollment.status', related='company_id.def_ren_enrollment_status_id', readonly=False)
    def_ren_next_enrollment_status_id = fields.Many2one('school_base.enrollment.status', related='company_id.def_ren_next_enrollment_status_id', readonly=False)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        config_parameter = self.env['ir.config_parameter'].sudo()
        reenrollment_required_fields_str = config_parameter.get_param(
            'adm_reenrollment_required_field_ids', '')
        reenrollment_required_fields = [
            int(e) for e in reenrollment_required_fields_str.split(',')
            if e.isdigit()
            ]

        reenrollment_optional_fields_str = config_parameter.get_param(
            'adm_reenrollment_optional_field_ids', '')
        reenrollment_optional_fields = [
            int(e) for e in reenrollment_optional_fields_str.split(',')
            if e.isdigit()
            ]

        res.update({
            'adm_reenrollment_required_field_ids': reenrollment_required_fields,
            'adm_reenrollment_optional_field_ids': reenrollment_optional_fields,
            })

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        for settings in self:
            config_parameter = self.env['ir.config_parameter'].sudo()
            config_parameter.set_param('adm_reenrollment_required_field_ids', ",".join(map(str, settings.adm_reenrollment_required_field_ids.ids)))
            config_parameter.set_param('adm_reenrollment_optional_field_ids', ",".join(map(str, settings.adm_reenrollment_optional_field_ids.ids)))