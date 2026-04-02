"""
File System Watcher - Monitors the /Inbox folder for new file drops.

When a file is dropped into /Inbox, this watcher:
1. Detects the new file via watchdog (polling-based for cross-platform support)
2. Creates a metadata .md file in /Needs_Action/ with frontmatter
3. Classifies priority based on filename keywords
4. Logs the triage action to /Logs/
5. Updates a signal file so the orchestrator knows to trigger Claude
"""

import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

# ── Sensitive file extensions that should never be processed ──
SENSITIVE_EXTENSIONS = {".env", ".key", ".pem", ".p12", ".pfx", ".credentials"}

# ── Keywords for priority classification ──
PRIORITY_KEYWORDS = {
    "critical": ["critical", "emergency", "outage"],
    "high": ["urgent", "asap", "important"],
    "medium": ["invoice", "report", "review", "todo"],
    "low": ["info", "fyi", "note", "readme"],
}


def classify_priority(filename: str) -> str:
    """Classify file priority based on filename keywords."""
    name_lower = filename.lower()
    for priority, keywords in PRIORITY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return priority
    return "medium"


def get_file_type(filepath: Path) -> str:
    """Determine a human-readable file type from extension."""
    ext_map = {
        ".md": "markdown",
        ".txt": "text",
        ".pdf": "pdf",
        ".csv": "spreadsheet",
        ".xlsx": "spreadsheet",
        ".json": "data",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image",
        ".py": "script",
        ".js": "script",
        ".html": "webpage",
        ".docx": "document",
    }
    return ext_map.get(filepath.suffix.lower(), "unknown")


class InboxHandler(FileSystemEventHandler):
    """Handles file creation events in the Inbox folder."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.logs_dir = self.vault_path / "Logs"
        self.logger = logging.getLogger("InboxHandler")
        self.processed_files: set[str] = set()

    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Skip hidden files and temp files
        if source.name.startswith(".") or source.name.startswith("~"):
            return

        # Deduplicate: skip if we already processed this exact file path
        if source.name in self.processed_files:
            return
        self.processed_files.add(source.name)

        # Skip sensitive files
        if source.suffix.lower() in SENSITIVE_EXTENSIONS:
            self.logger.warning(f"QUARANTINED sensitive file: {source.name}")
            self._log_action(
                action_type="quarantine",
                source=str(source),
                destination="blocked",
                details=f"Sensitive file type {source.suffix} blocked",
                result="blocked",
            )
            return

        self.logger.info(f"New file detected: {source.name}")

        try:
            self._create_action_file(source)
            self._write_signal()
        except Exception as e:
            self.logger.error(f"Failed to process {source.name}: {e}")
            self._log_action(
                action_type="error",
                source=str(source),
                destination="",
                details=str(e),
                result="failure",
            )

    def _create_action_file(self, source: Path):
        """Create a metadata markdown file in Needs_Action."""
        now = datetime.now(timezone.utc)
        priority = classify_priority(source.name)
        file_type = get_file_type(source)
        file_size = source.stat().st_size

        safe_name = source.stem.replace(" ", "_")
        action_filename = f"FILE_{safe_name}_{now.strftime('%Y-%m-%d_%H%M%S')}.md"
        action_path = self.needs_action / action_filename

        content = f"""---
type: file_drop
original_name: "{source.name}"
file_type: {file_type}
size_bytes: {file_size}
priority: {priority}
source_path: "{source}"
received: {now.isoformat()}
status: pending
---

## New File for Processing

**File:** {source.name}
**Type:** {file_type}
**Size:** {file_size:,} bytes
**Priority:** {priority}
**Received:** {now.strftime('%Y-%m-%d %H:%M:%S UTC')}

