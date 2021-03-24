# -*- coding: utf-8 -*-

{
    'name': "Admission AISJ Customization",

    'summary': """ Module for custom AISJ Admission Process """,

    'description': """ Module for custom AISJ Admission Process """,

    'author': "Eduweb Group SL",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '1',

    # any module necessary for this one to work correctly
    'depends': ['adm', 'adm_reenrollment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/adm_application_views.xml',
        'views/adm_reenrollment_views.xml',
        'views/portal_templates.xml',

        # Templates
        'views/templates/adm_application_templates.xml',
        'views/templates/adm_reenrollment_templates.xml',

        'views/custom/adm_aisj_additional_support.xml',
        'views/custom/adm_aisj_applicant_programs_views.xml',
        'views/custom/adm_aisj_interested_options.xml',
        'views/custom/adm_aisj_how_hear_about_us_views.xml',
        ],
    # 'qweb': [ ],
    # 'application': True
    }


