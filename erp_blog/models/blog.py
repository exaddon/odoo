from odoo import fields, models


class Blog(models.Model):
    _inherit = 'blog.blog'

    style = fields.Selection([
        ('usual', 'Usual'),
        ('video', 'Video'),
        ('publication', 'Publication'),
        ('download', 'Download'),
    ], string='Style Type', default='usual')
    # 'sequence' is a standard field of blog.blog in Odoo 19 (same column, data kept)


class BlogPost(models.Model):
    _inherit = 'blog.post'

    style = fields.Selection(related='blog_id.style', string='Style Type', readonly=True)
    iframe = fields.Char(string='Video Iframe Code',
                         help="The iframe code to display the video in the blog post. Only used when the style is set to 'video'.")

    page_url = fields.Char(string='Extra URL')
    publication_date = fields.Date(string='Publication Date')
    download_attachment = fields.Many2one('ir.attachment', string='Download Attachment',
                                          domain="[('public', '=', True)]")

    erp_image = fields.Binary(string='Image', help="The image to display in the blog post. Only used when the style is set to 'publication' or 'download'.")