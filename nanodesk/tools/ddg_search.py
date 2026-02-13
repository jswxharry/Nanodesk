"""DuckDuckGo search tool for Nanodesk.

无需 API Key 的网络搜索，作为 Brave Search 的免费替代方案。
"""

from typing import Any

from nanobot.agent.tools.base import Tool


class DuckDuckGoSearchTool(Tool):
    """Search the web using DuckDuckGo (no API key required)."""
    
    name = "ddg_search"
    description = "Search the web using DuckDuckGo. No API key required. Returns titles, URLs, and snippets."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "count": {"type": "integer", "description": "Results (1-10)", "minimum": 1, "maximum": 10}
        },
        "required": ["query"]
    }
    
    def __init__(self, max_results: int = 5):
        self.max_results = max_results
    
    async def execute(self, query: str, count: int | None = None, **kwargs: Any) -> str:
        try:
            # Try to import duckduckgo-search
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                return (
                    "Error: duckduckgo-search not installed.\n"
                    "Install with: pip install duckduckgo-search"
                )
            
            n = min(max(count or self.max_results, 1), 10)
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=n))
            
            if not results:
                return f"No results for: {query}"
            
            lines = [f"Results for: {query}\n"]
            for i, item in enumerate(results, 1):
                lines.append(f"{i}. {item.get('title', '')}\n   {item.get('href', '')}")
                if desc := item.get("body"):
                    lines.append(f"   {desc}")
            return "\n".join(lines)
            
        except Exception as e:
            return f"Error: {e}"