## Suggested Actions
- [ ] Review file content
- [ ] Categorize and file appropriately
- [ ] Move to /Done when processed
"""

        action_path.write_text(content, encoding="utf-8")
        self.logger.info(
            f"Created action file: {action_path.name} [priority={priority}]"
        )

        self._log_action(
            action_type="triage",
            source=str(source),
            destination=str(action_path),
            details=f"New {file_type} file triaged as {priority} priority",
            result="success",
        )

    def _write_signal(self):
        """Write a signal file so the orchestrator knows new work is available."""
        signal_path = self.vault_path / ".new_work_signal"
        signal_path.write_text(
            datetime.now(timezone.utc).isoformat(), encoding="utf-8"
        )

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
            "actor": "file_watcher",
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


class ApprovedHandler(FileSystemEventHandler):
    """Handles file creation events in the Approved folder."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.done = self.vault_path / "Done"
        self.logs_dir = self.vault_path / "Logs"
        self.scripts_dir = self.vault_path / "scripts"
        self.logger = logging.getLogger("ApprovedHandler")
        self.processed_files: set[str] = set()

    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)

        if source.name.startswith(".") or source.name.startswith("~"):
            return

        if not source.name.endswith(".md"):
            return

        if source.name in self.processed_files:
            return
        self.processed_files.add(source.name)

        self.logger.info(f"Approved item detected: {source.name}")

        try:
            content = source.read_text(encoding="utf-8")
            action_type = "unknown"
            for line in content.split("\n"):
                if line.startswith("action_type:"):
                    action_type = line.split(":", 1)[1].strip().strip("\"'")
                    break

            self.logger.info(f"Action type: {action_type}")
            self._dispatch(source, content, action_type)

        except Exception as e:
            self.logger.error(f"Failed to process approved item {source.name}: {e}")
            self._log_action("error", str(source), "", str(e), "failure")

    def _dispatch(self, source: Path, content: str, action_type: str):
        """Dispatch approved action based on action_type."""
        if action_type == "linkedin_post":
            self._handle_linkedin_post(source, content)
        else:
            # For other action types, write signal for orchestrator
            self.logger.info(f"Writing signal for orchestrator to handle: {action_type}")
            self._write_signal()
            self._log_action(
                "approved_dispatch",
                str(source),
                "",
                f"Approved {action_type} — signaled orchestrator",
                "pending",
            )

    def _handle_linkedin_post(self, source: Path, content: str):
        """Extract post content and run linkedin_poster.py."""
        # Extract post content from the "### Proposed Content" markdown section
        post_content = None
        in_proposed = False
        lines = []
        for line in content.split("\n"):
            if line.strip() == "### Proposed Content":
                in_proposed = True
                continue
            if in_proposed:
                if line.startswith("### "):
                    break
                lines.append(line)

        if lines:
            post_content = "\n".join(lines).strip()

        if not post_content:
            self.logger.error("Could not extract post content from approval file")
            self._log_action("error", str(source), "", "No post content found", "failure")
            return

        # Write content to temp file and invoke linkedin_poster.py
        tmp_file = self.scripts_dir / ".tmp_post_content.txt"
        tmp_file.write_text(post_content, encoding="utf-8")

        self.logger.info(f"Posting to LinkedIn ({len(post_content)} chars)...")

        try:
            import subprocess

            result = subprocess.run(
                ["uv", "run", "python", "linkedin_poster.py", "--content-file", str(tmp_file)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.scripts_dir),
            )

            if result.returncode == 0:
                self.logger.info(f"LinkedIn post result: {result.stdout.strip()[:200]}")
                self._complete_item(source, result.stdout.strip())
            else:
                self.logger.error(f"LinkedIn post failed: {result.stderr[:200]}")
                self._log_action("error", str(source), "", result.stderr[:200], "failure")

        except subprocess.TimeoutExpired:
            self.logger.error("LinkedIn posting timed out")
            self._log_action("error", str(source), "", "Posting timed out", "failure")
        finally:
            tmp_file.unlink(missing_ok=True)

    def _complete_item(self, source: Path, summary: str):
        """Move executed approval to /Done."""
        now = datetime.now(timezone.utc)
        content = source.read_text(encoding="utf-8")
        content = content.replace("status: pending_approval", "status: done")
        content += (
            f"\n\n## Execution\n"
            f"- **Executed:** {now.isoformat()}\n"
            f"- **Summary:** {summary[:200]}\n"
        )
        source.write_text(content, encoding="utf-8")

        dest = self.done / source.name
        source.rename(dest)
        self.logger.info(f"Moved to Done: {source.name}")

        self._log_action("approved_executed", str(source), str(dest), summary[:100], "success")

    def _write_signal(self):
        signal_path = self.vault_path / ".new_work_signal"
        signal_path.write_text(
            datetime.now(timezone.utc).isoformat(), encoding="utf-8"
        )

    def _log_action(self, action_type, source, destination, details, result):
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        log_file = self.logs_dir / f"{today}.json"
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_type": action_type,
            "actor": "approved_watcher",
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
    inbox_path = vault_path / "Inbox"
    approved_path = vault_path / "Approved"

    # Ensure directories exist
    for folder in ["Inbox", "Needs_Action", "Pending_Approval", "Approved", "Rejected", "Done", "Logs", "Plans"]:
        (vault_path / folder).mkdir(parents=True, exist_ok=True)

    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(vault_path / "Logs" / "watcher.log"),
        ],
    )
    logger = logging.getLogger("FileSystemWatcher")

    logger.info(f"Vault path: {vault_path}")
    logger.info(f"Watching: {inbox_path}")
    logger.info(f"Watching: {approved_path}")
    logger.info("Drop files into /Inbox/ to trigger processing.")
    logger.info("Move files to /Approved/ to execute approved actions.")
    logger.info("Press Ctrl+C to stop.\n")

    # PollingObserver works reliably across WSL, Windows, macOS, Linux
    inbox_handler = InboxHandler(str(vault_path))
    approved_handler = ApprovedHandler(str(vault_path))
    observer = PollingObserver(timeout=5)
    observer.schedule(inbox_handler, str(inbox_path), recursive=False)
    observer.schedule(approved_handler, str(approved_path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down file watcher...")
        observer.stop()

    observer.join()
    logger.info("File watcher stopped.")


if __name__ == "__main__":
    main()
