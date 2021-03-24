# -*- coding: utf-8 -*-

{
    'name': "Admission Reporting",

    'summary': """
        Reporting Module
    """,

    'description': """""",

    'author': "Eduweb Group SL",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Admission',
    'version': '0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web_dashboard', 'web_cohort', 'web_map', 'adm'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/adm_reporting_inquiry_dashboard.xml',
        'views/adm_reporting_application_dashboard.xml',
        # 'views/adm_reporting_grade_level_student_count_dashboard.xml',
        'views/adm_reporting_menus.xml',
        # 'views/adm_reporting_templates.xml',
    ],
    'application': True
}

