import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Literal

from replayci.runlog.events import Event
from replayci.runlog.recorder import Recorder
from replayci.tools.registry import registry
from replayci.tools.hashing import compute_args_hash

Mode = Literal["record", "replay"]

class ToolExecutor:
    def __init__(self, recorder: Recorder, mode: Mode, fixtures_dir: Optional[Path] = None):
        self.recorder = recorder
        self.mode = mode
        self.fixtures_dir = fixtures_dir

    def execute(self, tool_name: str, args: Dict[str, Any], step_count: int) -> Any:
        # 1. Emit tool_call event
        self._log_event(step_count, "tool_call", {"tool": tool_name, "args": args})

        # 2. Compute args hash for fixture path
        args_hash = compute_args_hash(args)
        
        # Path where we WOULD save it (in current run)
        current_fixture_path = self.recorder.fixtures_dir / tool_name / f"{args_hash}.json"

        result = None

        if self.mode == "replay":
            # REPLAY MODE: Load from fixtures_dir ONLY
            if not self.fixtures_dir:
                 raise RuntimeError("Replay mode requires fixtures_dir to be set.")
                 
            fixture_path = self.fixtures_dir / tool_name / f"{args_hash}.json"
            
            if not fixture_path.exists():
                raise RuntimeError(
                    f"Fixture not found for tool '{tool_name}' with args hash {args_hash}. "
                    f"Replay failed. Expected at: {fixture_path}\n"
                    f"Args: {args}"
                )
            
            with open(fixture_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                result = data["result"]
        
        else:
            # RECORD MODE: Execute real tool and save fixture
            tool_func = registry.get(tool_name)
            if not tool_func:
                raise ValueError(f"Tool {tool_name} not found in registry")
            
            result = tool_func(**args)
            
            # Save fixture
            current_fixture_path.parent.mkdir(parents=True, exist_ok=True)
            with open(current_fixture_path, "w", encoding="utf-8") as f:
                json.dump({
                    "tool": tool_name,
                    "args": args,
                    "result": result
                }, f, indent=2)

        # 3. Emit tool_result event
        self._log_event(step_count + 1, "tool_result", {"tool": tool_name, "result": result})
        
        return result

    def _log_event(self, step: int, type: str, payload: Dict[str, Any]):
        event = Event(
            run_id=self.recorder.run_id,
            step=step,
            type=type, # type: ignore
            payload=payload
        )
        self.recorder.log(event)
