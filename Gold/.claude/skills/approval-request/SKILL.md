# Skill: Approval Request Generator

## Description

Creates structured HITL (Human-in-the-Loop) approval request files for high-impact actions. This skill is the gateway for all outbound and destructive actions in the Gold tier — nothing goes out without manager sign-off.

## When to Use

Invoke `/approval-request` whenever ANY of these actions are about to execute:

| Trigger | Risk Level |
|---------|-----------|
| Send email to new contact | high |
| Send email (any `send_email` call) | medium |
| Post to LinkedIn | high |
| Post to Facebook | high |
| Post to Instagram | high |
| Post to Twitter/X (tweet or thread) | high |
| Delete email | high |
| Delete or move files outside vault | medium |
| Create Odoo invoice | critical |
| Post/confirm Odoo invoice | critical |
| Register Odoo payment | critical |
| Cancel Odoo invoice | critical |
| Create Odoo expense | high |
| Create/update Odoo partner | medium |
| Any action the AI is uncertain about | high |

**What does NOT require approval:**
- Creating email drafts (`draft_email`)
- Internal file moves (Inbox → Needs_Action → Done)
- Dashboard updates
- Log entries
- Reading emails or files
- Reading Odoo data (search, list, reports)
- Plan.md creation (the plan itself doesn't need approval; individual steps might)

## Input

The invoking skill or agent provides:

1. **action_type** — One of: `email_send`, `linkedin_post`, `meta_post`, `tweet`, `email_delete`, `file_delete`, `financial`
2. **description** — What the action will do (human-readable)
3. **proposed_content** — The full content that will be sent/posted/deleted
4. **context** — Why this action is being taken (e.g., "Follow-up to client inquiry from March 14")
5. **metadata** — Additional fields depending on action type:
   - Email: `to`, `subject`, `body`, `cc`, `bcc`, `thread_id`
   - LinkedIn: `post_content`, `hashtags`
   - Meta: `platform` (facebook|instagram), `post_content`, `hashtags`, `image_url`
   - Twitter: `tweet_content`, `thread_tweets` (if thread), `hashtags`
   - Delete: `target_path` or `message_id`
   - Financial: `operation` (create_invoice|register_payment|create_expense|update_partner), `partner`, `amount`, `line_items`

## Output

A YAML-frontmatter markdown file placed in `/Pending_Approval/`:

### File Naming
```
APPROVAL_<action_type>_<short-desc>_YYYY-MM-DD_HHMMSS.md
```

Examples:
- `APPROVAL_email_send_intro-to-partner_2026-03-17_090000.md`
- `APPROVAL_linkedin_post_q1-update_2026-03-17_140000.md`
- `APPROVAL_meta_post_fb-product-launch_2026-04-01_100000.md`
- `APPROVAL_tweet_industry-insight_2026-04-01_120000.md`
- `APPROVAL_financial_invoice-acme-corp_2026-04-01_140000.md`

### File Structure

```markdown
---
type: approval_request
action_type: <email_send|linkedin_post|meta_post|tweet|email_delete|file_delete|financial>
description: "<short description>"
risk_level: <low|medium|high|critical>
requested_at: <ISO timestamp>
expires_at: <ISO timestamp +48h>
status: pending_approval
proposed_action:
  # Fields vary by action_type — see metadata above
---

## Approval Request: <Description>

**Action:** <what will happen when approved>
**Risk Level:** <low|medium|high|critical>
**Requested:** <human-readable timestamp>
**Expires:** <human-readable timestamp +48h>

### Proposed Content

<full content that will be sent/posted>

### Context

<why this action is being taken — what triggered it, what it accomplishes>

### Risk Assessment

<brief assessment of what could go wrong>

### Instructions for Manager

- **To approve:** Move this file to `/Approved/`
- **To reject:** Move this file to `/Rejected/`
- **To modify:** Edit the proposed content above, then move to `/Approved/`
- **Expires:** This request will be flagged as stale after 48 hours
```

## Workflow

1. Receive action details from the invoking skill
2. Determine risk level using `references/approval-thresholds.md`
3. Generate the approval file with full content preview
4. Write the file to `/Pending_Approval/`
5. Log the approval request to `/Logs/`
6. Return the approval file path to the invoking skill
7. The invoking skill should then STOP and wait — do not proceed until the item appears in `/Approved/`

## Integration Points

- **Called by:** `/email-assistant`, `/linkedin-poster`, `/meta-poster`, `/twitter-poster`, `/odoo-finance`, `/plan-executor` (for approval-gated steps)
- **Monitored by:** `filesystem_watcher.py` (`ApprovedHandler`) and `orchestrator.py` (`_check_approved_items()`)
- **Dashboard:** Pending approvals count shown in `Dashboard.md`

## Important Rules

1. NEVER skip the approval step — even if the manager previously approved a similar action
2. NEVER auto-approve — the manager must physically move the file
3. Include the FULL proposed content in the approval file — no summaries or truncation
4. One approval per action — don't batch multiple actions into one approval file
5. If the action is part of a Plan.md, reference the plan file in the context
6. For financial actions, always include full amounts, partner names, and line item details
