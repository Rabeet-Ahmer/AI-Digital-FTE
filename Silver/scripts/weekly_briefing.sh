#!/usr/bin/env bash
# weekly_briefing.sh — Weekly CEO briefing generation via Claude Code
#
# Cron schedule: 0 7 * * 1 (7:00 AM every Monday)
#
# What it does:
#   1. Invokes Claude Code with the /ceo-briefing skill
#   2. Generates a BRIEFING_weekly_YYYY-MM-DD.md in /Plans/
#   3. Reviews Done/, Logs/, Needs_Action/, Pending_Approval/ for the past week
#
# Prerequisites:
#   - Claude Code installed and in PATH
#   - WSL2: cron must be running (sudo service cron start)

set -euo pipefail

# Resolve paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$VAULT_DIR/Logs"
LOG_FILE="$LOG_DIR/cron_weekly.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

echo "========================================" >> "$LOG_FILE"
echo "Weekly Briefing — $(date -u +%Y-%m-%dT%H:%M:%S%z)" >> "$LOG_FILE"
echo "Vault: $VAULT_DIR" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

PROMPT="You are the AI Employee (Silver Tier). Generate the weekly CEO briefing using the /ceo-briefing skill.

Review the past 7 days of activity:
1. Read all files in /Done/ that were completed in the past 7 days
2. Read JSON logs from /Logs/ for the past 7 days
3. Check /Needs_Action/ for items still pending
4. Check /Pending_Approval/ for approvals awaiting decision
5. Check /Plans/ for active and completed plans
6. Check /Rejected/ for any rejected items

Generate a comprehensive BRIEFING_weekly_$(date +%Y-%m-%d).md file in /Plans/ with:
- Executive summary
- Key metrics
- Completed items list
- Pending items
- Highlights and recommendations
- Next week outlook

Respond with a summary of the briefing generated."

# Invoke Claude Code in non-interactive mode
if command -v claude &> /dev/null; then
    claude --print --prompt "$PROMPT" --cwd "$VAULT_DIR" >> "$LOG_FILE" 2>&1 || {
        echo "ERROR: Claude Code failed with exit code $?" >> "$LOG_FILE"
    }
else
    echo "WARNING: Claude Code not found in PATH. Skipping briefing." >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"
echo "Briefing generation completed at $(date -u +%Y-%m-%dT%H:%M:%S%z)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"
