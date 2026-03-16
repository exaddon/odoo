import werkzeug
from werkzeug.utils import redirect

from odoo import http, tools
from odoo.http import request
from odoo.addons.website_blog.controllers.main import WebsiteBlog
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.controllers.main import QueryURL


class BlogInherit(WebsiteBlog):

    @http.route([
        '''/resources/<model("blog.blog"):blog>/<model("blog.post", "[('blog_id','=',blog.id)]"):blog_post>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def erp_blog_post(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        return super().blog_post(blog, blog_post, tag_id=None, page=1, enable_editor=None, **post)

    @http.route([
        '''/blog/<model("blog.blog"):blog>/<model("blog.post", "[('blog_id','=',blog.id)]"):blog_post>''',
    ], type='http', auth="public", website=True, sitemap=True)
    def old_blog_post_erp(self, blog, blog_post, tag_id=None, page=1, enable_editor=None, **post):
        new_url = f"/resources/{blog.slug}/{blog_post.slug}"
        return request.redirect(new_url, code=301)

    @http.route([
        '/blog/<path:subpath>',
        '/blog',
    ], type='http', auth='public', website=True)
    def blog_redirect(self, subpath=None, **kwargs):
        print('WORK THIS OR NOT3')
        print('WORK THIS OR NOT')
        print('WORK THIS OR NOT2')
        print('WORK THIS OR NOT1')
        if not subpath:
            return redirect('/resources', code=301)

        return redirect(f'/resources/{subpath}', code=301)

    @http.route([
        '/resources',
        '/resources/page/<int:page>',
        '/resources/tag/<string:tag>',
        '/resources/tag/<string:tag>/page/<int:page>',
        '/resources/<model("blog.blog"):blog>',
        '/resources/<model("blog.blog"):blog>/page/<int:page>',
        '/resources/<model("blog.blog"):blog>/tag/<string:tag>',
        '/resources/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>',
    ], type='http', auth="public", website=True, sitemap=True)
    def blog(self, blog=None, tag=None, page=1, search=None, **opt):
        Blog = request.env['blog.blog']
        blog = Blog.search([('website_id', '=', request.website.id)], limit=1, order='sequence')
        if not blog:
            blog = Blog.search([('website_id', '=', request.website.id)], limit=1, order='sequence')
            url = QueryURL('/resources/%s' % slug(blog), search=search, **opt)()
            return request.redirect(url, code=302)

        blogs = tools.lazy(lambda: Blog.search(request.website.website_domain(), order="sequence"))

        if not blog and len(blogs) == 1:
            url = QueryURL('/resources/%s' % slug(blogs[0]), search=search, **opt)()
            return request.redirect(url, code=302)

        date_begin, date_end = opt.get('date_begin'), opt.get('date_end')

        if tag and request.httprequest.method == 'GET':
            # redirect get tag-1,tag-2 -> get tag-1
            tags = tag.split(',')
            if len(tags) > 1:
                url = QueryURL('' if blog else '/resources', ['blog', 'tag'], blog=blog, tag=tags[0],
                               date_begin=date_begin,
                               date_end=date_end, search=search)()
                return request.redirect(url, code=302)

        values = self._prepare_blog_values(blogs=blogs, blog=blog, tags=tag, page=page, search=search, **opt)

        # in case of a redirection need by `_prepare_blog_values` we follow it
        if isinstance(values, werkzeug.wrappers.Response):
            return values

        if blog:
            values['main_object'] = blog
        values['blog_url'] = QueryURL('/resources', ['blog', 'tag'], blog=blog, tag=tag, date_begin=date_begin,
                                      date_end=date_end, search=search)

        return request.render("website_blog.blog_post_short", values)
