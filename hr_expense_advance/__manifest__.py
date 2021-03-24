# -*- coding: utf-8 -*-
{
    'name': 'Expenses Advance',

    'summary': """ Expenses Advance """,

    'description': """
        Expenses Advance
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'hr_expense',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/hr_expense_advance_views.xml',
        'views/hr_expense_views.xml',
    ],
}