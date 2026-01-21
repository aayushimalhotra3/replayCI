from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any
import yaml

from replayci.tools.registry import registry

@dataclass
class AllowedTool:
    name: str

@dataclass
class Assertions:
    max_tool_calls: int

@dataclass
class Scenario:
    id: str
    goal_prompt: str
    allowed_tools: List[AllowedTool]
    assertions: Assertions

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scenario':
        tools = [AllowedTool(name=t['name']) for t in data.get('allowed_tools', [])]
        assertions_data = data.get('assertions', {})
        assertions = Assertions(max_tool_calls=assertions_data.get('max_tool_calls', 10))
        
        return cls(
            id=data['id'],
            goal_prompt=data['goal_prompt'],
            allowed_tools=tools,
            assertions=assertions
        )

def load_scenario(path: Path) -> Scenario:
    if not path.exists():
        raise FileNotFoundError(f"Scenario file not found: {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    scenario = Scenario.from_dict(data)
    
    # Validate allowed tools exist in registry
    for tool in scenario.allowed_tools:
        if not registry.get(tool.name):
            raise ValueError(f"Scenario allows unknown tool: {tool.name}")
            
    return scenario
