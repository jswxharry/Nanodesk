# Nanodesk AI 协作指南（必读）

> 本文档是所有 AI 编码助手的必读配置。
> 关键信息直接写在此文件，详细规范指向具体文件。

---

## ⚠️ 绝对禁止（红线）

**Git 操作**：
- ❌ 自动 `git commit` 而不告知用户
- ❌ 自动 `git push` 到远端
- ❌ 批量提交未审核的改动

**正确流程**：展示改动 → 用户确认 → 执行

---

## 🎯 核心编码规范（写代码时立即遵守）

### 1. 代码注释必须用英文
```python
# ✅ Fetch user list from database
# ❌ 获取用户列表

class MyTool:
    """Screenshot tool for Windows."""  # ✅
    """Windows桌面截图工具"""  # ❌
```
例外：`TODO:` / `FIXME:` 标记开头

### 2. Python 3.11+ 语法
```python
# ✅ str | None, list[str]
def process(text: str | None) -> list[str]: ...

# ❌ Optional[str], List[str]
```

### 3. 命名规范
- 类：`PascalCase`
- 函数/变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`

### 4. 路径处理
```python
# ✅ Pathlib
from pathlib import Path
config = Path.home() / ".nanobot" / "config.json"

# ❌ 字符串拼接路径
```

### 5. 异步模式
- I/O 操作必须 `async`
- 使用 `httpx` 而非 `requests`

### 6. 简洁高效原则
**避免过度设计，节约上下文开销**。

```python
# ✅ 简洁直接
def get_user(user_id: str) -> User | None:
    """Fetch user by ID."""
    return db.query(User).filter_by(id=user_id).first()

# ❌ 过度设计
class UserRepositoryFactory:
    def __init__(self, config_provider):
        self._config = config_provider.get_config()
    ...
```

**决策原则**：
- 除非性能差别很大，或有其他重要因素，否则优先简单方案
- 能用简单方案，不用复杂架构
- 函数短小精悍，避免层层嵌套
- 一行能说清的事，不写两行
- 优先读取现有代码风格，保持一致

---

## 📁 代码位置决策

| 场景 | 放在哪里 |
|------|---------|
| Windows 特定功能 | `nanodesk/` |
| 跨平台通用功能 | `nanobot/`（可贡献给上游）|
| 个人定制工具 | `nanodesk/` |
| VS Code 配置 | `.vscode/` |

**决策原则**：这段代码对其他 nanobot 用户有用吗？有用 → `nanobot/`，否则 → `nanodesk/`

---

## 📚 详细规范（必须阅读）

**编码规范**：
- `AGENTS.md` - 原项目编码规范（命名、类型注解、异步等）
- `nanodesk/docs/LANGUAGE_POLICY.md` - 语言策略（代码注释英文）

**协作规范**：
- `nanodesk/docs/AI_COLLABORATION.md` - Git 工作流、提交规范
- `nanodesk/docs/CODE_LOCATION.md` - 代码归属详细判断
- `nanodesk/docs/COMMIT_RULES.md` - 提交信息前缀规范

**项目架构**：
- `nanodesk/docs/ARCHITECTURE.md` - 分支策略、目录结构
- `nanodesk/docs/SYNC_WORKFLOW.md` - 上游同步流程

**AI 必须读取**：在进行任何代码修改前，阅读 `LANGUAGE_POLICY.md` 和 `CODE_LOCATION.md`。

---

## 🚀 快速命令

```powershell
# 运行
nanodesk agent          # 交互式聊天
nanodesk gateway        # 启动网关（接收飞书等消息）

# 同步上游
.\nanodesk\scripts\sync-upstream.ps1

# 检查状态
git branch -v
nanodesk status
```

---

## 📝 提交信息规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `custom:` | `nanodesk/` 的定制代码 | `custom: add screenshot tool` |
| `feat:` | 通用功能（可贡献）| `feat: add Discord channel` |
| `fix:` | Bug 修复 | `fix: handle timeout` |
| `docs:` | 文档改进 | `docs: update guide` |
| `sync:` | 同步上游 | `sync: merge upstream` |

---

**此文件已包含最关键信息，详细规范请阅读上述指向的文件。**
