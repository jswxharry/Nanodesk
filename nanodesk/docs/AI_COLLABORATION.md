# AI 协作指南

> 本文档面向 AI 编程助手，指导如何与 Nanodesk 项目协作。
> 
> 涵盖：代码位置决策、Git 工作流、提交规范、项目架构

---

## 一、核心原则（必读）

### 1.1 Git 操作必须经用户确认 ⚠️

**禁止行为**：
- ❌ 自动 `git commit` 而不告知用户
- ❌ 自动 `git push` 到远端
- ❌ 批量提交未审核的改动

**正确流程**：
```
1. AI 完成代码修改
2. AI 展示改动内容（git diff 或文件列表）
3. 用户审核确认
4. AI 执行：git add → git commit → git push（如需）
```

**确认话术**：
- "代码已修改，请审核后确认是否提交"
- "改动内容如下，确认后我将执行 git commit"
- "是否推送到远端 origin/nanodesk 分支？"

### 1.2 代码位置决策

修改代码前，先判断：

> **"这段代码对原库的其他用户也有用吗？"**

| 答案 | 位置 | 后续操作 |
|------|------|---------|
| **是** | `nanobot/`（或后续提取）| 用 `feat:`/`fix:` 提交，考虑提 PR |
| **否** | `nanodesk/`（个人定制）| 用 `custom:` 提交 |

**快速判断标准**：
- ✅ `nanobot/` - Bug 修复、通用功能、性能优化、文档改进
- ✅ `nanodesk/` - Windows 特定功能、个人工作流、实验性代码、私有业务逻辑

---

## 二、详细判断标准

复杂的代码归属判断场景，参见 [CODE_LOCATION.md](./CODE_LOCATION.md)：

- 必须放在 `nanodesk/` 的情况（个人环境、私有业务、实验功能等）
- 适合 `nanobot/` 的情况（Bug 修复、通用功能、性能优化等）
- 灰色地带决策流程图
- 具体代码示例

**快速原则**：
- ✅ `nanobot/` - Bug 修复、通用功能、性能优化、文档改进
- ✅ `nanodesk/` - Windows 特定功能、个人工作流、实验性代码、私有业务逻辑
- **不确定时**：优先放 `nanodesk/`，标记 `TODO: evaluate for upstream`

---

## 三、提交信息规范

### 3.1 前缀规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `custom:` | 个人定制代码（`nanodesk/`） | `custom: add my screenshot tool` |
| `feat:` | 通用功能（`nanobot/`） | `feat: add Mattermost channel` |
| `fix:` | Bug 修复 | `fix: handle timeout in shell tool` |
| `docs:` | 文档改进 | `docs: update deployment guide` |
| `refactor:` | 重构优化 | `refactor: simplify memory manager` |
| `chore:` | 维护工作 | `chore: update dependencies` |
| `sync:` | 同步上游 | `sync: merge upstream into nanodesk` |

### 3.2 特殊标记

**修改了 `nanobot/` 但不确定是否适合贡献**：
```bash
git commit -m "fix(web): handle redirect loop - TODO: evaluate for upstream"
```

**必须修改核心文件的个人适配**：
```bash
git commit -m "custom: patch memory limit for local LLM"
```

### 3.3 分支提交规范

**nanodesk 分支（工作分支）**：
```bash
custom: add personal tools
feat: implement new channel - TODO: extract
docs: update my notes
```

**main 分支（干净分支，用于提 PR）**：
```bash
feat: add Discord thread support
fix: correct timeout calculation
docs: fix typo in README
```

### 3.4 禁止的提交信息

❌ 模糊不清：
```bash
git commit -m "update"           # 不知道改了什么
git commit -m "fix bug"          # 什么 bug？
git commit -m "changes"          # 无意义
```

---

## 四、Git 工作流

### 4.1 分支策略

| 分支 | 用途 | 规则 |
|------|------|------|
| `main` | 跟踪上游，提 PR | `git merge upstream/main --ff-only`，不直接开发 |
| `nanodesk` | 主工作分支 | 日常开发，可修改任何文件 |

### 4.2 同步上游

```bash
# 使用脚本（推荐）
.\nanodesk\scripts\sync-upstream.ps1

# 或手动
git checkout main
git fetch upstream
git merge upstream/main --ff-only
git checkout nanodesk
git merge main
```

### 4.3 提取贡献

```bash
# 使用脚本
.\nanodesk\scripts\extract-contrib.ps1 <commit-hash>

# 或手动
git checkout main
git checkout -b contrib/fix-xxx
git cherry-pick <commit-from-nanodesk>
git push origin contrib/fix-xxx
# 然后到 GitHub 提 PR
```

---

## 五、项目结构

```
Nanodesk/
├── nanobot/                 # 📦 原库代码（跟踪上游）
│   ├── agent/               # 核心代理逻辑
│   ├── channels/            # 官方频道（TG/Discord/飞书等）
│   └── ...
├── nanodesk/                # 🔥 你的定制
│   ├── channels/            # 你的自定义频道
│   ├── tools/               # 你的自定义工具
│   ├── skills/              # 你的技能
│   └── docs/                # 本文档
├── .vscode/                 # VS Code 配置
├── .kimi/                   # Kimi Code 配置
└── README.md                # 顶部加 Nanodesk 标识
```

### 5.1 特殊文件保护

以下文件受 `.gitattributes` 保护，同步上游时自动保留我们的版本：
- `README.md`
- `.gitignore`
- `.gitattributes`

修改这些文件前请确认必要性。

---

## 六、开发规范

### 6.1 路径处理（Windows 开发）

```python
# ✅ 正确 - 跨平台
from pathlib import Path
config_path = Path.home() / ".nanobot" / "config.json"

# ❌ 错误 - Windows 不兼容
config_path = os.path.expanduser("~/.nanobot/config.json")
```

### 6.2 编码规范

- 文件编码：UTF-8
- 换行符：Git 自动处理，不要手动改
- 脚本：优先 `.ps1` (PowerShell)，保留 `.sh` 用于 WSL

### 6.3 类型注解

```python
# Python 3.11+ 语法
def process(text: str | None) -> list[str]:
    ...
```

---

## 七、禁止事项

- ❌ 在 `nanodesk/` 中硬编码个人敏感信息（密码、Token、私钥）
- ❌ 未经评估直接修改 `nanobot/` 核心文件
- ❌ 将个人业务逻辑伪装成通用功能
- ❌ 未经用户确认执行 Git 操作

---

## 八、推荐事项

- ✅ 使用配置而非硬编码
- ✅ 写清晰的注释说明代码用途
- ✅ 不确定时优先放 `nanodesk/`
- ✅ 定期同步上游，减少冲突
- ✅ 有意义的提交信息，方便 cherry-pick

---

## 九、参考

- [nanobot AGENTS.md](../AGENTS.md) - 原库开发指南
- [nanobot README.md](../README.md) - 原库说明

---

**更新记录**:

| 日期 | 内容 |
|------|------|
| 2026-02-12 | 合并 AI_GUIDELINES、AI_PREFERENCES、CODE_LOCATION、COMMIT_RULES |
