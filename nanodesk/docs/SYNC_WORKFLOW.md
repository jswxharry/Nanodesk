# 上游同步工作流（AI 参考）

> 用户说"同步上游"、"更新主库"等指令时执行。

---

## 核心思想

将 **nanobot 主库的最新改进** 合并到 **你的 Nanodesk 个人定制版**，同时**完整保留你的定制代码**。

### 为什么做

- **免费获取改进**：Bug 修复、性能优化、新功能
- **保持兼容性**：避免定制代码与上游脱节
- **安全修复**：及时获得安全补丁

### 关键原则

```
nanobot/ 目录  →  上游代码  →  跟踪更新
nanodesk/ 目录 →  你的定制  →  同步时不触碰
```

**不是**覆盖你的代码，**而是**把上游改进「嫁接」到你的定制版上。

### 分支策略

```
upstream/main → origin/main → nanodesk
   (源头)        (镜像)       (你的工作)
```

- `main`：干净的 upstream 镜像
- `nanodesk`：你的工作分支

### AI 准则

**禁止**：
- ❌ 自动提交用户的代码改动
- ❌ 强制覆盖 `nanodesk/` 目录的文件
- ❌ 不询问就推送到远程

**必须**：
- ✅ 展示上游更新内容，让用户知情
- ✅ 冲突时优先保护 `nanodesk/` 的定制
- ✅ 关键操作后告知状态

**可自主判断**：
- 命令执行顺序（结果正确即可）
- 信息展示方式（清晰易懂即可）
- 错误处理话术（友好、清晰即可）

---

## 标准操作流程

> 理解目标后可微调细节

### 目标 1：确认状态和获取更新

**目标**：确认 upstream 是否有新提交，获取但不应用更新。

**关键检查点**：
- upstream 远程是否存在？
- 用户是否有未提交的本地改动？
- upstream 是否有新提交？

**参考命令**：
```bash
git remote -v                          # 确认配置
git fetch upstream                     # 获取更新
git log main..upstream/main --oneline  # 查看新提交
```

**如何处理**：
- 有未提交改动 → 询问是否暂存/提交，或继续（--force）
- 无新提交 → 告知"已是最新"，结束
- 有新提交 → 展示给用户，询问是否继续

---

### 目标 2：更新 main 分支

**目标**：让本地 main 与 upstream/main 完全一致（快进合并）。

**关键原则**：
- 使用 `--ff-only` 确保安全
- 失败说明本地 main 有额外提交，需调查原因

**参考命令**：
```bash
git checkout main
git merge upstream/main --ff-only
```

**如何处理**：
- 成功 → 继续下一步
- 失败 → 检查本地 main 的额外提交，决定 reset 或人工处理

---

### 目标 3：合并到 nanodesk 工作分支

**目标**：将 main 的更新合并到 nanodesk，解决可能的冲突。

**关键原则**：
- 优先保留 `nanodesk/` 的本地内容
- `nanobot/` 接受 upstream 版本
- 根目录配置文件根据 `.gitattributes` 处理

**参考命令**：
```bash
git checkout nanodesk
git merge main -m "sync: merge upstream updates into nanodesk"
```

**冲突处理策略**：

```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# 策略：nanobot/ 接受 upstream，nanodesk/ 保留本地
git checkout --theirs nanobot/
git checkout --ours nanodesk/
git add .
git commit -m "sync: merge upstream and resolve conflicts"
```

**如何处理**：
- 冲突文件少 → 逐文件处理并告知用户
- 冲突文件多（全是 nanobot/）→ 批量处理
- nanodesk/ 有冲突 → 展示具体内容让用户确认

---

### 目标 4：推送到远程（需用户确认）

**目标**：将本地更新推送到 origin，保持远程同步。

**关键原则**：
- 推送前必须展示变更内容
- 必须获得用户明确确认

**参考命令**：
```bash
git log origin/main..main --oneline       # 展示 main 的变更
git log origin/nanodesk..nanodesk --oneline  # 展示 nanodesk 的变更
git push origin main
git push origin nanodesk
```

**确认话术**：
> "同步完成，main 分支有 X 个新提交。是否推送到远程 origin？"

---

## 常见异常情况处理

### 场景 1：没有 upstream 远程

**现象**：`git fetch upstream` 报错 "does not appear to be a git repository"

**处理**：
```bash
git remote add upstream https://github.com/HKUDS/nanobot.git
```

**建议**：确认用户在本地开发后直接添加；不确定则询问用户。

---

### 场景 2：main 分支无法 fast-forward

**现象**：`--ff-only` 失败

**诊断**：
```bash
git log --graph --oneline --all --decorate -10
```

**可能原因**：
1. 之前误在 main 分支提交过东西
2. upstream 被 force push（罕见）

**处理**：
- 确认本地 main 的提交已提取到 nanodesk → `git reset --hard upstream/main`
- 不确定 → 询问用户

---

### 场景 3：合并到 nanodesk 时冲突

**现象**：`git merge main` 后 `git status` 显示冲突文件

**核心决策**：
- `nanobot/` 目录 → 接受 upstream（`--theirs`）
- `nanodesk/` 目录 → 保留本地（`--ours`）
- 根目录（README/.gitignore 等）→ 根据 `.gitattributes`，通常是保留本地

**处理**：
- 冲突文件少 → 逐文件处理并告知用户
- 冲突文件多（全是 nanobot/）→ 批量处理
- nanodesk/ 有冲突 → 展示具体内容让用户确认

---

### 场景 4：网络问题

**现象**：`git fetch upstream` 超时或连接失败

**处理**：
1. 检查网络连接
2. 如果使用代理，确认代理可用
3. 重试

**建议**：自动重试 1-2 次，仍失败则告知用户。

---

## 用户交互建议

### 发现更新时

```
发现 upstream 有新提交：

b429bf9 fix: improve long-running stability for various channels

变更文件：
- nanobot/channels/dingtalk.py
- nanobot/channels/feishu.py
- nanobot/channels/qq.py
- nanobot/channels/telegram.py

是否执行同步？[Y/n]
```

### 同步完成后

```
✅ 同步完成！

更新内容：
- 飞书/钉钉/QQ：添加自动重连机制
- Telegram：增大连接池 + 错误处理

当前状态：
- main: b429bf9 (与 upstream 同步)
- nanodesk: 93ce21f (已合并 upstream)

是否推送到远程 origin？[Y/n]
```

### 遇到冲突时

```
⚠️ 合并到 nanodesk 时遇到冲突

冲突文件：
- nanobot/channels/feishu.py（接受 upstream 版本）
- nanodesk/bootstrap.py（保留你的版本）

已自动解决。确认后完成合并？[Y/n]
```

---

## 检查清单

同步完成后确认：

- [ ] `main` 分支与 `upstream/main` 同步（`git log main..upstream/main` 无输出）
- [ ] `nanodesk` 分支已合并 main（`git log main..nanodesk` 显示合并提交）
- [ ] 如有冲突，已按策略解决（nanobot/ 接受 upstream，nanodesk/ 保留本地）
- [ ] 推送前获得用户确认
- [ ] 推送后远程分支状态正确
- [ ] 如有功能变更，告知用户可能的影响

---

## 相关文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 分支策略说明
- [CODE_LOCATION.md](./CODE_LOCATION.md) - 代码归属详细判断标准
- [COMMIT_RULES.md](./COMMIT_RULES.md) - 提交信息规范
- [nanobot AGENTS.md](../AGENTS.md) - 原库开发指南

---

**更新记录**:

| 日期 | 内容 |
|------|------|
| 2026-02-12 | 创建文档，整理同步流程 |
