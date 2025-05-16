from odoo import models,fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    followup_reminder_type = fields.Selection([('automatic', 'Automatic'), ('manual', 'Manual')], string="Reminders", default='manual')