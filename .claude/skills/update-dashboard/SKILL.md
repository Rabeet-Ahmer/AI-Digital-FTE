---
name: update-dashboard
description: Update the Bronze Dashboard.md with current vault state — inbox counts, pending items, recent activity, and system status. Use when the user says "update dashboard", "refresh status", or after processing items.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(ls *), Bash(wc *)
---

Update `Bronze/Dashboard.md` with the current state of the vault.

## Steps

1. **Count Inbox items**: List files in `Bronze/Inbox/`
2. **Count Needs_Action items**: List `.md` files in `Bronze/Needs_Action/` and extract their priorities
3. **Count Done items**: List files in `Bronze/Done/`
4. **Read today's log**: Load `Bronze/Logs/YYYY-MM-DD.json` for recent activity
5. **Rebuild Dashboard.md** with the template below

## Dashboard Template

```markdown
---
last_updated: <current ISO timestamp>
version: 0.1.0
tier: bronze
---

# AI Employee Dashboard

## System Status

| Component        | Status  | Last Check           |
| ---------------- | ------- | -------------------- |
| File Watcher     | <status>| <timestamp>          |
| Orchestrator     | <status>| <timestamp>          |
| Vault Connection | Active  | <timestamp>          |

## Inbox Summary

- **Inbox Items:** <count>
- **Needs Action:** <count>
- **Completed (Total):** <count>

## Needs Action Queue

| # | File | Type | Priority | Created |
| - | ---- | ---- | -------- | ------- |
<rows from Needs_Action .md files>

## Recent Activity

| Timestamp | Action | Details | Status |
| --------- | ------ | ------- | ------ |
<last 10 entries from today's log>

## Notes

- Bronze tier: File system watcher active
- All actions are logged in `/Logs/`
- Drop files into `/Inbox/` for automatic processing
```

## Rules

- Always include an accurate `last_updated` timestamp
- If log file doesn't exist for today, show "No activity today"
- For system status, check if `Bronze/Logs/watcher.log` and `Bronze/Logs/orchestrator.log` were recently written to determine Active/Offline

$ARGUMENTS
