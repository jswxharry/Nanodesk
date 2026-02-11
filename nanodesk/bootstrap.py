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
    
    print("🔧 Loading Nanodesk customization...")
    
    # TODO: 在这里注册你的扩展
    # 示例：
    # from nanodesk.tools import register_tools
    # from nanodesk.channels import register_channels
    # register_tools()
    # register_channels()
    
    print("✅ Nanodesk customization loaded")
