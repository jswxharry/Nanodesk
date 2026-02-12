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
│   ├── sync-upstream.sh/.ps1    # 同步上游（Bash/PowerShell）
│   ├── extract-contrib.sh/.ps1  # 提取可贡献代码（Bash/PowerShell）
│   └── init-venv.ps1            # 初始化虚拟环境（Windows）
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

## 默认分支

**默认分支是 `nanodesk`**（而非 `main`）。

这样设计的原因：
- 新用户 clone 下来直接获得可用的定制版
- 避免误在 `main` 分支开发
- 符合"个人定制版"的定位

**例外**：给原库提 PR 时，需要从 `main` 分支创建。

## 首次设置

如果是新克隆的仓库，先添加 upstream：

```bash
# 1. 添加 upstream 远程仓库
git remote add upstream https://github.com/HKUDS/nanobot.git

# 2. 验证
git remote -v
# 应显示 origin（你的 fork）和 upstream（原库）

# 3. 创建并切换到 nanodesk 工作分支
git checkout -b nanodesk

# 4. 推送分支到 origin
git push -u origin nanodesk
```

## Git 配置保护

为了防止同步上游时覆盖你的配置，我们在 `.gitattributes` 中设置了：

```gitattributes
README.md merge=ours
.gitignore merge=ours
.gitattributes merge=ours
```

这意味着同步时如果这些文件有冲突，Git 会自动保留 **你的版本**。

### .gitignore 特殊处理

原库有 `docs/` 会忽略所有 docs 目录，我们改为 `/docs/` 只忽略根目录：

```gitignore
/docs/          # 只忽略根目录的 docs/
```

这样 `nanodesk/docs/` 可以正常提交。

**注意**：如果 upstream 有重要的 .gitignore 更新（安全相关），需要手动审查：
```bash
git diff upstream/main -- .gitignore
# 手动合并需要的规则
```

## 脚本使用详解

### sync-upstream.sh

完整流程：
```bash
./nanodesk/scripts/sync-upstream.sh
```

脚本会自动：
1. 更新 `main` 分支到最新 upstream
2. 合并到 `nanodesk` 分支
3. 自动解决 `README.md` 冲突（保留我们的）

如果还有其他冲突：
```bash
# 手动解决
git status                    # 看哪些文件冲突
# 编辑冲突文件...
git add .
git commit -m "sync: resolve conflicts"
git push origin nanodesk
```

### extract-contrib.sh

从 `nanodesk` 提取干净提交：
```bash
./nanodesk/scripts/extract-contrib.sh <commit-hash>
```

示例：
```bash
# 1. 找到可贡献的 commit
git log nanodesk --not main --oneline
# e.g. a1b2c3d fix: handle timeout

# 2. 提取
./nanodesk/scripts/extract-contrib.sh a1b2c3d

# 3. 脚本会创建 contrib/xxx 分支，然后你去 GitHub 提 PR
```

## 注意事项

1. **不要频繁修改 `nanobot/` 目录**：尽量用 monkey patch 或扩展机制
2. **保持 `main` 分支干净**：只用于跟踪上游和提 PR
3. **有意义的提交**：可贡献的改动用清晰 commit message，方便 cherry-pick
4. **及时同步**：定期运行 `sync-upstream.sh`，减少冲突积累
5. **检查 .gitignore 变更**：upstream 更新后检查是否有新的忽略规则需要同步

## 相关文档

- [AI_COLLABORATION.md](./AI_COLLABORATION.md) - AI 协作指南
- [CODE_LOCATION.md](./CODE_LOCATION.md) - 代码归属判断
- [COMMIT_RULES.md](./COMMIT_RULES.md) - 提交信息规范
- [nanobot AGENTS.md](../AGENTS.md) - 原库开发指南
- [nanobot README.md](../README.md) - 原库说明
