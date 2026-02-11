# 提交信息规范

帮助区分个人定制和可贡献代码的提交信息规则。

## 提交信息前缀

使用前缀让历史记录一目了然：

| 前缀 | 用途 | 示例 |
|------|------|------|
| `custom:` | 个人定制代码（nanodesk/） | `custom: add my company SSO` |
| `feat:` | 通用功能（nanobot/） | `feat: add Mattermost channel` |
| `fix:` | Bug 修复 | `fix: handle timeout in shell tool` |
| `docs:` | 文档改进 | `docs: update deployment guide` |
| `refactor:` | 重构优化 | `refactor: simplify memory manager` |
| `chore:` | 维护工作 | `chore: update dependencies` |
| `sync:` | 同步上游 | `sync: merge upstream into nanodesk` |

## 需要标记的情况

### 1. 修改了 nanobot/ 但不确定是否适合贡献

```bash
git commit -m "fix(web): handle redirect loop - TODO: evaluate for upstream"
```

后续评估后：
- 适合贡献 → `git commit --amend -m "fix(web): handle redirect loop"`
- 不适合 → `git commit --amend -m "custom: handle redirect loop for my case"`

### 2. 必须修改核心文件的个人适配

```bash
git commit -m "custom: patch memory limit for local LLM"
# 同时在 nanodesk/patches/ 生成 patch 文件备份
```

### 3. 临时/实验性功能

```bash
git commit -m "custom: WIP - experimental voice control"
```

## 分支提交规范

### nanodesk 分支（工作分支）

可混合各种提交：
```bash
custom: add personal tools
feat: implement new channel - TODO: extract
docs: update my notes
fix: workaround for my env
```

### main 分支（干净分支）

只保留规范提交，用于提 PR：
```bash
feat: add Discord thread support
fix: correct timeout calculation
docs: fix typo in README
```

## 提取贡献时的提交重写

从 `nanodesk` 提取到 `contrib/` 分支时，清理提交信息：

```bash
# 1. cherry-pick 并修改信息
git cherry-pick <hash>
git commit --amend -m "feat: clean message"  # 移除 custom: 和 TODO:

# 2. 或 squash 多个相关提交
git merge --squash <branch>
git commit -m "feat: complete feature description"
```

## 禁止的提交信息

❌ 模糊不清：
```bash
git commit -m "update"           # 不知道改了什么
git commit -m "fix bug"          # 什么 bug？
git commit -m "changes"          # 无意义
```

❌ 混合多个不相关改动：
```bash
git commit -m "fix bug and add feature and update docs"  # 拆分提交
```

## 好的提交信息示例

```bash
# 个人定制
custom: add screenshot tool for macOS
custom: configure default model to local LLM
custom: disable Telegram channel in default config

# 通用功能
feat(channels): add Slack thread support
feat(tools): add PDF reader tool
feat(config): add timeout option for web search

# Bug 修复
fix(shell): handle command not found error
fix(memory): prevent race condition on save

# 文档
docs: add Windows installation guide
docs(security): clarify API key storage

# 重构
refactor(agent): extract context builder
refactor(tools): use async context manager
```
