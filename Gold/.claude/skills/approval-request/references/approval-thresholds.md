# Approval Thresholds

## Risk Level Classification

### Critical Risk
Actions that could cause financial loss, legal liability, or irreversible damage.

| Action | Trigger |
|--------|---------|
| Financial action | Invoice, payment, billing, subscription changes (Odoo) |
| Bulk email send | Sending to 5+ recipients at once |
| Data deletion | Removing files that contain business data |
| Odoo invoice create/post | Creating or confirming accounting entries |
| Odoo payment registration | Recording payments against invoices |

**Threshold:** Always requires approval. Flagged prominently in Dashboard. Manager notification via briefing.

### High Risk
Actions that represent the company externally or affect important relationships.

| Action | Trigger |
|--------|---------|
| Email to new contact | First email to an address not in sent history |
| LinkedIn post | Any public LinkedIn content |
| Facebook post | Any public Facebook Page content |
| Instagram post | Any public Instagram content |
| Twitter/X tweet or thread | Any public tweet |
| Email delete | Removing emails from inbox |
| Cold outreach | First contact with potential clients/partners |
| Odoo expense creation | Submitting expense records |

**Threshold:** Always requires approval. 48h expiry.

### Medium Risk
Routine outbound communications with established contacts.

| Action | Trigger |
|--------|---------|
| Email reply | Responding to an existing thread |
| Follow-up email | Re-engaging with a known contact |
| Meeting request | Scheduling with known contacts |
| File deletion | Removing vault files (non-data) |
| Odoo partner create/update | New customer/vendor records |

**Threshold:** Requires approval in Gold tier (all sends require approval). 48h expiry.

### Low Risk (No Approval Needed)
Internal operations that don't affect external parties.

| Action | Trigger |
|--------|---------|
| Create email draft | Drafts stay in Gmail drafts folder |
| File triage | Moving files between vault folders |
| Dashboard update | Refreshing status display |
| Log entry | Writing to audit log |
| Plan creation | Creating Plan.md files |
| Email read/search | Viewing email content |
| Odoo read operations | Searching, listing, reporting on Odoo data |

**Threshold:** No approval needed. Execute immediately.

## Escalation Rules

1. If uncertain about risk level, **escalate up** (treat medium as high, high as critical)
2. If an action combines multiple risk levels, use the **highest** risk level
3. If an action is part of a plan that was already discussed with the manager, still require approval for each outbound step — plans don't pre-approve actions
4. Time-sensitive actions (e.g., urgent reply needed) should note the urgency in the approval file but still require approval
5. Multi-platform posts (same content to LinkedIn + Facebook + Twitter) need **separate approval per platform**

## Stale Approval Handling

- Items pending for >24h: Include in next Dashboard update with "aging" note
- Items pending for >48h: Flag as STALE in Dashboard, include in next briefing
- Items pending for >7 days: Move to `/Rejected/` with auto-rejection note, log the expiry
