# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'AISJ Theme',
    'description': 'AISJ Theme',
    'category': 'Theme/Schools',
    'summary': 'AISJ Theme',
    'sequence': 120,
    'version': '0.0',
    'depends': ['theme_common', 'website_animate'],
    'data': [
        'views/assets.xml',
        'views/image_content.xml',
        'views/image_library.xml',
        'views/snippets_options.xml',
        'views/snippets.xml',
        'views/custom_layout_templates.xml'
    ],
    'images': [
        'static/description/AISJ_description.jpg',
        'static/description/AISJ_screenshot.jpg',
    ],
    # 'application': False,
    # 'license': 'LGPL-3',
    # 'live_test_url': 'https://theme-clean.odoo.com/page/demo_page_home',
}
