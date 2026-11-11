{
    'name': 'Exaddon: Manual Follow-up Reminders by Default',
    'summary': 'New partners get "Manual" follow-up reminders instead of "Automatic"',
    'description': """
Replaces the res.partner override that was hidden inside the 17.0 copy of
account_financial_report (field followup_reminder_type, default 'manual').
Existing partners keep their stored value; only the default for new partners is set.
""",
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'author': 'Exaddon AG',
    'depends': ['account_followup'],
    'data': [],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
