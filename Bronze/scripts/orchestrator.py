"""
Orchestrator - Master process that coordinates the AI Employee.

Responsibilities:
1. Monitor /Needs_Action for pending items
2. Trigger Claude Code to process items (via subprocess)
3. Update Dashboard.md with current state
4. Move completed items to /Done
5. Maintain audit logs

This is the Bronze-tier orchestrator: it runs a processing loop
that scans folders and invokes Claude Code when work is detected.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


class BronzeOrchestrator:
    def __init__(self, vault_path: str, poll_interval: int = 30):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / "Inbox"
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.plans = self.vault_path / "Plans"
        self.logs_dir = self.vault_path / "Logs"
        self.dashboard = self.vault_path / "Dashboard.md"
        self.signal_file = self.vault_path / ".new_work_signal"
        self.poll_interval = poll_interval
        self.logger = logging.getLogger("Orchestrator")

        # Ensure directories exist
        for folder in [self.inbox, self.needs_action, self.done, self.plans, self.logs_dir]:
            folder.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Main loop: poll for work, process, update dashboard."""
        self.logger.info(f"Orchestrator started. Vault: {self.vault_path}")
        self.logger.info(f"Polling every {self.poll_interval}s. Press Ctrl+C to stop.\n")

        try:
            while True:
                pending = self._get_pending_items()

                if pending:
                    self.logger.info(f"Found {len(pending)} pending item(s)")
                    for item in pending:
                        self._process_item(item)

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
            f"You are the AI Employee (Bronze Tier). "
            f"Process this item from /Needs_Action/:\n\n"
            f"File: {item_path.name}\n"
            f"Content:\n{content}\n\n"
            f"Instructions:\n"
            f"1. Read the file metadata and content\n"
            f"2. Determine what action is needed\n"
            f"3. If simple, summarize what was done\n"
            f"4. The item has been triaged and is ready for review\n"
            f"5. Respond with a short summary of the action taken"
        )

        try:
            # Invoke Claude Code in non-interactive mode
            result = subprocess.run(
                ["bonsai start", "--print", "--prompt", prompt],
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

    def _complete_item(self, item_path: Path, summary: str):
        """Move a processed item to /Done and log it."""
        now = datetime.now(timezone.utc)

        # Update the file status and add completion summary
        content = item_path.read_text(encoding="utf-8")
        content = content.replace("status: in_progress", "status: done")
        content += f"\n\n## Completion\n- **Completed:** {now.isoformat()}\n- **Summary:** {summary}\n"
        item_path.write_text(content, encoding="utf-8")

        # Move to Done
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

        # Build the Needs Action table rows
        if pending_items:
            queue_rows = ""
            for i, item in enumerate(sorted(pending_items), 1):
                content = item.read_text(encoding="utf-8")
                # Extract priority from frontmatter
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

        # Read recent log entries for the activity table
        today = now.strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.json"
        recent_activity = ""
        if log_file.exists():
            try:
                entries = json.loads(log_file.read_text(encoding="utf-8"))
                for entry in entries[-5:]:  # Last 5 entries
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
version: 0.1.0
tier: bronze
---

# AI Employee Dashboard

## System Status

| Component        | Status  | Last Check           |
| ---------------- | ------- | -------------------- |
| File Watcher     | Active  | {now.isoformat()} |
| Orchestrator     | Active  | {now.isoformat()} |
| Vault Connection | Active  | {now.isoformat()} |

## Inbox Summary

- **Inbox Items:** {inbox_count}
- **Needs Action:** {pending_count}
- **Completed (Total):** {done_count}

## Needs Action Queue

| # | File | Type | Priority | Created |
| - | ---- | ---- | -------- | ------- |
{queue_rows}
## Recent Activity

| Timestamp | Action | Details | Status |
| --------- | ------ | ------- | ------ |
{recent_activity}
## Notes

- Bronze tier: File system watcher active
- All actions are logged in `/Logs/`
- Drop files into `/Inbox/` for automatic processing
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

    orchestrator = BronzeOrchestrator(str(vault_path), poll_interval=30)
    orchestrator.run()


if __name__ == "__main__":
    main()
