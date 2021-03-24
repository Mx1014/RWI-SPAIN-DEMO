# -*- coding: utf-8 -*-
{
    'name': 'Internal Ticketing',

    'summary': """ Internal Ticketing """,

    'description': """
        Internal Ticketing
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Helpdesk',
    'version': '1.0',

    'depends': [
        'web',
        'portal',
        'hr',
        'helpdesk',
    ],

    'data': [
        'views/internal_ticket_portal_templates.xml',
        'views/helpdesk_ticket_views.xml',
    ],
}