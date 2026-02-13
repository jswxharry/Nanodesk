"""Nanodesk custom tools."""

from nanobot.agent.tools.registry import ToolRegistry
from nanodesk.tools.ddg_search import DuckDuckGoSearchTool


def register_tools():
    """Register all custom tools."""
    # DuckDuckGo search (no API key required)
    ToolRegistry.register(DuckDuckGoSearchTool())
    print("[INFO] Registered DuckDuckGo search tool")
