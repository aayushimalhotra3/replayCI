import json
import os
from pathlib import Path
from typing import TextIO

from replayci.runlog.events import Event

class Recorder:
    def __init__(self, run_id: str, runs_dir: Path):
        self.run_id = run_id
        self.runs_dir = runs_dir
        self.run_dir = runs_dir / run_id
        self.events_path = self.run_dir / "events.jsonl"
        self.fixtures_dir = self.run_dir / "fixtures"
        self._file: TextIO | None = None

    def start(self):
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.fixtures_dir.mkdir(exist_ok=True)
        self._file = open(self.events_path, "a", encoding="utf-8")

    def log(self, event: Event):
        if not self._file:
            raise RuntimeError("Recorder not started. Call start() first.")
        self._file.write(json.dumps(event.to_dict()) + "\n")
        self._file.flush()

    def close(self):
        if self._file:
            self._file.close()
            self._file = None
