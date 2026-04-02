# Skill: Odoo Financial Operations

## Description

Manages financial operations in Odoo ERP via MCP: creating invoices, recording payments, managing customers/vendors, and handling expenses. All write operations route through `/approval-request` at critical risk level.

## When to Use

Invoke `/odoo-finance` when:

- The manager says "create an invoice", "record a payment", "add a customer", "log an expense"
- A plan step requires a financial action
- Processing an inbox item that involves invoicing, billing, or payments

## Available Operations

### Customer/Vendor Management (`res.partner`)
| Operation | Approval Required? |
|-----------|-------------------|
| List/search partners | No |
| View partner details | No |
| Create new partner | Yes (medium) |
| Update partner info | Yes (medium) |

### Invoicing (`account.move`)
| Operation | Approval Required? |
|-----------|-------------------|
| List/search invoices | No |
| View invoice details | No |
| Create draft invoice | Yes (critical) |
| Confirm/post invoice | Yes (critical) |
| Cancel invoice | Yes (critical) |

### Payments (`account.payment`)
| Operation | Approval Required? |
|-----------|-------------------|
| List/search payments | No |
| View payment details | No |
| Register payment | Yes (critical) |

### Expenses (`hr.expense`)
| Operation | Approval Required? |
|-----------|-------------------|
| List/search expenses | No |
| View expense details | No |
| Create expense | Yes (high) |
| Submit expense report | Yes (high) |

## MCP Tools

This skill uses the Odoo MCP server (`mcp-odoo-adv`). Available operations:

- `search_read` — Search and read records from any model
- `create` — Create new records
- `write` — Update existing records
- `unlink` — Delete records (requires critical approval)

## Workflow: Create Invoice

1. **Gather info:** Customer name, line items (product, quantity, unit price), payment terms
2. **Search customer:** `search_read` on `res.partner` to find or confirm the customer
3. **Build invoice data:**
   ```json
   {
     "model": "account.move",
     "vals": {
       "move_type": "out_invoice",
       "partner_id": <customer_id>,
       "invoice_line_ids": [[0, 0, {"name": "Service", "quantity": 1, "price_unit": 1000.00}]]
     }
   }
   ```
4. **Route through `/approval-request`** with:
   - `action_type: financial`
   - `risk_level: critical`
   - Full invoice details in proposed content
5. **On approval:** Execute the MCP `create` call
6. **Log and update Dashboard**

## Workflow: Record Payment

1. **Identify invoice:** Search `account.move` for the invoice
2. **Build payment data:**
   ```json
   {
     "model": "account.payment",
     "vals": {
       "payment_type": "inbound",
       "partner_type": "customer",
       "partner_id": <customer_id>,
       "amount": 1000.00,
       "journal_id": <bank_journal_id>
     }
   }
   ```
3. **Route through `/approval-request`** at critical level
4. **On approval:** Execute the MCP `create` call
5. **Log and update Dashboard**

## Reference

See `references/odoo-models.md` for field definitions and model relationships.

## Important Rules

1. **All financial writes require approval.** No exceptions — invoices, payments, expenses.
2. **Read operations are free.** Searching, listing, and viewing don't need approval.
3. **Validate before submitting.** Check partner exists, amounts are correct, dates are valid.
4. **Log every operation.** Both reads and writes go to audit log.
5. **Never delete financial records.** Cancel or reverse instead.
6. **Currency awareness.** Always specify currency if the Odoo instance uses multi-currency.
