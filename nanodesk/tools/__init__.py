"""Nanodesk custom tools."""

from nanobot.agent.tools.registry import ToolRegistry
from nanodesk.tools.browser_search import BrowserFetchTool, BrowserSearchTool
from nanodesk.tools.ddg_search import DuckDuckGoSearchTool


def register_tools():
    """Register all custom tools."""
    registry = ToolRegistry()

    # DuckDuckGo search (no API key required)
    registry.register(DuckDuckGoSearchTool())
    print("[INFO] Registered DuckDuckGo search tool")

    # Browser-based search and fetch (Playwright)
    registry.register(BrowserSearchTool())
    registry.register(BrowserFetchTool())
    print("[INFO] Registered browser search tools")
