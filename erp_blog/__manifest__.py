# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ERP Blog',
    'author': 'ERP SWISS',
    'version': '1.0',
    'description': """Erpswiss""",
    'depends': ['website_blog'],
    'data': [
        'views/blog_styles.xml',
        'views/blog_post_view.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'erp_blog/static/src/js/blog.js',
            'erp_blog/static/src/scss/blog.scss',

        ]
    },
    'application': True,
    'installable': True,
}
