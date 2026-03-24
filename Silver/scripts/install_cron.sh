#!/usr/bin/env bash
# install_cron.sh — Install cron jobs for Silver-tier AI Employee
#
# Installs:
#   - Daily inbox sweep at 8:00 AM
#   - Weekly CEO briefing at 7:00 AM Monday
#
# WSL2 Notes:
#   - Cron doesn't start automatically in WSL2. After every Windows reboot:
#       sudo service cron start
#   - Alternative: Use Windows Task Scheduler to call WSL commands
#     (see bottom of this script for instructions)
#
# Usage:
#   chmod +x install_cron.sh
#   ./install_cron.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DAILY_SCRIPT="$SCRIPT_DIR/daily_inbox_sweep.sh"
WEEKLY_SCRIPT="$SCRIPT_DIR/weekly_briefing.sh"

echo "Silver-tier AI Employee — Cron Job Installer"
echo "============================================="
echo ""

# Ensure scripts are executable
chmod +x "$DAILY_SCRIPT"
chmod +x "$WEEKLY_SCRIPT"
echo "Made scripts executable."

# Define cron entries
DAILY_CRON="0 8 * * * $DAILY_SCRIPT"
WEEKLY_CRON="0 7 * * 1 $WEEKLY_SCRIPT"

# Check if entries already exist
EXISTING_CRON=$(crontab -l 2>/dev/null || true)

CHANGES_MADE=false

if echo "$EXISTING_CRON" | grep -qF "$DAILY_SCRIPT"; then
    echo "Daily inbox sweep cron already installed. Skipping."
else
    echo "Installing daily inbox sweep (8:00 AM daily)..."
    EXISTING_CRON="$EXISTING_CRON
$DAILY_CRON"
    CHANGES_MADE=true
fi

if echo "$EXISTING_CRON" | grep -qF "$WEEKLY_SCRIPT"; then
    echo "Weekly briefing cron already installed. Skipping."
else
    echo "Installing weekly briefing (7:00 AM Monday)..."
    EXISTING_CRON="$EXISTING_CRON
$WEEKLY_CRON"
    CHANGES_MADE=true
fi

if [ "$CHANGES_MADE" = true ]; then
    # Clean up blank lines and install
    echo "$EXISTING_CRON" | sed '/^$/d' | crontab -
    echo ""
    echo "Cron jobs installed successfully!"
else
    echo ""
    echo "No changes needed — all cron jobs already installed."
fi

echo ""
echo "Current crontab:"
echo "----------------"
crontab -l 2>/dev/null || echo "(empty)"

echo ""
echo "============================================="
echo "IMPORTANT: WSL2 Cron Setup"
echo "============================================="
echo ""
echo "Cron doesn't auto-start in WSL2. After every Windows reboot, run:"
echo "  sudo service cron start"
echo ""
echo "To auto-start cron, add to /etc/wsl.conf:"
echo "  [boot]"
echo "  command = service cron start"
echo ""
echo "============================================="
echo "Alternative: Windows Task Scheduler"
echo "============================================="
echo ""
echo "If you prefer Windows Task Scheduler over WSL cron:"
echo ""
echo "1. Open Task Scheduler (taskschd.msc)"
echo "2. Create Basic Task:"
echo "   - Name: 'AI Employee - Daily Inbox Sweep'"
echo "   - Trigger: Daily at 8:00 AM"
echo "   - Action: Start a program"
echo "   - Program: wsl.exe"
echo "   - Arguments: -d Ubuntu -- bash -lc '$DAILY_SCRIPT'"
echo ""
echo "3. Create Basic Task:"
echo "   - Name: 'AI Employee - Weekly Briefing'"
echo "   - Trigger: Weekly, Monday at 7:00 AM"
echo "   - Action: Start a program"
echo "   - Program: wsl.exe"
echo "   - Arguments: -d Ubuntu -- bash -lc '$WEEKLY_SCRIPT'"
echo ""
echo "Note: Replace 'Ubuntu' with your WSL distro name if different."
echo "Check with: wsl -l -v"
