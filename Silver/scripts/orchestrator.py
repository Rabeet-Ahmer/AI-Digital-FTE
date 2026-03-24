"""
Orchestrator - Master process that coordinates the AI Employee.

Responsibilities:
1. Monitor /Needs_Action for pending items
2. Monitor /Approved for approved actions to execute
3. Monitor /Plans for active plans to drive forward
4. Trigger Claude Code to process items (via subprocess)
5. Update Dashboard.md with current state
6. Move completed items to /Done
7. Flag stale approvals (>48h)
8. Maintain audit logs

This is the Silver-tier orchestrator: it runs a processing loop
that scans folders, manages the approval pipeline, drives plans,
and invokes Claude Code when work is detected.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path


class SilverOrchestrator:
    def __init__(self, vault_path: str, poll_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / "Inbox"
        self.needs_action = self.vault_path / "Needs_Action"
        self.pending_approval = self.vault_path / "Pending_Approval"
        self.approved = self.vault_path / "Approved"
        self.rejected = self.vault_path / "Rejected"
        self.done = self.vault_path / "Done"
        self.plans = self.vault_path / "Plans"
        self.logs_dir = self.vault_path / "Logs"
        self.dashboard = self.vault_path / "Dashboard.md"
        self.signal_file = self.vault_path / ".new_work_signal"
        self.poll_interval = poll_interval
        self.logger = logging.getLogger("Orchestrator")

        # Ensure directories exist
        for folder in [
            self.inbox,
            self.needs_action,
            self.pending_approval,
            self.approved,
            self.rejected,
            self.done,
            self.plans,
            self.logs_dir,
        ]:
            folder.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main loop: poll for work, process approvals, drive plans, update dashboard."""
        self.logger.info(f"Silver Orchestrator started. Vault: {self.vault_path}")
        self.logger.info(f"Polling every {self.poll_interval}s. Press Ctrl+C to stop.\n")

        try:
            while True:
                # 1. Check approved items first (highest priority)
                self._check_approved_items()

                # 2. Check for stale approvals
                self._check_stale_approvals()

                # 3. Check active plans
                self._check_active_plans()

                # 4. Process pending Needs_Action items
                pending = self._get_pending_items()
                if pending:
                    self.logger.info(f"Found {len(pending)} pending item(s)")
                    for item in pending:
                        self._process_item(item)

                # 5. Update dashboard
                self._update_dashboard()
                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            self.logger.info("Orchestrator shutting down.")

    def _get_pending_items(self) -> list[Path]:
        """Get all .md files in Needs_Action that have status: pending."""
        items = []
        for f in sorted(self.needs_action.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            if "status: pending" in content:
                items.append(f)
        return items

    def _process_item(self, item_path: Path):
        """Process a single Needs_Action item by invoking Claude Code."""
        self.logger.info(f"Processing: {item_path.name}")
        content = item_path.read_text(encoding="utf-8")

        # Mark as in-progress
        updated = content.replace("status: pending", "status: in_progress")
        item_path.write_text(updated, encoding="utf-8")

        # Build the prompt for Claude Code
        prompt = (
            f"You are the AI Employee (Silver Tier). "
            f"Process this item from /Needs_Action/:\n\n"
            f"File: {item_path.name}\n"
            f"Content:\n{content}\n\n"
            f"Instructions:\n"
            f"1. Read the file metadata and content\n"
            f"2. Determine what action is needed\n"
            f"3. If the task requires 3+ steps, create a Plan.md via /plan-executor\n"
            f"4. If an outbound action is needed (email send, LinkedIn post, delete), "
            f"route through /approval-request\n"
            f"5. If simple, summarize what was done\n"
            f"6. Respond with a short summary of the action taken"
        )

        try:
            result = subprocess.run(
                ["claude", "--print", "--prompt", prompt],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.vault_path),
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                self.logger.info(f"Claude response: {response[:200]}")
                self._complete_item(item_path, response)
            else:
                self.logger.error(f"Claude error: {result.stderr[:200]}")
                self._mark_error(item_path, result.stderr)

        except FileNotFoundError:
            self.logger.warning(
                "Claude Code not found in PATH. "
                "Running in offline mode — marking item as reviewed."
            )
            self._complete_item(item_path, "Processed in offline mode (Claude not available)")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Claude timed out processing {item_path.name}")
            self._mark_error(item_path, "Processing timed out")

    def _check_approved_items(self):
        """Scan /Approved/ for items and dispatch their actions."""
        approved_files = sorted(self.approved.glob("*.md"))
        for item_path in approved_files:
            self.logger.info(f"Executing approved action: {item_path.name}")
            content = item_path.read_text(encoding="utf-8")

            # Extract action_type from frontmatter
            action_type = "unknown"
            for line in content.split("\n"):
                if line.startswith("action_type:"):
                    action_type = line.split(":", 1)[1].strip()
                    break

            # Build prompt for Claude to execute the approved action
            prompt = (
                f"You are the AI Employee (Silver Tier). "
                f"This action has been APPROVED by the manager. Execute it now.\n\n"
                f"Approved File: {item_path.name}\n"
                f"Action Type: {action_type}\n"
                f"Content:\n{content}\n\n"
                f"Instructions:\n"
                f"1. Read the approved action details\n"
                f"2. Execute the action (send email, post to LinkedIn, delete, etc.)\n"
                f"3. This is APPROVED — proceed with the action\n"
                f"4. Respond with confirmation of what was done"
            )

            try:
                result = subprocess.run(
                    ["claude", "--print", "--prompt", prompt],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.vault_path),
                )

                if result.returncode == 0:
                    response = result.stdout.strip()
                    self.logger.info(f"Approved action executed: {response[:200]}")
                    self._complete_approved_item(item_path, response)
                    self._log_action(
                        "approval_granted",
                        str(item_path),
                        str(self.done / item_path.name),
                        f"Executed approved {action_type}: {response[:100]}",
                        "success",
                    )
                else:
                    self.logger.error(f"Error executing approved action: {result.stderr[:200]}")
                    self._log_action(
                        "error",
                        str(item_path),
                        "",
                        f"Failed to execute approved {action_type}: {result.stderr[:100]}",
                        "failure",
                    )

            except FileNotFoundError:
                self.logger.warning("Claude Code not found. Cannot execute approved action.")
                self._complete_approved_item(
                    item_path, "Approved but not executed (Claude not available)"
                )
            except subprocess.TimeoutExpired:
                self.logger.error(f"Timeout executing approved action: {item_path.name}")

    def _complete_approved_item(self, item_path: Path, summary: str):
        """Move an executed approved item to /Done."""
        now = datetime.now(timezone.utc)
        content = item_path.read_text(encoding="utf-8")
        content = content.replace("status: pending_approval", "status: done")
        content += (
            f"\n\n## Execution\n"
            f"- **Executed:** {now.isoformat()}\n"
            f"- **Summary:** {summary}\n"
        )
        item_path.write_text(content, encoding="utf-8")

        dest = self.done / item_path.name
        item_path.rename(dest)
        self.logger.info(f"Approved item completed: {item_path.name}")

    def _check_stale_approvals(self):
        """Flag approval items that have been pending for >48h."""
        now = datetime.now(timezone.utc)
        stale_threshold = timedelta(hours=48)

        for item_path in self.pending_approval.glob("*.md"):
            content = item_path.read_text(encoding="utf-8")

            # Try to extract requested_at from frontmatter
            requested_at = None
            for line in content.split("\n"):
                if line.startswith("requested_at:"):
                    try:
                        ts_str = line.split(":", 1)[1].strip()
                        requested_at = datetime.fromisoformat(ts_str)
                    except (ValueError, IndexError):
                        pass
                    break

            if requested_at is None:
                # Fall back to file modification time
                mtime = item_path.stat().st_mtime
                requested_at = datetime.fromtimestamp(mtime, tz=timezone.utc)

            age = now - requested_at
            if age > stale_threshold and "STALE" not in content:
                self.logger.warning(f"Stale approval detected: {item_path.name} ({age.days}d {age.seconds // 3600}h old)")
                # Add stale marker to the file
                stale_note = (
                    f"\n\n> **STALE WARNING:** This approval request has been pending for "
                    f"{age.days}d {age.seconds // 3600}h. Please review and approve or reject.\n"
                )
                content += stale_note
                item_path.write_text(content, encoding="utf-8")

                self._log_action(
                    "approval_expired",
                    str(item_path),
                    "",
                    f"Approval stale after {age.days}d {age.seconds // 3600}h",
                    "pending_approval",
                )

    def _check_active_plans(self):
        """Find in-progress plans and drive the next step."""
        for plan_path in self.plans.glob("PLAN_*.md"):
            content = plan_path.read_text(encoding="utf-8")

            # Only process in_progress plans
            if "status: in_progress" not in content:
                continue

            # Skip plans blocked by approval
            if "blocked_by: approval_pending" in content:
                self.logger.info(f"Plan blocked by approval: {plan_path.name}")
                continue

            # Skip plans blocked by errors
            if "blocked_by: error" in content:
                self.logger.info(f"Plan blocked by error: {plan_path.name}")
                continue

            self.logger.info(f"Driving plan: {plan_path.name}")

            prompt = (
                f"You are the AI Employee (Silver Tier). "
                f"Continue executing this plan — complete the next unchecked step.\n\n"
                f"Plan File: {plan_path.name}\n"
                f"Content:\n{content}\n\n"
                f"Instructions:\n"
                f"1. Find the next unchecked step (- [ ])\n"
                f"2. Execute that step\n"
                f"3. If the step requires an outbound action, route through /approval-request "
                f"and update the plan's blocked_by field\n"
                f"4. Mark the step as done (- [x]) and update the frontmatter counters\n"
                f"5. Respond with what was done"
            )

            try:
                result = subprocess.run(
                    ["claude", "--print", "--prompt", prompt],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.vault_path),
                )

                if result.returncode == 0:
                    self.logger.info(f"Plan step completed: {result.stdout.strip()[:200]}")
                    self._log_action(
                        "plan_step",
                        str(plan_path),
                        "",
                        f"Executed plan step: {result.stdout.strip()[:100]}",
                        "success",
                    )
                else:
                    self.logger.error(f"Plan step error: {result.stderr[:200]}")

            except FileNotFoundError:
                self.logger.warning("Claude Code not found. Cannot drive plan.")
            except subprocess.TimeoutExpired:
                self.logger.error(f"Timeout driving plan: {plan_path.name}")

    def _complete_item(self, item_path: Path, summary: str):
        """Move a processed item to /Done and log it."""
        now = datetime.now(timezone.utc)

        content = item_path.read_text(encoding="utf-8")
        content = content.replace("status: in_progress", "status: done")
        content += f"\n\n## Completion\n- **Completed:** {now.isoformat()}\n- **Summary:** {summary}\n"
        item_path.write_text(content, encoding="utf-8")

        dest = self.done / item_path.name
        item_path.rename(dest)
        self.logger.info(f"Moved to Done: {item_path.name}")

        self._log_action("process", str(item_path), str(dest), summary, "success")

    def _mark_error(self, item_path: Path, error: str):
        """Mark an item as errored but leave in Needs_Action for retry."""
        content = item_path.read_text(encoding="utf-8")
        content = content.replace("status: in_progress", "status: error")
        content += f"\n\n## Error\n- **Time:** {datetime.now(timezone.utc).isoformat()}\n- **Error:** {error}\n"
        item_path.write_text(content, encoding="utf-8")
        self._log_action("error", str(item_path), "", error, "failure")

    def _update_dashboard(self):
        """Rewrite Dashboard.md with current vault state."""
        now = datetime.now(timezone.utc)

        inbox_count = len(list(self.inbox.glob("*")))
        pending_items = list(self.needs_action.glob("*.md"))
        pending_count = len(pending_items)
        done_count = len(list(self.done.glob("*.md")))
        approval_count = len(list(self.pending_approval.glob("*.md")))
        approved_count = len(list(self.approved.glob("*.md")))
        rejected_count = len(list(self.rejected.glob("*.md")))

        # Build the Needs Action table rows
        if pending_items:
            queue_rows = ""
            for i, item in enumerate(sorted(pending_items), 1):
                content = item.read_text(encoding="utf-8")
                priority = "medium"
                for line in content.split("\n"):
                    if line.startswith("priority:"):
                        priority = line.split(":")[1].strip()
                        break
                file_type = "file_drop"
                for line in content.split("\n"):
                    if line.startswith("type:"):
                        file_type = line.split(":")[1].strip()
                        break
                queue_rows += f"| {i} | {item.name} | {file_type} | {priority} | {item.stat().st_mtime:.0f} |\n"
        else:
            queue_rows = "| -- | No pending items | -- | -- | -- |\n"

        # Build the Pending Approvals table rows
        approval_items = list(self.pending_approval.glob("*.md"))
        if approval_items:
            approval_rows = ""
            for i, item in enumerate(sorted(approval_items), 1):
                content = item.read_text(encoding="utf-8")
                action_type = "unknown"
                risk_level = "medium"
                requested_at = ""
                for line in content.split("\n"):
                    if line.startswith("action_type:"):
                        action_type = line.split(":", 1)[1].strip()
                    elif line.startswith("risk_level:"):
                        risk_level = line.split(":", 1)[1].strip()
                    elif line.startswith("requested_at:"):
                        requested_at = line.split(":", 1)[1].strip()[:19]

                # Calculate age
                age_str = "unknown"
                try:
                    req_dt = datetime.fromisoformat(requested_at)
                    age = now - req_dt
                    if age.days > 0:
                        age_str = f"{age.days}d"
                    else:
                        age_str = f"{age.seconds // 3600}h"
                except (ValueError, TypeError):
                    pass

                is_stale = "STALE" in content
                stale_marker = " **STALE**" if is_stale else ""
                approval_rows += f"| {i} | {item.name} | {action_type} | {risk_level} | {requested_at} | {age_str}{stale_marker} |\n"
        else:
            approval_rows = "| -- | No pending approvals | -- | -- | -- | -- |\n"

        # Build Active Plans table
        plan_files = list(self.plans.glob("PLAN_*.md"))
        active_plans = []
        for pf in plan_files:
            content = pf.read_text(encoding="utf-8")
            if "status: in_progress" in content or "status: blocked" in content:
                active_plans.append(pf)

        if active_plans:
            plan_rows = ""
            for i, pf in enumerate(sorted(active_plans), 1):
                content = pf.read_text(encoding="utf-8")
                status = "unknown"
                steps_total = 0
                steps_completed = 0
                current_step = 0
                for line in content.split("\n"):
                    if line.startswith("status:"):
                        status = line.split(":", 1)[1].strip()
                    elif line.startswith("steps_total:"):
                        try:
                            steps_total = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith("steps_completed:"):
                        try:
                            steps_completed = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith("current_step:"):
                        try:
                            current_step = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                progress = f"{steps_completed}/{steps_total}"
                plan_rows += f"| {i} | {pf.name} | {status} | {progress} | Step {current_step} |\n"
        else:
            plan_rows = "| -- | No active plans | -- | -- | -- |\n"

        # Read recent log entries
        today = now.strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.json"
        recent_activity = ""
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text(encoding="utf-8"))
                for entry in entries[-5:]:
                    ts = entry.get("timestamp", "")[:19]
                    action = entry.get("action_type", "")
                    details = entry.get("details", "")[:50]
                    result = entry.get("result", "")
                    recent_activity += f"| {ts} | {action} | {details} | {result} |\n"
            except Exception:
                pass

        if not recent_activity:
            recent_activity = f"| {now.strftime('%Y-%m-%d')} | System running | Orchestrator active | OK |\n"

        dashboard_content = f"""---
last_updated: {now.isoformat()}
version: 0.2.0
tier: silver
---

# AI Employee Dashboard (Silver)

## System Status

| Component        | Status  | Last Check           |
| ---------------- | ------- | -------------------- |
| File Watcher     | Active  | {now.isoformat()} |
| Orchestrator     | Active  | {now.isoformat()} |
| Vault Connection | Active  | {now.isoformat()} |
| Approval Pipeline| Active  | {now.isoformat()} |
| LinkedIn Poster  | Standby | {now.isoformat()} |
| Cron Scheduler   | Active  | {now.isoformat()} |

## Inbox Summary

- **Inbox Items:** {inbox_count}
- **Needs Action:** {pending_count}
- **Pending Approval:** {approval_count}
- **Completed (Total):** {done_count}

## Pending Approvals

| # | File | Action Type | Risk Level | Requested | Age |
| - | ---- | ----------- | ---------- | --------- | --- |
{approval_rows}
## Needs Action Queue

| # | File | Type | Priority | Created |
| - | ---- | ---- | -------- | ------- |
{queue_rows}
## Active Plans

| # | Plan | Status | Progress | Current Step |
| - | ---- | ------ | -------- | ------------ |
{plan_rows}
## Scheduled Tasks

| Schedule | Task | Last Run | Next Run | Status |
| -------- | ---- | -------- | -------- | ------ |
| Daily 8:00 AM | Inbox Sweep | -- | -- | Configured |
| Monday 7:00 AM | CEO Briefing | -- | -- | Configured |

## LinkedIn Activity

| Date | Post Topic | Status | Engagement |
| ---- | ---------- | ------ | ---------- |
| -- | No posts yet | -- | -- |

## Recent Activity

| Timestamp | Action | Details | Status |
| --------- | ------ | ------- | ------ |
{recent_activity}
## Notes

- Silver tier: HITL approval workflow active
- All outbound actions (email send, LinkedIn post) require approval
- Drop files into `/Inbox/` for automatic processing
- Approval items appear in `/Pending_Approval/` — move to `/Approved/` or `/Rejected/`
- All actions are logged in `/Logs/`
"""

        self.dashboard.write_text(dashboard_content, encoding="utf-8")

    def _log_action(
        self,
        action_type: str,
        source: str,
        destination: str,
        details: str,
        result: str,
    ):
        """Append a JSON log entry to today's log file."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.json"

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "actor": "orchestrator",
            "source": source,
            "destination": destination,
            "details": details,
            "result": result,
        }

        entries = []
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, Exception):
                entries = []

        entries.append(entry)
        log_file.write_text(
            json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def main():
    vault_path = Path(__file__).resolve().parent.parent

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(vault_path / "Logs" / "orchestrator.log"),
        ],
    )

    orchestrator = SilverOrchestrator(str(vault_path), poll_interval=30)
    orchestrator.run()


if __name__ == "__main__":
    main()
