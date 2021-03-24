# -*- coding: utf-8 -*-
{
    'name': 'Budget Variance',

    'summary': """ Budget Variance """,

    'description': """
        Budget Variance
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'account_budget',
    ],

    'data': [
        'data/ir_cron_data.xml',
        'views/crossovered_budget_views.xml',
        'views/crossovered_budget_lines_views.xml',
    ],
}