#!/usr/bin/env bash
# install_cron.sh — Install cron jobs for Gold-tier AI Employee
#
# Installs:
#   - Daily inbox sweep at 8:00 AM
#   - Weekly CEO briefing at 7:00 AM Monday
#   - Weekly Meta token expiry check (Sunday 9 PM)
#   - Daily Twitter rate limit tracking (11:55 PM)
#   - Weekly Odoo financial summary (Friday 6:00 PM)
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
META_CHECK_SCRIPT="$SCRIPT_DIR/meta_token_check.sh"
TWITTER_RATE_SCRIPT="$SCRIPT_DIR/twitter_rate_check.sh"
ODOO_SUMMARY_SCRIPT="$SCRIPT_DIR/odoo_weekly_summary.sh"

echo "Gold-tier AI Employee — Cron Job Installer"
echo "============================================="
echo ""

# Create stub scripts if they don't exist
for script in "$META_CHECK_SCRIPT" "$TWITTER_RATE_SCRIPT" "$ODOO_SUMMARY_SCRIPT"; do
    if [ ! -f "$script" ]; then
        cat > "$script" << 'STUBEOF'
#!/usr/bin/env bash
# Auto-generated stub — replace with actual implementation
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VAULT_DIR="$(dirname "$SCRIPT_DIR")"
echo "$(date -u +%Y-%m-%dT%H:%M:%S) - Running $(basename "$0")" >> "$VAULT_DIR/Logs/watcher.log"
STUBEOF
    fi
done

# Ensure scripts are executable
for script in "$DAILY_SCRIPT" "$WEEKLY_SCRIPT" "$META_CHECK_SCRIPT" "$TWITTER_RATE_SCRIPT" "$ODOO_SUMMARY_SCRIPT"; do
    if [ -f "$script" ]; then
        chmod +x "$script"
    fi
done
echo "Made scripts executable."

# Define cron entries
DAILY_CRON="0 8 * * * $DAILY_SCRIPT"
WEEKLY_CRON="0 7 * * 1 $WEEKLY_SCRIPT"
META_CRON="0 21 * * 0 $META_CHECK_SCRIPT"
TWITTER_CRON="55 23 * * * $TWITTER_RATE_SCRIPT"
ODOO_CRON="0 18 * * 5 $ODOO_SUMMARY_SCRIPT"

# Check if entries already exist
EXISTING_CRON=$(crontab -l 2>/dev/null || true)

CHANGES_MADE=false

install_cron_entry() {
    local script_path="$1"
    local cron_entry="$2"
    local description="$3"

    if echo "$EXISTING_CRON" | grep -qF "$script_path"; then
        echo "  $description — already installed. Skipping."
    else
        echo "  Installing: $description"
        EXISTING_CRON="$EXISTING_CRON
$cron_entry"
        CHANGES_MADE=true
    fi
}

install_cron_entry "$DAILY_SCRIPT" "$DAILY_CRON" "Daily inbox sweep (8:00 AM daily)"
install_cron_entry "$WEEKLY_SCRIPT" "$WEEKLY_CRON" "Weekly briefing (7:00 AM Monday)"
install_cron_entry "$META_CHECK_SCRIPT" "$META_CRON" "Meta token expiry check (9 PM Sunday)"
install_cron_entry "$TWITTER_RATE_SCRIPT" "$TWITTER_CRON" "Twitter rate limit tracking (11:55 PM daily)"
install_cron_entry "$ODOO_SUMMARY_SCRIPT" "$ODOO_CRON" "Odoo financial summary (6 PM Friday)"

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
echo "   - Name: 'AI Employee Gold - Daily Inbox Sweep'"
echo "   - Trigger: Daily at 8:00 AM"
echo "   - Action: Start a program"
echo "   - Program: wsl.exe"
echo "   - Arguments: -d Ubuntu -- bash -lc '$DAILY_SCRIPT'"
echo ""
echo "3. Create additional tasks for weekly briefing, Meta check,"
echo "   Twitter tracking, and Odoo summary using similar pattern."
echo ""
echo "Note: Replace 'Ubuntu' with your WSL distro name if different."
echo "Check with: wsl -l -v"
