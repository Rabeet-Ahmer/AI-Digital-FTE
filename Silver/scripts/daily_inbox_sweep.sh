#!/usr/bin/env bash
# daily_inbox_sweep.sh — Daily inbox triage via Claude Code
#
# Cron schedule: 0 8 * * * (8:00 AM daily)
#
# What it does:
#   1. Triages unread Gmail messages
#   2. Processes files in /Inbox/
#   3. Handles pending items in /Needs_Action/
#   4. Checks approved items in /Approved/
#   5. Updates Dashboard.md
#
# Prerequisites:
#   - Claude Code installed and in PATH
#   - Gmail MCP configured
#   - WSL2: cron must be running (sudo service cron start)

set -euo pipefail

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$VAULT_DIR/Logs"
LOG_FILE="$LOG_DIR/cron_daily.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

echo "========================================" >> "$LOG_FILE"
echo "Daily Inbox Sweep — $(date -u +%Y-%m-%dT%H:%M:%S%z)" >> "$LOG_FILE"
echo "Vault: $VAULT_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

PROMPT="You are the AI Employee (Silver Tier). Perform the daily inbox sweep:

1. Check Gmail for unread messages using search_emails with query 'is:unread'. Triage any found emails using the inbox-triager agent — classify by priority and create action items for important ones.

2. Check /Inbox/ for any new files that haven't been triaged yet. Process them into /Needs_Action/.

3. Check /Needs_Action/ for pending items. Process each one by priority (critical > high > medium > low).

4. Check /Approved/ for any approved actions. Execute them.

5. Check /Pending_Approval/ for stale items (>48h). Flag them.

6. Update Dashboard.md with current counts.

7. Log all actions to /Logs/.

Respond with a summary of what was done."

# Invoke Claude Code in non-interactive mode
if command -v claude &> /dev/null; then
    claude --print --prompt "$PROMPT" --cwd "$VAULT_DIR" >> "$LOG_FILE" 2>&1 || {
        echo "ERROR: Claude Code failed with exit code $?" >> "$LOG_FILE"
    }
else
    echo "WARNING: Claude Code not found in PATH. Skipping sweep." >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "Sweep completed at $(date -u +%Y-%m-%dT%H:%M:%S%z)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
