# -*- coding: utf-8 -*-
{
    'name': 'Time Off Portal',

    'summary': """ Time Off Portal """,

    'description': """
        Time Off Portal
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Human Resources',
    'version': '1.0',

    'depends': [
        'web',
        'portal',
        'hr_holidays',
        'hr_holidays_extends',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/hr_leave_security.xml',
        'data/res_groups_data.xml',
        'views/assets.xml',
        'views/hr_leave_portal_templates.xml',
        'views/mail_templates.xml',
        'views/hr_leave_views.xml',
    ],
}