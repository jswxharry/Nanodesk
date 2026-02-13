# 开发者指南

> 代码归属判断、提交规范和语言策略

---

## 一、代码归属判断

决定代码应该放在 `nanobot/` 还是 `nanodesk/` 的标准。

### 1.1 必须放在 nanodesk/ 的情况（个人定制）

以下情况**绝对不要**放到原库：

| 类别 | 示例 |
|------|------|
| 个人环境相关 | 本地文件路径、个人电脑配置、仅在你的机器上能运行的代码 |
| 私有业务逻辑 | 公司内部工作流、个人账号逻辑、特定组织集成 |
| 实验/临时功能 | 快速原型、未测试稳定的功能、仅供个人学习的代码 |
| 特定工具依赖 | 只有你的电脑安装的软件、非通用 API、本地服务依赖 |

### 1.2 适合 nanobot/ 的情况（通用贡献）

以下情况**适合**贡献给原库：

| 类别 | 示例 |
|------|------|
| Bug 修复 | 修复崩溃、错误行为、改进错误处理 |
| 通用功能 | 新的 Channel（Discord、Slack 等）、通用工具、配置项扩展 |
| 性能优化 | 不改动行为的速度提升、内存优化 |
| 文档改进 | 修正错误说明、补充缺失文档 |

### 1.3 快速决策

```
这段代码对原库的其他用户也有用吗？
    ├── 是 → nanobot/（考虑提 PR）
    └── 否 → nanodesk/（个人定制）
```

**不确定时**：优先放 `nanodesk/`，标记 `TODO: evaluate for upstream`

---

## 二、提交规范

### 2.1 前缀规范

| 前缀 | 用途 | 示例 |
|------|------|------|
| `custom:` | 个人定制（`nanodesk/`） | `custom: add my screenshot tool` |
| `feat:` | 通用功能（`nanobot/`） | `feat: add Mattermost channel` |
| `fix:` | Bug 修复 | `fix: handle timeout in shell tool` |
| `docs:` | 文档改进 | `docs: update deployment guide` |
| `refactor:` | 重构优化 | `refactor: simplify memory manager` |
| `chore:` | 维护工作 | `chore: update dependencies` |
| `sync:` | 同步上游 | `sync: merge upstream into develop` |
| `release:` | 版本发布 | `release: v0.3.0` |
| `test:` | 测试相关 | `test: add unit tests for cron tool` |
| `perf:` | 性能优化 | `perf: reduce memory usage` |

### 2.2 特殊标记

**修改了 `nanobot/` 但不确定是否适合贡献**：
```bash
git commit -m "fix(web): handle redirect loop - TODO: evaluate for upstream"
```

**必须修改核心文件的个人适配**：
```bash
git commit -m "custom: patch memory limit for local LLM"
```

### 2.3 禁止的提交信息

❌ 模糊不清：
```bash
git commit -m "update"           # 不知道改了什么
git commit -m "fix bug"          # 什么 bug？
git commit -m "changes"          # 无意义
```

✅ 正确示例：
```bash
git commit -m "fix(feishu): handle empty message body in group chat"
git commit -m "feat(tools): add screenshot tool for Windows"
git commit -m "docs: update build guide for Windows 11"
```

---

## 三、语言策略

### 3.1 代码注释

- **使用英文**：代码注释、文档字符串
- 原因：国际化项目，英文是通用语言

```python
# ✅ Good
# Fetch message from queue and process it
async def process_message(msg: Message) -> None:
    """Process incoming message from queue."""
    pass

# ❌ Avoid
# 从队列获取消息并处理
async def process_message(msg: Message) -> None:
    """处理从队列来的消息."""
    pass
```

### 3.2 用户界面

- **中文优先**：面向中文用户的界面和错误提示
- 桌面应用、飞书消息、日志输出使用中文

```python
# ✅ Good
raise ValueError("API Key 不能为空，请在配置文件中设置")

# ❌ Avoid
raise ValueError("API Key cannot be empty")
```

### 3.3 项目文档

| 文档类型 | 语言 | 示例 |
|---------|------|------|
| 技术文档 | 中文 | ARCHITECTURE.md、BUILD.md |
| 代码注释 | 英文 | `nanobot/`、`nanodesk/` 内所有代码 |
| 用户指南 | 中文 | FEISHU_SETUP.md、CONFIGURATION.md |
| Git 提交 | 英文 | commit message |
| 变量/函数名 | 英文 | Python 代码 |

### 3.4 命名规范

```python
# ✅ 英文命名
class MessageHandler:
    def process_incoming(self, message: str) -> Result:
        pass

# ❌ 避免拼音或中文
class XiaoxiChuli:           # 不好
    def chuli_jieshou(self, msg: str):   # 不好
        pass
```

---

## 四、快速参考

### 代码位置检查清单

- [ ] 是否包含个人路径/账号？→ `nanodesk/`
- [ ] 是否仅在你的环境运行？→ `nanodesk/`
- [ ] 是否为通用 Bug 修复？→ `nanobot/`（考虑提 PR）
- [ ] 是否为新 Channel/工具？→ `nanobot/`（考虑提 PR）

### 提交流程

```bash
# 1. 创建功能分支
git checkout develop
git checkout -b feature/my-feature

# 2. 开发和提交
git add .
git commit -m "feat: add xxx feature"

# 3. 推送到远程
git push -u origin feature/my-feature

# 4. 创建 Pull Request 到 develop
```

---

## 参考

- [BRANCHING.md](./BRANCHING.md) - Git 分支管理
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 项目架构
