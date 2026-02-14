"""Nanodesk Bootstrap - Customization injection

Automatically loads customizations before nanobot starts.
"""

import os
import sys
from pathlib import Path

# Windows encoding fix: set UTF-8 encoding to avoid Unicode errors
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def inject():
    """Inject Nanodesk customization into nanobot.

    Registers custom tools, channels, and providers.
    """
    # Ensure project root is in path
    root = Path(__file__).parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Patch Windows encoding for compatibility
    _patch_windows_encoding()

    print("[INFO] Loading Nanodesk customization...")

    # Monkey patch AgentLoop to register custom tools
    _patch_agent_loop()

    print("[INFO] Nanodesk customization loaded")


def _patch_agent_loop():
    """Patch AgentLoop to register custom tools."""
    from nanobot.agent.loop import AgentLoop

    # Store original method
    original_register = AgentLoop._register_default_tools

    def _register_with_custom_tools(self):
        """Register default tools plus custom tools."""
        # Call original method
        original_register(self)

        # Register custom tools
        from nanodesk.tools.browser_search import BrowserFetchTool, BrowserSearchTool
        from nanodesk.tools.ddg_search import DuckDuckGoSearchTool

        self.tools.register(DuckDuckGoSearchTool())
        self.tools.register(BrowserSearchTool())
        self.tools.register(BrowserFetchTool())
        print("[INFO] Registered Nanodesk custom tools")

    # Replace method
    AgentLoop._register_default_tools = _register_with_custom_tools


def _patch_windows_encoding():
    """Patch Windows encoding to avoid UnicodeEncodeError."""
    if sys.platform != "win32":
        return

    import nanobot

    # Use ASCII fallback on Windows to avoid UnicodeEncodeError
    nanobot.__logo__ = "[nanobot]"
