# -*- coding: utf-8 -*-
{
    'name': 'Purchasing Flexible Workflow',

    'summary': """ Purchasing Flexible Workflow """,

    'description': """
        Purchasing Flexible Workflow
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Purchase',
    'version': '1.0',

    'depends': [
        'flexible_workflow',
        'purchase',
    ],

    'data': [
        "data/workflow_workflow_data.xml",
        "views/purchase_order_views.xml",
    ],
}