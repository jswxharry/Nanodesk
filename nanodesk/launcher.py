"""Nanodesk Launcher - 启动入口

加载定制后启动 nanobot CLI。
"""


def main():
    """主入口函数"""
    # 1. 先注入 Nanodesk 定制
    from nanodesk import bootstrap
    bootstrap.inject()
    
    # 2. 启动 nanobot CLI
    from nanobot.cli.commands import app
    app()


if __name__ == "__main__":
    main()
