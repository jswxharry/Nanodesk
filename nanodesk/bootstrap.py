"""Nanodesk Bootstrap - Customization injection

Automatically loads customizations before nanobot starts.
Includes power management for Gateway mode on Windows.
"""

import os
import socket
import sys
from pathlib import Path

# Windows encoding fix: set UTF-8 encoding to avoid Unicode errors
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _is_gateway_mode() -> bool:
    """Check if running in Gateway mode"""
    return "gateway" in sys.argv


GATEWAY_LOCK_PORT = 28790  # Port for single instance lock


def _ensure_single_gateway():
    """Use socket port lock to ensure single instance"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", GATEWAY_LOCK_PORT))
        sock.listen(1)
        return sock  # Keep reference, auto-released on process exit
    except OSError:
        # Port already in use - another Gateway is running
        print("Gateway already running")
        sys.exit(1)


# Global lock reference to prevent garbage collection
_gateway_lock = None


def inject():
    """Inject Nanodesk customization into nanobot.

    Registers custom tools, channels, and providers.
    """
    global _gateway_lock
    
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

    # Gateway mode: single instance lock + power management
    if _is_gateway_mode():
        # 1. Ensure single instance (prevent multiple instances)
        _gateway_lock = _ensure_single_gateway()

        # 2. Start power management (Windows only)
        if sys.platform == "win32":
            from nanodesk.desktop.core.power_manager import (
                prevent_sleep,
                start_power_monitor,
            )

            prevent_sleep()
            start_power_monitor()


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
