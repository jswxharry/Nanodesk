# Nanodesk 分支管理规范

> Git 工作流和分支策略，确保开发有序、发布可控
> 
> 最后更新：2026-02-14

---

## 分支类型

### 1. 长期分支（Protected）

| 分支 | 用途 | 保护规则 |
|------|------|---------|
| `main` | 上游同步 | 仅同步 upstream，禁止直接提交 |
| `nanodesk` | **稳定版** | 仅通过 PR/MR 合并，禁止直接推送 |
| `develop` | **开发版** | 功能集成，日常开发基准 |

### 2. 短期分支（Temporary）

| 前缀 | 用途 | 生命周期 |
|------|------|---------|
| `feature/*` | 新功能开发 | 合并后删除 |
| `fix/*` | 问题修复 | 合并后删除 |
| `release/*` | 版本发布准备 | 发布后删除 |
| `hotfix/*` | 紧急修复 | 合并后删除 |

---

## 工作流图示

```
upstream/main ──────┬───────────────────────────
                    │ fetch/merge
                    ▼
origin/main ───────●────────●─────────●─────────  (只读镜像)
                    \       /         /
                     \     / merge   /
                      \   /         /
                       \ /         /
origin/nanodesk ────────●─────────●──────────────  (稳定版)
                       / \       /
                      /   \     /
                     /     \   /
                    /       \ /
origin/develop ────●─────────●───────────────────  (开发版)
                  / \       / \
                 /   \     /   \
                /     \   /     \
               /       \ /       \
feature/* ────●         ●         ●──────────────  (功能分支)
             /         /         /
feature/* ──●─────────●─────────●────────────────  (功能分支)
```

---

## 标准工作流程

### 场景 1：开发新功能

```bash
# 1. 从 develop 创建功能分支
git checkout develop
git pull origin develop
git checkout -b feature/search-tools

# 2. 开发并提交
git add .
git commit -m "feat: add DuckDuckGo search tool"

# 3. 推送到远程
git push -u origin feature/search-tools

# 4. 创建 Pull Request 到 develop
# 在 GitHub 上操作，或请 AI 协助

# 5. 代码审查通过后合并
# 合并后可选择删除分支
git branch -d feature/search-tools
git push origin --delete feature/search-tools
```

### 场景 2：修复 Bug

```bash
# 从 develop 创建修复分支
git checkout develop
git checkout -b fix/tray-icon-missing

# 修复、提交、PR 流程同上
```

### 场景 3：发布新版本

```bash
# 1. 从 develop 创建发布分支
git checkout develop
git checkout -b release/v0.3.0

# 2. 版本号更新、文档整理
# 只做与发布相关的修改，不添加新功能

# 3. 合并到 nanodesk（稳定版）
git checkout nanodesk
git merge release/v0.3.0 --no-ff -m "release: v0.3.0"

# 4. 打标签
git tag -a v0.3.0 -m "Release version 0.3.0"
git push origin nanodesk --tags

# 5. 同步回 develop
git checkout develop
git merge nanodesk

# 6. 删除发布分支
git branch -d release/v0.3.0
```

### 场景 4：紧急修复（Hotfix）

```bash
# 从 nanodesk 创建 hotfix 分支
git checkout nanodesk
git checkout -b hotfix/critical-bug

# 修复并测试后
# 合并到 nanodesk 和 develop 两个分支
git checkout nanodesk
git merge hotfix/critical-bug --no-ff -m "hotfix: critical bug"

git checkout develop
git merge hotfix/critical-bug --no-ff -m "hotfix: critical bug (sync to develop)"

git branch -d hotfix/critical-bug
```

---

## 分支命名规范

```
feature/<简短描述>           # 功能：feature/search-tools
fix/<问题描述>               # 修复：fix/tray-icon-gc
release/<版本号>             # 发布：release/v0.3.0
hotfix/<问题描述>            # 热修：hotfix/memory-leak
docs/<文档描述>              # 文档：docs/api-reference
refactor/<重构描述>          # 重构：refactor/config-manager
test/<测试描述>              # 测试：test/browser-tools
```

---

## 提交信息规范

