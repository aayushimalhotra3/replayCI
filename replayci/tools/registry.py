from typing import Any, Callable, Dict, Optional

ToolFunc = Callable[..., Any]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolFunc] = {}

    def register(self, name: str, func: ToolFunc):
        self._tools[name] = func

    def get(self, name: str) -> Optional[ToolFunc]:
        return self._tools.get(name)

    def record_fixture(self, tool_name: str, args: Dict[str, Any], result: Any):
        # Placeholder for future fixture recording
        pass

# Global registry instance
registry = ToolRegistry()

# --- Fake Tools ---

def web_fetch(url: str) -> str:
    return f"Content from {url}\nSome fake content about the topic."

def summarize(text: str) -> str:
    return "Summary: This is a fake summary of the content."

def write_draft(summary: str) -> str:
    return """
Draft Report:
- Point 1: Key insight from research [1]
- Point 2: Another important fact [2]
- Point 3: Conclusion based on data

References:
[1] http://example.com/source1
[2] http://example.com/source2
    """.strip()

# Register default tools
registry.register("web_fetch", web_fetch)
registry.register("summarize", summarize)
registry.register("write_draft", write_draft)
