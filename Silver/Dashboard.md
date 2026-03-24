---
last_updated: 2026-03-24T19:06:00+00:00
version: 0.2.0
tier: silver
---

# AI Employee Dashboard (Silver)

## System Status

| Component        | Status  | Last Check           |
| ---------------- | ------- | -------------------- |
| File Watcher     | Active  | 2026-03-17T00:00:00+00:00 |
| Orchestrator     | Active  | 2026-03-17T00:00:00+00:00 |
| Vault Connection | Active  | 2026-03-17T00:00:00+00:00 |
| Approval Pipeline| Active  | 2026-03-17T00:00:00+00:00 |
| LinkedIn Poster  | Active  | 2026-03-24T19:06:00+00:00 |
| Cron Scheduler   | Active  | 2026-03-17T00:00:00+00:00 |

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

## LinkedIn Activity

| Date | Post Topic | Status | Engagement |
| ---- | ---------- | ------ | ---------- |
| 2026-03-24 | March 2026 AI News Roundup | Published | -- |

## Recent Activity

| Timestamp | Action | Details | Status |
| --------- | ------ | ------- | ------ |
| 2026-03-24 | linkedin_post | March 2026 AI News Roundup published | OK |
| 2026-03-24 | approval_granted | LinkedIn post approved by manager | OK |
| 2026-03-17 | system_init | Silver tier initialized | OK |

## Notes

- Silver tier: HITL approval workflow active
- All outbound actions (email send, LinkedIn post) require approval
- Drop files into `/Inbox/` for automatic processing
- Approval items appear in `/Pending_Approval/` — move to `/Approved/` or `/Rejected/`
- All actions are logged in `/Logs/`
