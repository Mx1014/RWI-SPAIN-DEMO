# -*- coding: utf-8 -*-
{
    'name': 'Form.io Extensions',

    'summary': """ Form.io Extensions """,

    'description': """
        Form.io Extensions
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'formio',
        'website_formio',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/formio_form_views.xml',
        'views/formio_builder_views.xml',
        'views/formio_automation_views.xml',
        'views/formio_form_portal_templates.xml',
        'data/website_page_data.xml',
    ],
}