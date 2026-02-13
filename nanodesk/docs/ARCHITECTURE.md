# Nanodesk 架构设计

本文档说明 Nanodesk 的项目结构、核心原则和最佳实践。

**Git 分支策略详见**：[BRANCHING.md](./BRANCHING.md)

---

## 项目定位

**Nanodesk** 是 [nanobot](https://github.com/HKUDS/nanobot) 的**实用个人助手**定制版本：

1. **实用优先**：功能够用且开箱即用，不为轻量牺牲实用（Practicality first）
2. **本地桌面优化**：添加适合本地桌面端的工具和功能
3. **双向贡献**：既能自由定制，又能回馈原库改进
4. **低维护成本**：方便同步上游更新，减少冲突

---

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

### 3. 最小侵入

- 根目录 `README.md` 只加顶部标识，其余保持原库内容
- 同步时快速解决冲突（`git checkout --ours README.md`）

---

## 目录结构

```
nanodesk/
├── __init__.py              # 模块标识
├── bootstrap.py             # 注入逻辑（核心）
├── launcher.py              # CLI 入口
├── desktop/                 # Windows 桌面应用
├── channels/                # 自定义频道
├── tools/                   # 自定义工具
├── skills/                  # 自定义技能（SKILL.md）
├── providers/               # LLM 适配
├── patches/                 # 必要时的补丁记录
├── scripts/                 # 辅助脚本
│   ├── build/              # 构建和打包脚本
│   ├── dev/                # 开发和测试脚本
│   ├── git/                # Git 工作流脚本
│   └── release/            # 发布脚本
└── docs/                    # 文档
```

---

## 快速开始

### 首次设置

```bash
# 1. 添加 upstream 远程仓库
git remote add upstream https://github.com/HKUDS/nanobot.git

# 2. 创建并切换到 develop 工作分支
git checkout -b develop

# 3. 推送分支到 origin
git push -u origin develop
```

### 开发新功能

```bash
# 从 develop 创建功能分支
git checkout develop
git checkout -b feature/my-feature

# 开发完成后合并回 develop
git checkout develop
git merge feature/my-feature
git push origin develop
```

---

## 扩展开发

### 添加工具

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    async def execute(self, **kwargs) -> str:
        return "result"
```

在 `bootstrap.py` 注册：

```python
def inject():
    from nanodesk.tools.my_tool import MyTool
    from nanobot.agent.tools.registry import ToolRegistry
    ToolRegistry.register(MyTool())
```

### 添加频道

类似工具，继承 `BaseChannel`，在 `bootstrap.py` 注册。

---

## Git 配置保护

`.gitattributes` 设置：

```gitattributes
README.md merge=ours
.gitignore merge=ours
.gitattributes merge=ours
```

同步时自动保留你的版本。

---

## 注意事项

1. **不要频繁修改 `nanobot/` 目录**：尽量用扩展机制
2. **保持 `main` 分支干净**：只用于跟踪上游
3. **及时同步**：定期运行 `sync-upstream.ps1`

---

## 相关文档

- [BRANCHING.md](./BRANCHING.md) - Git 分支管理
- [AI_COLLABORATION.md](./AI_COLLABORATION.md) - AI 协作指南
- [SYNC_WORKFLOW.md](./SYNC_WORKFLOW.md) - 上游同步流程
- [nanobot AGENTS.md](../AGENTS.md) - 原库开发指南
