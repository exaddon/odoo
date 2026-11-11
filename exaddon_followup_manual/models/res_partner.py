from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        # Same behaviour as on 17.0: no automatic payment reminders for new partners
        # unless someone switches them on explicitly.
        if ('followup_reminder_type' in fields_list
                and 'followup_reminder_type' in self._fields
                and 'default_followup_reminder_type' not in self.env.context):
            res['followup_reminder_type'] = 'manual'
        return res
