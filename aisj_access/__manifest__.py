# -*- coding: utf-8 -*-
{
    'name': 'AISJ Access Rights',

    'summary': """ AISJ Access Rights """,

    'description': """
        AISJ Access Rights
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'account',
        'purchase',
        'hide_menu_by_group',
        'helpdesk',
    ],

    'data': [
        'data/res_groups_data.xml',
        'security/ir.model.access.csv',
        'security/account_move_security.xml',
        'security/purchase_order_security.xml',
        'security/purchase_order_line_security.xml',
        'views/portal_templates.xml',
    ],
}