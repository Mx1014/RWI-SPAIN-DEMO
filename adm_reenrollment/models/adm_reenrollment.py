# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import safe_eval

SELECT_REENROLLMENT_STATUS = [
    ("open", "Open"),
    ("finished", "Finished"),
    ("withdrawn", "Withdrawn"),
    ("rejected", "Rejected"),
    ("blocked", "Blocked"),
    ]


class AdmReenrollmentTask(models.Model):
    _name = 'adm.reenrollment.task'
    _description = "Reenrollment task"

    name = fields.Char()
    stage_id = fields.Many2one('adm.reenrollment.stage')


class AdmReenrollmentStage(models.Model):
    _name = 'adm.reenrollment.stage'
    _order = 'sequence'
    _description = "Reenrollment stage"

    name = fields.Char("Status Name")
    description = fields.Text("Description")
    sequence = fields.Integer(readonly=True, default=-1)
    fold = fields.Boolean("Fold")
    type = fields.Selection([
            ("start", "Start"),
            ("stage", "Stage"),
            ("returning", "Returning"),
            ("not_returning", "Not returning"),
        ], default='stage')

    task_ids = fields.One2many('adm.reenrollment.task', 'stage_id')

    reenrollment_status_to_facts = fields.Selection(SELECT_REENROLLMENT_STATUS, string="Reenrollment Status to FACTS")
    sub_status_to_facts = fields.Many2one("school_base.enrollment.sub_status", string="Sub Status to FACTS")
    import_to_facts = fields.Boolean()


class AdmReenrollment(models.Model):
    _name = 'adm.reenrollment'
    _description = "Reenrollment"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    active = fields.Boolean(default=True)

    partner_id = fields.Many2one('res.partner', string='Student')
    name = fields.Char(string="Name", related="partner_id.name")

    stage_id = fields.Many2one('adm.reenrollment.stage', 'Stage', group_expand="_read_group_stage_ids")
    stage_task_ids = fields.One2many('adm.reenrollment.task', related='stage_id.task_ids')

    grade_level_id = fields.Many2one('school_base.grade_level', string="Current Grade level")
    school_year_id = fields.Many2one('school_base.school_year', string=_("Reenrollment school year"))

    user_id = fields.Many2one('res.users')

    ################
    # Demographics #
    ################
    email = fields.Char(string="Email", related="partner_id.email", index=True)
    mobile = fields.Char(string="Phone", related="partner_id.mobile")
    phone = fields.Char(string="Home phone", related="partner_id.phone")
    image = fields.Binary("Applicant´s Photo", related="partner_id.image_1920")

    ##########
    # Family #
    ##########
    family_ids = fields.Many2many(related='partner_id.family_ids')
    family_id = fields.Many2one('res.partner', domain=lambda self: [('is_family', '=', True), ('id', 'in', self.partner_id.family_ids.ids)])
    family_res_id = fields.Integer("Family ID")

    ###############
    # Responsible #
    ###############
    responsible_user_id = fields.Many2one('res.users')
    custody_user_ids = fields.Many2many('res.users', help="All the users here will receive a mail to go to complete the reenrollment")
    custody_partner_ids = fields.Many2many('res.partner',
                                           compute='compute_custody_partner_ids',
                                           store=True,
                                           help="All the partner here will receive a mail to go to complete the reenrollment")
    # responsible_email = fields.Char(related='responsible_user_id.email')

    responsible_school_status = fields.Selection([('parent', _("Parent")), ('staff', _("Staff"))], string="Responsible school status")

    partner_guardian1 = fields.Many2one('res.partner')
    partner_guardian2 = fields.Many2one('res.partner')

    #####################
    # Reenrollment data #
    #####################
    is_returning = fields.Boolean(help=_("Will the student will return to the school?"))
    next_grade_level_id = fields.Many2one('school_base.grade_level', "Next grade level")

    # gpa = fields.Float("GPA", related='partner_id.gpa')
    student_id_documentation_file = fields.Binary(related='partner_id.id_documentation_file', string="ID Documentation", readonly=False)
    student_id_documentation_file_name = fields.Char(related='partner_id.id_documentation_file_name', readonly=False)

    guardian1_id_documentation_file = fields.Binary(related='partner_guardian1.id_documentation_file', string="Guardian 1 ID Documentation", readonly=False)
    guardian1_id_documentation_file_name = fields.Char(related='partner_guardian1.id_documentation_file_name', readonly=False)
    
    guardian2_id_documentation_file = fields.Binary(related='partner_guardian2.id_documentation_file', string="Guardian 2 ID Documentation", readonly=False)
    guardian2_id_documentation_file_name = fields.Char(related='partner_guardian2.id_documentation_file_name', readonly=False)

    ############
    # Location #
    ############
    partner_home_address_id = fields.Many2one('school_base.home_address', related='partner_id.home_address_id')

    #################
    # Relationships #
    #################
    partner_relationship_ids = fields.One2many('school_base.relationship', related='partner_id.relationship_ids')
    #################
    # Documentation #
    #################

    ###################
    # --- Methods --- #
    ###################
    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        return self.env['adm.reenrollment.stage'].search([])

    def get_required_fields(self):
        # First we get the all the fields
        config_parameter = self.env['ir.config_parameter'].sudo()
        reenrollment_required_fields_str = config_parameter.get_param('adm_reenrollment_required_field_ids', '')
        reenrollment_required_fields = [int(e) for e in reenrollment_required_fields_str.split(',') if e.isdigit()]
        required_field_ids = self.env['adm_reenrollment.fields.settings'].sudo().browse(reenrollment_required_fields)

        # Then we filter by the field domain
        filtered_required_fields_ids = self.env['adm_reenrollment.fields.settings'].sudo()
        for required_field_id in required_field_ids:
            if required_field_id.apply_domain_in_records(self):
                filtered_required_fields_ids += required_field_id

        return filtered_required_fields_ids

    def get_optional_fields(self):
        reenrollment_optional_fields_str = self.env['ir.config_parameter'].sudo().get_param('adm_reenrollment_optional_field_ids', '')
        reenrollment_optional_fields = [int(e) for e in reenrollment_optional_fields_str.split(',') if e.isdigit()]
        optional_field_ids = self.env['adm_reenrollment.fields.settings'].sudo().browse(reenrollment_optional_fields)

        filtered_optional_field_ids = self.env['adm_reenrollment.fields.settings'].sudo()
        for required_field_id in optional_field_ids:
            if required_field_id.apply_domain_in_records(self):
                filtered_optional_field_ids += optional_field_ids

        return filtered_optional_field_ids

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AdmReenrollment, self).create(vals_list)
        res._recompute_followers()
        return res

    def write(self, vals):
        res = super(AdmReenrollment, self).write(vals)
        self._recompute_followers()
        return res

    def _recompute_followers(self):
        for record in self:
            student_id = record.partner_id
            partner_ids = student_id.relationship_ids.filtered_domain([('custody', '=', True)]).mapped('partner_2')
            record.message_subscribe(partner_ids=partner_ids.ids)

    @api.depends('partner_relationship_ids', 'partner_relationship_ids.custody')
    def compute_custody_partner_ids(self):
        for reenrollment in self:
            student_id = reenrollment.partner_id
            custody_partner_ids = student_id.relationship_ids.filtered_domain([('custody', '=', True)]).mapped('partner_2')
            reenrollment.custody_partner_ids = custody_partner_ids
        self._recompute_followers()
