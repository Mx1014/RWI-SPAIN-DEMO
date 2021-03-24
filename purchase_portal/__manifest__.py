# -*- coding: utf-8 -*-
{
    'name': 'Purchase Portal',

    'summary': """ Purchase Portal """,

    'description': """
        Purchase Portal
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Purchase',
    'version': '1.0',

    'depends': [
        'portal',
        'purchase',
        'purchase_flexible_workflow',
        'purchase_budget',
    ],

    'data': [
        'views/assets.xml',
        'views/purchase_request_portal_templates.xml',
    ],
}
