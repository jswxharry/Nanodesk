"""Nanodesk Bootstrap - 启动时注入定制

在 nanobot 启动前自动加载你的定制扩展。
"""

import sys
from pathlib import Path


def inject():
    """注入 Nanodesk 定制到 nanobot

    注册你的工具、频道、技能等扩展。
    """
    # 确保项目根目录在路径中
    root = Path(__file__).parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

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
