# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime


class CreateReenrollmentRecords(models.TransientModel):
    _name = 'create.reenrollment.records'
    _description = "Reenrollment records"

    next_enrollment_status_id = fields.Many2one('school_base.enrollment.status',
                                                default=lambda self: self.env.company.def_ren_next_enrollment_status_id,
                                                string="Enrollment next status", required=True)
    current_enrollment_status_id = fields.Many2one('school_base.enrollment.status',
                                                   default=lambda self: self.env.company.def_ren_enrollment_status_id,
                                                   string="Enrollment current status")
    student_ids = fields.Many2many('res.partner')
    overwrite_existing_records = fields.Boolean()

    @api.onchange('next_enrollment_status_id', 'current_enrollment_status_id')
    def onchange_next_enrrollment_status(self):
        for record in self:
            if record.next_enrollment_status_id and record.current_enrollment_status_id:
                record.student_ids = self.env['res.partner'].search([('person_type', '=', 'student'),
                                                                     ('student_next_status_id', '=', record.next_enrollment_status_id.id),
                                                                     ('student_status_id', '=', record.current_enrollment_status_id.id)])
            else:
                record.student_ids = False

    def create_records(self):
        for record in self:
            for student_id in record.student_ids:
                next_grade_level_id = student_id.next_grade_level_id
                district_code_id = next_grade_level_id.school_code_id.district_code_id
                reenrollment_school_year_id = self.env['res.company'].search(
                    [('district_code_id', '=', district_code_id.id)]).enrollment_school_year_id

                # Check if there is some existing reenrollment record for the school year
                if (record.overwrite_existing_records or
                    not student_id.reenrollment_record_ids
                                  .filtered(lambda r: r.school_year_id == reenrollment_school_year_id)):
                    student_id.write({
                        'reenrollment_record_ids': [(0, 0, {
                            'reenrollment_status': 'open',
                            'next_grade_level_id': next_grade_level_id.id,
                            'school_year_id': reenrollment_school_year_id.id,
                            'note': "Created by %s at %s in \"CREATE REENROLLMENT RECORDS\" wizard" % (self.env.user.name, str(datetime.datetime.now())),
                            })],
                    })
                student_id._compute_reenrollment_status()
