"""
Base Watcher - Template for all AI Employee watchers.
Provides the abstract interface that all watchers must implement.
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod


class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.inbox = self.vault_path / "Inbox"
        self.done = self.vault_path / "Done"
        self.logs = self.vault_path / "Logs"
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure required directories exist
        for folder in [self.needs_action, self.inbox, self.done, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """Return list of new items to process."""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder."""
        pass

    def run(self):
        self.logger.info(f"Starting {self.__class__.__name__}")
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    path = self.create_action_file(item)
                    self.logger.info(f"Created action file: {path}")
            except Exception as e:
                self.logger.error(f"Error: {e}")
            time.sleep(self.check_interval)
