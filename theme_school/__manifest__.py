# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'School Theme',
    'description': 'School Theme',
    'category': 'Theme/Services',
    'summary': 'School',
    'sequence': 120,
    'version': '0.0',
    'depends': ['theme_common', 'website_animate'],
    'data': [
        'views/assets.xml',
        'views/image_content.xml',
        'views/image_library.xml',
        'views/snippets_options.xml',
        'views/snippets.xml',
    ],
    'images': [
        'static/description/Clean_description.jpg',
        'static/description/clean_screenshot.jpg',
    ],
    # 'application': False,
    # 'license': 'LGPL-3',
    # 'live_test_url': 'https://theme-clean.odoo.com/page/demo_page_home',
}
