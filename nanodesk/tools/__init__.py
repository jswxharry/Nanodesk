"""Nanodesk Tools - 自定义工具

添加你的个人工具。
"""


def get_custom_tools():
    """返回所有自定义工具实例
    
    在 bootstrap.py 中调用注册。
    """
    tools = []
    
    # TODO: 添加你的工具
    # from nanodesk.tools.screenshot import ScreenshotTool
    # tools.append(ScreenshotTool())
    
    return tools


def register_tools():
    """注册所有自定义工具"""
    from nanobot.agent.tools.registry import ToolRegistry
    
    for tool in get_custom_tools():
        ToolRegistry.register(tool)
