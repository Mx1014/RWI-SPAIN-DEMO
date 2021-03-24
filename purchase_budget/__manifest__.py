# -*- coding: utf-8 -*-
{
    'name': 'Purchase Budget',

    'summary': """ Purchase Budget """,

    'description': """
        Purchase Budget
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Purchase',
    'version': '1.0',

    'depends': [
        'purchase',
        'account_budget',
    ],

    'data': [
        'views/crossovered_budget_views.xml',
        'views/purchase_order_views.xml',
        'views/res_users_views.xml',
    ],
}
