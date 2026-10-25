from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    po_approval_threshold = fields.Monetary(
        string="PO Approval Threshold",
        currency_field="currency_id",
        default=5000.0,
        help="Purchase orders with an untaxed amount above this need manager approval.",
    )
