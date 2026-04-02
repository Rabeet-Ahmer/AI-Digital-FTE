# Odoo Model Reference

## res.partner (Customers & Vendors)

| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Partner name (required) |
| `email` | char | Email address |
| `phone` | char | Phone number |
| `street` | char | Street address |
| `city` | char | City |
| `state_id` | many2one | State/Province → `res.country.state` |
| `country_id` | many2one | Country → `res.country` |
| `zip` | char | ZIP/Postal code |
| `vat` | char | Tax ID / VAT number |
| `customer_rank` | integer | >0 = is a customer |
| `supplier_rank` | integer | >0 = is a vendor |
| `company_type` | selection | `person` or `company` |
| `property_payment_term_id` | many2one | Default payment terms → `account.payment.term` |

## account.move (Invoices, Bills, Journal Entries)

| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Invoice number (auto-generated) |
| `move_type` | selection | `out_invoice` (customer), `in_invoice` (vendor), `out_refund`, `in_refund`, `entry` |
| `partner_id` | many2one | Customer/Vendor → `res.partner` |
| `invoice_date` | date | Invoice date |
| `invoice_date_due` | date | Due date |
| `state` | selection | `draft`, `posted`, `cancel` |
| `amount_total` | monetary | Total amount (read-only, computed) |
| `amount_residual` | monetary | Amount due / unpaid (read-only) |
| `currency_id` | many2one | Currency → `res.currency` |
| `invoice_line_ids` | one2many | Line items → `account.move.line` |
| `payment_state` | selection | `not_paid`, `in_payment`, `paid`, `partial`, `reversed` |

### Invoice Line Fields (`account.move.line`)

| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Description |
| `product_id` | many2one | Product → `product.product` (optional) |
| `quantity` | float | Quantity |
| `price_unit` | float | Unit price |
| `tax_ids` | many2many | Taxes → `account.tax` |
| `price_subtotal` | monetary | Subtotal (computed) |

## account.payment

| Field | Type | Description |
|-------|------|-------------|
| `payment_type` | selection | `inbound` (receive) or `outbound` (send) |
| `partner_type` | selection | `customer` or `supplier` |
| `partner_id` | many2one | Partner → `res.partner` |
| `amount` | monetary | Payment amount |
| `currency_id` | many2one | Currency → `res.currency` |
| `journal_id` | many2one | Bank/Cash journal → `account.journal` |
| `date` | date | Payment date |
| `ref` | char | Reference / memo |
| `state` | selection | `draft`, `posted`, `cancel` |

## hr.expense

| Field | Type | Description |
|-------|------|-------------|
| `name` | char | Expense description (required) |
| `employee_id` | many2one | Employee → `hr.employee` |
| `product_id` | many2one | Expense category → `product.product` |
| `total_amount` | monetary | Total amount |
| `date` | date | Expense date |
| `reference` | char | Bill reference |
| `state` | selection | `draft`, `reported`, `approved`, `done`, `refused` |

## Common Queries

### Find all unpaid invoices
```python
search_read("account.move", [["move_type", "=", "out_invoice"], ["payment_state", "!=", "paid"], ["state", "=", "posted"]])
```

### Find customer by name
```python
search_read("res.partner", [["name", "ilike", "Company Name"], ["customer_rank", ">", 0]])
```

### Get total outstanding receivables
```python
search_read("account.move", [["move_type", "=", "out_invoice"], ["state", "=", "posted"], ["payment_state", "in", ["not_paid", "partial"]]], fields=["partner_id", "amount_residual"])
```

### Get payments received this month
```python
search_read("account.payment", [["payment_type", "=", "inbound"], ["state", "=", "posted"], ["date", ">=", "2026-04-01"]])
```
