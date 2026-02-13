# 上游同步工作流（AI 参考）

> 用户说"同步上游"、"更新主库"等指令时执行。
> 
> **分支策略详见**：[BRANCHING.md](./BRANCHING.md)

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

### AI 准则

**禁止**：
- ❌ 自动提交用户的代码改动
- ❌ 强制覆盖 `nanodesk/` 目录的文件
- ❌ 不询问就推送到远程

**必须**：
- ✅ 展示上游更新内容，让用户知情
- ✅ 冲突时优先保护 `nanodesk/` 的定制
- ✅ 关键操作后告知状态

---

## 快速命令

```bash
# 一键同步（推荐）
./nanodesk/scripts/git/sync-upstream.ps1

# 手动同步
# 1. 获取上游更新
git fetch upstream
git log main..upstream/main --oneline  # 查看新提交

# 2. 更新 main 分支
git checkout main
git merge upstream/main --ff-only

# 3. 合并到 develop
git checkout develop
git merge main -m "sync: merge upstream updates"

# 4. 推送
git push origin main develop
```

---

## 常见异常处理

### 场景 1：没有 upstream 远程

```bash
git remote add upstream https://github.com/HKUDS/nanobot.git
```

### 场景 2：main 无法 fast-forward

```bash
# 查看分支状态
git log --graph --oneline --all --decorate -10

# 如确认本地 main 有误，强制重置
git reset --hard upstream/main
```

### 场景 3：合并冲突

```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# 策略：nanobot/ 接受 upstream，nanodesk/ 保留本地
git checkout --theirs nanobot/
git checkout --ours nanodesk/
git add .
git commit -m "sync: merge upstream and resolve conflicts"
```

### 场景 4：网络问题

1. 检查网络连接
2. 确认代理设置
3. 重试 1-2 次

---

## 检查清单

- [ ] `main` 与 `upstream/main` 同步
- [ ] `develop` 已合并 main
- [ ] 冲突已解决（nanobot/ 接受 upstream，nanodesk/ 保留本地）
- [ ] 推送前获得用户确认

---

## 相关文档

- [BRANCHING.md](./BRANCHING.md) - Git 分支管理规范
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 项目架构
