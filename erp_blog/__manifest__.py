# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'ERP Blog and Recruitment',
    'author': 'ERP SWISS',
    'version': '1.0',
    'description': """ERP SWISS Recruitment and Blog""",
    'depends': ['website_blog', 'website_hr_recruitment'],
    'data': [
        'views/blog_styles.xml',
        'views/blog_post_view.xml',
        'views/recruitment_job.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'erp_blog/static/src/js/blog.js',
            'erp_blog/static/src/scss/blog.scss',
            'erp_blog/static/src/scss/job.scss',
        ]
    },
    'application': True,
    'installable': True,
}
