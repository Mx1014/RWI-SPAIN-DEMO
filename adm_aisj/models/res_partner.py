# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    c_aisj_employer = fields.Char()
    c_aisj_occupation = fields.Char()

    c_aisj_parent_question_1 = fields.Char('Interested in being an AISJ business partner donation')
    c_aisj_parent_question_2 = fields.Selection([('yes', 'Yes'), ('no', 'No')],
                                                "May we provide your contact information to our Parent Teacher Support Association (PTSA) so that they might reach out to welcome you?")

    identification = fields.Char("Identification", default="N/A", required=True)

    iqama_document_file = fields.Binary(string="Iqama document", attachment=True)
    iqama_document_file_name = fields.Char(string="Iqama document")
