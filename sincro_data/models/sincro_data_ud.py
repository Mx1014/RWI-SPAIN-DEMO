# -*- coding:utf-8 -*-

from odoo import models, fields, api


class FieldUD(models.Model):
    _name = "sincro_data.field_ud"
    name = fields.Char(string="Field name")
    odoo_field_id = fields.Many2one('ir.model.fields', string='Odoo field',
                                    domain=[('model', 'in', ['res.partner', 'adm.application', 'adm.reenrollment'])])
    # EN FACTS LOS TIPOS SE DEFINEN POR LA POSICIOIN EN EL USER DEGINED CONFIGURATION
    group_type = fields.Selection([
        ('1', "Text"),
        ('2', "Yes/No"),
        ('3', "Date"),
        ('4', "Integer"),
        ('5', 'Real Number'),
        ('6', 'Defined List Select')
    ],
        string="Field type", default='1'
    )
    group_id = fields.Many2one("sincro_data.group_ud", string="Group")
    facts_id = fields.Integer("Facts ID")


class GroupUD(models.Model):
    _name = "sincro_data.group_ud"
    name = fields.Char(string="Group name")
    district_wide = fields.Boolean(string="District Wide")
    field_ids = fields.One2many("sincro_data.field_ud", "group_id", "Fields")
    group_type_id = fields.Many2one("sincro_data.group_type_ud", string="Group type")
    facts_id = fields.Integer("Facts ID")


class GroupUD(models.Model):
    _name = "sincro_data.group_type_ud"
    name = fields.Char("Name")
    group_type = fields.Selection([
        # ('classes', "Classes"),
        # ('course', "Course"),
        ('families', "Families"),
        ('family_individual', "Family individual"),
        # ('medical', 'Medical'),
        # ('school', "School"),
        # ('staff', "Staff"),
        ('students', "Students"),
    ],
        string="Group type", default='students'
    )
    group_ids = fields.One2many("sincro_data.group_ud", "group_type_id", "Groups")
