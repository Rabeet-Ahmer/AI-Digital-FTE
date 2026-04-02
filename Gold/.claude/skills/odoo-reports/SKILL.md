# Skill: Odoo Financial Reports

## Description

Generates read-only financial reports from Odoo ERP data. No write operations — purely informational. Used for dashboards, briefings, and manager queries about financial status.

## When to Use

Invoke `/odoo-reports` when:

- The manager asks "what invoices are outstanding?", "how much did we collect?", "expense summary"
- `/ceo-briefing` needs a Financial Summary section
- Dashboard update needs financial metrics
- Any financial reporting or analytics request

## Available Reports

### 1. Outstanding Invoices
Lists all unpaid customer invoices with aging.

**Query:** `account.move` where `move_type=out_invoice`, `state=posted`, `payment_state` in (`not_paid`, `partial`)

**Output:**
```markdown
## Outstanding Invoices

| Customer | Invoice # | Date | Due Date | Amount | Paid | Balance | Status |
|----------|-----------|------|----------|--------|------|---------|--------|

**Total Outstanding:** $X,XXX.XX
**Overdue (>30 days):** $X,XXX.XX
```

### 2. Payments Received
Lists payments received in a given period.

**Query:** `account.payment` where `payment_type=inbound`, `state=posted`, date range

**Output:**
```markdown
## Payments Received (<period>)

| Date | Customer | Amount | Reference |
|------|----------|--------|-----------|

**Total Received:** $X,XXX.XX
```

### 3. Expense Summary
Lists expenses by category and status.

**Query:** `hr.expense` with grouping by `product_id` (category)

**Output:**
```markdown
## Expense Summary (<period>)

| Category | Count | Total | Status |
|----------|-------|-------|--------|

**Total Expenses:** $X,XXX.XX
```

### 4. Accounts Receivable Aging
Groups outstanding invoices by age buckets.

**Output:**
```markdown
## AR Aging Report

| Bucket | Count | Amount |
|--------|-------|--------|
| Current (0-30 days) | X | $X,XXX |
| 31-60 days | X | $X,XXX |
| 61-90 days | X | $X,XXX |
| 90+ days | X | $X,XXX |

**Total AR:** $X,XXX.XX
```

### 5. Financial Summary (for CEO Briefing)
Compact summary for inclusion in weekly briefings.

**Output:**
```markdown
## Financial Summary

| Metric | Amount |
|--------|--------|
| Total Outstanding AR | $X,XXX |
| Overdue AR (>30 days) | $X,XXX |
| Payments Received (This Week) | $X,XXX |
| New Invoices Created (This Week) | X |
| Expenses Submitted (This Week) | $X,XXX |
```

## Integration Points

- **Called by:** `/ceo-briefing` (Financial Summary section), Dashboard rebuild
- **Uses:** Odoo MCP server (`search_read` operations only)
- **No approval needed** — all operations are read-only

## Important Rules

1. **Read-only.** This skill never creates, updates, or deletes records.
2. **Data-driven.** Report actual data — never fabricate or estimate.
3. **Format consistently.** Use tables, currency formatting, date formatting.
4. **Handle empty results.** If no data, say "No records found" — don't error.
5. **Respect privacy.** Don't include sensitive partner details beyond what's needed for the report.
