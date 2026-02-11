# Nanodesk 架构设计

本文档说明 Nanodesk 的项目结构、Git 工作流和最佳实践。

## 项目定位

**Nanodesk** 是 [nanobot](https://github.com/HKUDS/nanobot) 的个人定制版本，目标是：

1. **功能定制**：添加适合本地桌面端的工具和功能
2. **双向贡献**：既能自由定制，又能回馈原库改进
3. **低维护成本**：方便同步上游更新，减少冲突

## 核心原则

### 1. 物理隔离

所有个人代码放在 `nanodesk/` 目录，与 `nanobot/` 完全分离：

```
Nanodesk/
├── nanobot/          # 📦 原库代码（尽量只读）
└── nanodesk/         # 🔥 你的定制（随心所欲）
```

### 2. 启动注入

通过 `bootstrap.py` 在运行时动态加载定制，**不修改原库文件**：

```python
# nanodesk/launcher.py
def main():
    from nanodesk import bootstrap
    bootstrap.inject()      # 注入你的工具、频道等
    
    from nanobot.cli.commands import app
    app()                   # 启动原库 CLI
```

### 3. 分支策略

| 分支 | 用途 | 规则 |
|-----|------|------|
| `main` | 跟踪上游 | `git merge upstream/main --ff-only`，不直接开发 |
| `nanodesk` | 主工作分支 | 日常开发，可修改任何文件 |

**工作流图示**：

```
upstream/main ─────┬────────────────────────
                   │
                   │  fetch/merge
                   ▼
origin/main ──────●────────●─────────●──────  # 干净，用于提 PR
                   \       /         /
                    \     / merge   /
                     \   /         /
                      \ /         /
origin/nanodesk ───────●─────────●──────────  # 你的工作分支
```

### 4. 最小侵入

- 根目录 `README.md` 只加顶部标识，其余保持原库内容
- 同步时快速解决冲突（`git checkout --ours README.md`）

## 目录结构详解

```
nanodesk/
├── __init__.py              # 模块标识
├── bootstrap.py             # 注入逻辑（核心）
├── launcher.py              # CLI 入口
├── README.md                # Nanodesk 文档
├── channels/                # 自定义频道
│   └── __init__.py          # 注册函数
├── tools/                   # 自定义工具
│   └── __init__.py          # 注册函数
├── skills/                  # 自定义技能（SKILL.md）
├── providers/               # LLM 适配
├── patches/                 # 必要时的补丁记录
│   └── README.md
├── scripts/                 # 辅助脚本
│   ├── sync-upstream.sh     # 同步上游
│   └── extract-contrib.sh   # 提取可贡献代码
└── docs/                    # 文档
    └── ARCHITECTURE.md      # 本文件
```

## 常见工作流程

### 日常开发

```bash
git checkout nanodesk

# 添加新工具
vim nanodesk/tools/screenshot.py

# 或修改原库代码（如果必须）
vim nanobot/agent/tools/web.py

git add .
git commit -m "feat: add screenshot tool"
git push origin nanodesk
```

### 同步上游更新

```bash
./nanodesk/scripts/sync-upstream.sh

# 或手动
git checkout main
git fetch upstream
git merge upstream/main --ff-only
git checkout nanodesk
git merge main
```

### 给原库提 PR

```bash
# 从 nanodesk 分支提取干净提交
./nanodesk/scripts/extract-contrib.sh <commit-hash>

# 然后到 GitHub 创建 PR
```

## 扩展开发指南

### 添加工具

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "工具描述"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        }
    
    async def execute(self, **kwargs) -> str:
        return "result"
```

在 `bootstrap.py` 注册：

```python
def inject():
    # ...
    from nanodesk.tools import register_tools
    register_tools()
```

### 添加频道

类似工具，继承 `BaseChannel`，在 `bootstrap.py` 注册。

## 注意事项

1. **不要频繁修改 `nanobot/` 目录**：尽量用 monkey patch 或扩展机制
2. **保持 `main` 分支干净**：只用于跟踪上游和提 PR
3. **有意义的提交**：可贡献的改动用清晰 commit message，方便 cherry-pick
4. **及时同步**：定期运行 `sync-upstream.sh`，减少冲突积累

## 相关文档

- [nanobot AGENTS.md](../AGENTS.md) - 原库开发指南
- [nanobot README.md](../README.md) - 原库说明