```
<type>: <简短描述>

<body>  # 可选

<footer>  # 可选
```

**类型：**
- `feat` - 新功能
- `fix` - 修复
- `docs` - 文档
- `style` - 代码格式（不影响功能）
- `refactor` - 重构
- `test` - 测试
- `chore` - 构建/工具
- `perf` - 性能优化
- `release` - 版本发布
- `sync` - 上游同步

---

## 保护规则建议

### GitHub 分支保护（推荐配置）

**nanodesk 分支：**
- [x] Require pull request reviews before merging
- [x] Require status checks to pass
- [x] Require branches to be up to date before merging
- [x] Restrict pushes that create files larger than 100MB

**main 分支：**
- [x] Restrict pushes that create files larger than 100MB
- [x] Allow force pushes (用于同步 upstream)

---

## Squash 合并与冲突避免

> ⚠️ **重要**：如果使用 Squash and Merge，必须遵循以下流程避免冲突

### 问题背景

GitHub 的 **Squash and Merge** 会把多个提交压缩成一个新提交（不同哈希），导致：

```
develop:  A→B→C          nanodesk: A→B'(squash)
              ↓ 继续修改        ↓ 基于 squash 继续
         冲突！B和B'是不同提交
```

### 解决方案

每次 PR 合并到 `nanodesk` 后，立即同步 `develop`：

```bash
# 1. 确保本地是最新
 git fetch origin nanodesk develop

# 2. 切换到 develop，重置为 nanodesk
git checkout develop
git reset --hard origin/nanodesk

# 3. 强制推送（覆盖 develop 的历史）
git push --force-with-lease origin develop
```

### 完整工作流程

```bash
# 开发阶段
 git checkout develop
git checkout -b feature/xxx
# ... 开发 ...
git push origin feature/xxx
# 创建 PR: feature/xxx → develop
# 合并到 develop

# 发布阶段（develop → nanodesk）
# 创建 PR: develop → nanodesk
# 选择 "Squash and merge"
# PR 合并完成后，立即执行同步：

git fetch origin
git checkout develop
git reset --hard origin/nanodesk
git push --force-with-lease origin develop
```

### 替代方案

如果不希望用 `reset --hard`，可以在 GitHub 设置中：

```
Settings → Branches → Branch protection rules → nanodesk
  ↓
Require merge strategy:
  ✅ Allow merge commits      ← 使用这个
  ❌ Allow squash merging    ← 禁用这个
```

**区别**：
- **Merge commit**: 保留完整历史，不会产生冲突，但历史较复杂
- **Squash**: 历史简洁，但需每次手动同步 develop

---

## 快速命令参考

```bash
# 查看所有分支
git branch -a

# 查看分支图
git log --graph --oneline --all --decorate -20

# 清理已合并的本地分支
git branch --merged | grep -v "\*" | grep -v "main\|nanodesk\|develop" | xargs -n 1 git branch -d

# 清理已合并的远程分支
git remote prune origin

# 同步上游（main 分支）
./nanodesk/scripts/git/sync-upstream.ps1
```

---

## 迁移计划

> 从当前"单分支开发"迁移到"多分支工作流"

### 步骤 1：创建 develop 分支（现在执行）

```bash
# 基于当前 nanodesk 创建 develop
git checkout nanodesk
git checkout -b develop
git push -u origin develop

# 设置默认分支为 develop（GitHub 设置）
```

### 步骤 2：后续开发流程

1. 所有新功能从 `develop` 创建 `feature/*` 分支
2. 通过 PR 合并回 `develop`
3. 定期将 `develop` 合并到 `nanodesk`（发布）

### 步骤 3：历史债务处理

- 当前 `nanodesk` 保持为稳定版
- 未来新功能走 `feature/*` → `develop` → `nanodesk` 流程

---

## 相关文档

- [ARCHITECTURE.md](./ARCHITECTURE.md) - 项目架构
- [SYNC_WORKFLOW.md](./SYNC_WORKFLOW.md) - 上游同步流程
- [COMMIT_RULES.md](./COMMIT_RULES.md) - 提交规范
- [VERSIONING.md](./VERSIONING.md) - 版本管理
