import time
from pathlib import Path
from typing import Dict, Any, Literal, Optional

from replayci.runlog.events import Event
from replayci.runlog.recorder import Recorder
from replayci.scenario.loader import Scenario
from replayci.tools.executor import ToolExecutor

class ResearchAgentStub:
    def __init__(self, recorder: Recorder, scenario: Scenario, mode: Literal["record", "replay"], fixtures_dir: Optional[Path] = None):
        self.recorder = recorder
        self.scenario = scenario
        self.mode = mode
        # Initialize executor with fixtures_dir
        self.executor = ToolExecutor(recorder, mode, fixtures_dir=fixtures_dir)
        self.step_count = 0
        self.tool_calls_count = 0
        self.start_time = 0

    def run(self):
        self.start_time = time.time()
        self._log("run_start", {"scenario_id": self.scenario.id})

        # Step 1: Web Fetch
        url = "http://example.com/topic" 
        self._call_tool("web_fetch", {"url": url})

        # Step 2: Summarize
        self._call_tool("summarize", {"text": "dummy content from web_fetch"})

        # Step 3: Write Draft
        self._call_tool("write_draft", {"summary": "dummy summary"})

        latency_ms = int((time.time() - self.start_time) * 1000)
        self._log("run_end", {
            "tool_calls": self.tool_calls_count,
            "latency_ms": latency_ms
        })

    def _call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        # Validate tool is allowed
        allowed_names = [t.name for t in self.scenario.allowed_tools]
        if tool_name not in allowed_names:
            raise ValueError(f"Tool {tool_name} is not allowed in this scenario")

        self.step_count += 1
        # Executor handles tool_call and tool_result event emission
        result = self.executor.execute(tool_name, args, self.step_count)
        self.tool_calls_count += 1
        
        # Increment step for result event (already emitted by executor)
        self.step_count += 1
        
        return result

    def _log(self, type: str, payload: Dict[str, Any]):
        event = Event(
            run_id=self.recorder.run_id,
            step=self.step_count,
            type=type, # type: ignore
            payload=payload
        )
        self.recorder.log(event)
