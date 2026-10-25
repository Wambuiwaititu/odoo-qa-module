# Odoo QA Module: Purchase Approval Rule

A small **Odoo 17** custom module, `purchase_approval_rule`, plus automated **TransactionCase** tests. It's a portfolio example of testing business rules inside Odoo.

## What the module does
- Adds a **PO Approval Threshold** per company (Settings → Purchase).
- A purchase order whose untaxed amount (in company currency) is **above** the threshold can only be confirmed after a **Purchase Manager** approves it.
- Managers who confirm a PO themselves are recorded as the approver.
- Changing order lines after approval **resets** the approval.
- A threshold of 0 disables the rule.

## Tests (`purchase_approval_rule/tests/`)
| Test | Checks |
|---|---|
| below threshold | confirms normally |
| exactly at threshold | boundary: no approval needed |
| above threshold, normal user | `UserError`, PO stays draft |
| user self-approval | blocked |
| manager approves, user confirms | confirmed, approver recorded |
| manager confirms directly | approver = manager |
| edit lines after approval | approval reset |
| zero threshold | rule disabled |

## Run the tests
Requires an Odoo 17 source checkout and PostgreSQL.
```bash
# from the Odoo 17 source folder
./odoo-bin -d test_po_approval \
  --addons-path=addons,/path/to/odoo-qa-module \
  -i purchase_approval_rule \
  --test-tags /purchase_approval_rule \
  --stop-after-init --log-level=test
```

## Sample output
```
INFO test_po_approval odoo.modules.module: odoo.addons.purchase_approval_rule.tests.test_purchase_approval running
INFO test_po_approval odoo.tests.stats: purchase_approval_rule: 8 tests ...
INFO test_po_approval odoo.tests.result: 0 failed, 0 error(s) of 8 tests
```
(Illustrative. The output format follows Odoo 17's test runner.)

## Layout
```
purchase_approval_rule/
  __manifest__.py
  models/   res_company.py, res_config_settings.py, purchase_order.py
  views/    res_config_settings_views.xml
  tests/    test_purchase_approval.py
```
