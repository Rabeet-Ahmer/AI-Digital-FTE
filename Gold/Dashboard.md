---
last_updated: 2026-04-01T00:00:00+00:00
version: 0.3.0
tier: gold
---

# AI Employee Dashboard (Gold)

## System Status

| Component          | Status  | Last Check           |
| ------------------ | ------- | -------------------- |
| File Watcher       | Active  | 2026-04-01T00:00:00+00:00 |
| Orchestrator       | Active  | 2026-04-01T00:00:00+00:00 |
| Vault Connection   | Active  | 2026-04-01T00:00:00+00:00 |
| Approval Pipeline  | Active  | 2026-04-01T00:00:00+00:00 |
| LinkedIn Poster    | Standby | 2026-04-01T00:00:00+00:00 |
| Meta (FB/IG) API   | Standby | 2026-04-01T00:00:00+00:00 |
| Twitter/X API      | Standby | 2026-04-01T00:00:00+00:00 |
| Odoo ERP (MCP)     | Standby | 2026-04-01T00:00:00+00:00 |
| Cron Scheduler     | Active  | 2026-04-01T00:00:00+00:00 |

## Inbox Summary

- **Inbox Items:** 0
- **Needs Action:** 0
- **Pending Approval:** 0
- **Completed (Total):** 0

## Pending Approvals

| # | File | Action Type | Risk Level | Requested | Age |
| - | ---- | ----------- | ---------- | --------- | --- |
| -- | No pending approvals | -- | -- | -- | -- |

## Needs Action Queue

| # | File | Type | Priority | Created |
| - | ---- | ---- | -------- | ------- |
| -- | No pending items | -- | -- | -- |

## Active Plans

| # | Plan | Status | Progress | Current Step |
| - | ---- | ------ | -------- | ------------ |
| -- | No active plans | -- | -- | -- |

## Scheduled Tasks

| Schedule | Task | Last Run | Next Run | Status |
| -------- | ---- | -------- | -------- | ------ |
| Daily 8:00 AM | Inbox Sweep | -- | -- | Configured |
| Monday 7:00 AM | CEO Briefing | -- | -- | Configured |
| Weekly | Meta Token Expiry Check | -- | -- | Configured |
| Daily | Twitter Rate Limit Track | -- | -- | Configured |
| Friday 6:00 PM | Odoo Financial Summary | -- | -- | Configured |

## Social Media Activity

| Date | Platform | Post Topic | Status | Engagement |
| ---- | -------- | ---------- | ------ | ---------- |
| -- | No posts yet | -- | -- | -- |

## Financial Summary (Odoo)

| Metric | Value |
| ------ | ----- |
| Outstanding AR | -- |
| Payments This Week | -- |
| New Invoices | -- |
| Pending Expenses | -- |

*Connect Odoo ERP to populate. Run `scripts/docker/odoo-setup.sh` to start.*

## API Rate Limits

| Service | Limit | Used | Remaining | Resets |
| ------- | ----- | ---- | --------- | ------ |
| Twitter/X | 1,500/month | -- | -- | -- |
| Meta Graph API | 200/hour | -- | -- | -- |

## Recent Activity

| Timestamp | Action | Details | Status |
| --------- | ------ | ------- | ------ |
| 2026-04-01 | system_init | Gold tier initialized | OK |

## Notes

- Gold tier: HITL approval workflow active for all outbound actions
- Supported platforms: Email, LinkedIn, Facebook, Instagram, Twitter/X
- Odoo ERP: Financial operations via MCP (all writes require critical approval)
- Drop files into `/Inbox/` for automatic processing
- Approval items appear in `/Pending_Approval/` — move to `/Approved/` or `/Rejected/`
- All actions are logged in `/Logs/`
