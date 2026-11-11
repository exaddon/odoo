# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models


class ThemeUtils(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_exaddon_post_copy(self, mod):
        # Same header/footer setup as the 17.0 Exaddon theme
        self.enable_view('website.template_header_hamburger')
        self.enable_view('website.template_header_hamburger_align_right')
        self.enable_view('website.no_autohide_menu')
        self.enable_view('website.template_footer_contact')
