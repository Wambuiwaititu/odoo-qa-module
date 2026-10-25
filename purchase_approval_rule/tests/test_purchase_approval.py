from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestPurchaseApproval(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.company.po_approval_threshold = 1000.0
        cls.vendor = cls.env["res.partner"].create({"name": "Test Vendor"})
        cls.product = cls.env["product.product"].create({
            "name": "Office Chair", "type": "consu", "standard_price": 100.0})
        base = [cls.env.ref("base.group_user").id]
        cls.user = cls.env["res.users"].create({
            "name": "PO User", "login": "po_user",
            "groups_id": [(6, 0, base + [cls.env.ref("purchase.group_purchase_user").id])]})
        cls.manager = cls.env["res.users"].create({
            "name": "PO Manager", "login": "po_manager",
            "groups_id": [(6, 0, base + [cls.env.ref("purchase.group_purchase_manager").id])]})

    def _make_po(self, qty, price=100.0, user=None):
        env = self.env(user=user or self.user)
        return env["purchase.order"].create({
            "partner_id": self.vendor.id,
            "order_line": [(0, 0, {"product_id": self.product.id, "product_qty": qty,
                                   "price_unit": price})],
        })

    def test_below_threshold_confirms_without_approval(self):
        po = self._make_po(qty=5)  # 500
        self.assertFalse(po.needs_approval)
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

    def test_exactly_at_threshold_does_not_need_approval(self):
        po = self._make_po(qty=10)  # 1000, boundary
        self.assertFalse(po.needs_approval)

    def test_above_threshold_blocks_normal_user(self):
        po = self._make_po(qty=11)  # 1100
        self.assertTrue(po.needs_approval)
        with self.assertRaises(UserError):
            po.button_confirm()
        self.assertEqual(po.state, "draft")

    def test_user_cannot_self_approve(self):
        po = self._make_po(qty=20)
        with self.assertRaises(UserError):
            po.action_approve()

    def test_manager_approval_lets_user_confirm(self):
        po = self._make_po(qty=20)
        po.with_user(self.manager).action_approve()
        self.assertEqual(po.approved_by_id, self.manager)
        po.button_confirm()
        self.assertEqual(po.state, "purchase")

    def test_manager_confirm_records_approver(self):
        po = self._make_po(qty=20, user=self.manager)
        po.button_confirm()
        self.assertEqual(po.approved_by_id, self.manager)

    def test_editing_lines_resets_approval(self):
        po = self._make_po(qty=20)
        po.with_user(self.manager).action_approve()
        po.write({"order_line": [(1, po.order_line.id, {"product_qty": 30})]})
        self.assertFalse(po.approved_by_id)

    def test_zero_threshold_disables_rule(self):
        self.company.po_approval_threshold = 0.0
        po = self._make_po(qty=100)
        self.assertFalse(po.needs_approval)
