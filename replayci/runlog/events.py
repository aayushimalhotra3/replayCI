import time
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Literal, Optional

EventType = Literal["run_start", "tool_call", "tool_result", "agent_note", "run_end", "gate_result"]

@dataclass
class Event:
    run_id: str
    step: int
    type: EventType
    payload: Dict[str, Any]
    ts_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
