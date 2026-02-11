# Nanodesk

个人定制版 nanobot，专为本地桌面端场景优化。

## 简介

Nanodesk 基于 [nanobot](https://github.com/HKUDS/nanobot) 构建，保留了原项目的轻量架构（~4,000 行代码），同时添加个人定制功能：

- 本地桌面工具集成（截图、文件管理...）
- 自定义频道适配
- 个人工作流技能

## 快速开始

```bash
# 安装
pip install -e .

# 启动（自动加载你的定制）
nanodesk agent

# 或查看帮助
nanodesk --help
```

## 项目结构

```
nanodesk/
├── __init__.py          # 模块标识
├── bootstrap.py         # 启动注入逻辑
├── launcher.py          # CLI 入口
├── channels/            # 你的自定义频道
├── tools/               # 你的自定义工具
├── skills/              # 你的自定义技能
├── providers/           # 你的 LLM 适配
├── patches/             # 必要时的核心补丁
├── scripts/             # 辅助脚本
└── docs/                # 文档
```

## 开发指南

### 添加自定义工具

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "描述你的工具"
    
    async def execute(self, **kwargs) -> str:
        return "执行结果"
```

然后在 `bootstrap.py` 中注册：

```python
from nanodesk.tools.my_tool import MyTool
from nanobot.agent.tools.registry import ToolRegistry

ToolRegistry.register(MyTool())
```

### 同步上游更新

```bash
# 拉取最新 nanobot 代码
./nanodesk/scripts/sync-upstream.sh
```

### 给原库提 PR

如果你在开发中发现可以贡献给原库的改进：

```bash
# 从 nanodesk 分支提取干净提交
./nanodesk/scripts/extract-contrib.sh <commit-hash>
```

然后到 GitHub 创建 PR 到 `HKUDS/nanobot`。

## 分支策略

| 分支 | 用途 |
|------|------|
| `main` | 跟踪上游，用于提 PR，不直接开发 |
| `nanodesk` | 主工作分支，包含你的所有定制 |

## 文档

- [架构设计](./docs/ARCHITECTURE.md) - 项目结构和 Git 工作流
- 更多文档...

## License

MIT License（继承自 nanobot）
