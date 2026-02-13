"""Nanodesk custom tools."""

from nanobot.agent.tools.registry import ToolRegistry
from nanodesk.tools.ddg_search import DuckDuckGoSearchTool
from nanodesk.tools.browser_search import BrowserSearchTool, BrowserFetchTool


def register_tools():
    """Register all custom tools."""
    # DuckDuckGo search (no API key required)
    ToolRegistry.register(DuckDuckGoSearchTool())
    print("[INFO] Registered DuckDuckGo search tool")
    
    # Browser-based search and fetch (Playwright)
    ToolRegistry.register(BrowserSearchTool())
    ToolRegistry.register(BrowserFetchTool())
    print("[INFO] Registered browser search tools")
