# -*- coding: utf-8 -*-
{
    'name': "Sincro Data",

    'summary': """ Tool for the importation from Odoo to API´s """,

    'description': """
        Common models for eduwebgroup school modules
    """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list

    'category': 'Admission',
    'version': '1.1',

    # any module necessary for this one to work correctly, esta acoplado debido a adm debido al wizard
    # se debe desacoplar extrayendo esta funcionalidad en un submodulo
    'depends': ['base', 'base_automation', 'adm', 'school_base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/sincro_data_api_views.xml',
        'views/sincro_data_group_type_ud_views.xml',
        'views/sincro_data_server_views.xml',
        'views/sincro_data_header_views.xml',
        'views/sincro_data_log_views.xml',
        'views/sincro_data_parameter_views.xml',
        'views/sincro_data_panel_configuration_views.xml',

        'views/config_views.xml',
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        # 'data/update_state_data.xml',
        # wizard
        # 'views/wizard/sincro_data_wizards.xml',
        'views/wizard/templates_custom.xml',

    ],
    'qweb': [
        'static/src/xml/kanban_view_button.xml'        ],
    'demo': []
}
