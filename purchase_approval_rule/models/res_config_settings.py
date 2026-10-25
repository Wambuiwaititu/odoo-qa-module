from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    po_approval_threshold = fields.Monetary(
        related="company_id.po_approval_threshold",
        currency_field="company_currency_id",
        readonly=False,
    )
