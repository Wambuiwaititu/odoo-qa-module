from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    needs_approval = fields.Boolean(compute="_compute_needs_approval")
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)

    @api.depends("amount_untaxed", "company_id.po_approval_threshold")
    def _compute_needs_approval(self):
        for order in self:
            threshold = order.company_id.po_approval_threshold
            amount = order.currency_id._convert(
                order.amount_untaxed, order.company_id.currency_id, order.company_id,
                order.date_order or fields.Date.today(),
            )
            order.needs_approval = bool(threshold) and amount > threshold

    def _is_purchase_manager(self):
        return self.env.user.has_group("purchase.group_purchase_manager")

    def button_confirm(self):
        for order in self:
            if order.needs_approval and not order.approved_by_id:
                if not order._is_purchase_manager():
                    raise UserError(_(
                        "Purchase order %s is above the approval threshold and must be "
                        "approved by a Purchase Manager.", order.name))
                order.approved_by_id = self.env.user
        return super().button_confirm()

    def action_approve(self):
        if not self._is_purchase_manager():
            raise UserError(_("Only Purchase Managers can approve purchase orders."))
        self.write({"approved_by_id": self.env.user.id})

    def write(self, vals):
        # Changing lines after approval resets the approval.
        if "order_line" in vals:
            vals = dict(vals, approved_by_id=False)
        return super().write(vals)
