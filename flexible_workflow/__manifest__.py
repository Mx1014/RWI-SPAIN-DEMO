# -*- coding: utf-8 -*-
{
    'name': 'Flexible Workflow',

    'summary': """ Flexible Workflow """,

    'description': """
        Flexible Workflow
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Extra Tools',
    'version': '1.0',

    'depends': [
        'base',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/workflow_workflow_views.xml',
        'views/workflow_stage_views.xml',
        'views/workflow_attribute_views.xml',
    ],
}