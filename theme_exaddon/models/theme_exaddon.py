from odoo import models


class ThemeExaddon(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_exaddon_post_copy(self, mod):
        self.enable_view('website.template_header_hamburger')
        print("self.enable========================",self.enable_view)
        self.enable_view('website.template_header_hamburger_align_right')
        print("self.enable========================",self.enable_view)
        self.enable_view('website.no_autohide_menu')
        print("self.enable========================", self.enable_view)
        self.enable_view('website.template_footer_contact')
