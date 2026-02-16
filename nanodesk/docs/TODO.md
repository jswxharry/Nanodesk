# Nanodesk 待办事项

> 记录进行中的任务和待办功能
> 
> 最后更新：2026-02-16
> 
> 📜 **历史记录**: [CHANGELOG.md](./CHANGELOG.md)

---

## 待办功能 📋

### 🔴 高优先级（用户体验关键）

| 优先级 | 功能 | 状态 | 来源 | 备注 |
|--------|------|------|------|------|
| ⭐⭐⭐ | **本地知识检索** | 🔴 待设计 | [discussion/2026-02-14-core-philosophy-and-features.md](./discussion/2026-02-14-core-philosophy-and-features.md) | 最痛的点：Agent 无法回答"我之前说过什么" |
| ⭐⭐⭐ | **工具执行即时反馈** | 📝 设计完成 | [TOOL_EXECUTION_FEEDBACK.md](./design/TOOL_EXECUTION_FEEDBACK.md) | 解决"执行后无响应"的 UX 问题 |
| ⭐⭐⭐ | **关屏保持运行** | ✅ 已完成 | [PREVENT_SLEEP_KEEP_RUNNING.md](./design/PREVENT_SLEEP_KEEP_RUNNING.md) | Windows 电源管理，已实现 + 测试文档 |
| ⭐⭐ | Windows 截图工具 | 📋 待开发 | - | 飞书指令截图 |
| ⭐⭐ | **Agent 依赖自动安装** | 📋 待评估 | - | 允许 Agent 执行 pip install 等命令安装缺失依赖 |

### 🟡 中优先级（功能增强）

| 优先级 | 功能 | 状态 | 来源 | 备注 |
|--------|------|------|------|------|
| ⭐⭐ | **AI 自主开发与测试** | 📝 设计完成 | [AI_AUTONOMOUS_DEVELOPMENT.md](./design/AI_AUTONOMOUS_DEVELOPMENT.md) | 自动化测试、Vision-guided 验证 |
| ⭐ | 本地文件管理 | 📋 待开发 | - | 读取本地文件 |
| ⭐ | 钉钉通道 | 📋 评估中 | - | 备选通道 |

### 🟢 低优先级（Nice to have）

| 优先级 | 功能 | 状态 | 来源 | 备注 |
|--------|------|------|------|------|
| ⭐ | **配置向导更新** | 📋 待开发 | upstream #604 | 支持 Custom Provider 配置（目前需手动编辑 config.json）|
| ⭐ | **上下文大小显示** | 📝 设计完成 | [CONTEXT_SIZE_DISPLAY.md](./design/CONTEXT_SIZE_DISPLAY.md) | 显示对话 token 数，依赖 PR #257 |
| ⭐ | **搜索能力强化** | 📝 设计完成 | [SEARCH_ENHANCEMENT.md](./design/SEARCH_ENHANCEMENT.md) | 多源聚合、SearXNG 自托管方案 |
| ⭐ | 飞书语音 | 🔄 回滚待审 | - | 需开通 `im:resource` 权限 |
| ⭐ | Discord | ❌ 搁置 | - | 需代理 |

---

## 已完成 ✅

- [x] **Ollama Provider 支持** - Nanodesk 层实现本地 Ollama 模型支持 ✅ 2026-02-16
  - 实现 `nanodesk/providers/ollama_provider.py`
  - 推荐模型 qwen2.5:3b，实测 15-40 秒响应
  - 文档整理到 `docs/setup/`
- [x] **搜索工具测试** - ddg_search, browser_search, browser_fetch
- [x] **上游 v0.1.3.post7 测试** - 内存系统 v2、`/new` 命令、飞书修复
- [x] 文档精简（5篇文档 -732行）
- [x] 脚本分类整理（build/dev/git/release）
- [x] 自动化测试脚本（run_tests.ps1）

---

## 待合并

- [x] ~~合并 `develop` → `nanodesk`（测试已通过，等待执行）~~ ✅ 2026-02-14 完成
- [x] 合并 `develop` → `nanodesk`（BRANCHING.md Squash 合并指南更新）✅ 已完成

---

## 上游跟踪 🔗

详见 [UPSTREAM_PRS.md](./UPSTREAM_PRS.md)

| PR | 功能 | 优先级 |
|----|------|--------|
| #257 | Token Usage Tracking | 🔴 高 |
| #171 | MCP Support | 🔴 高 |
| #272 | Custom Provider | 🟡 中 |

---

## 快速参考

```powershell
# 运行测试
.\nanodesk\scripts\dev\run_tests.ps1          # 完整测试
.\nanodesk\scripts\dev\run_tests_quick.ps1    # 快速测试

# 启动桌面应用（开发模式）
.\nanodesk\scripts\dev\run_desktop.ps1

# 启动 Gateway
nanodesk gateway --verbose

# 同步上游
.\nanodesk\scripts\git\sync-upstream.ps1
```

---

## 文档索引

### 核心文档
- [README.md](./README.md) - 文档总索引
- [CHANGELOG.md](./CHANGELOG.md) - 版本历史
- [BRANCHING.md](./BRANCHING.md) - Git 分支管理
- [CONTRIBUTING.md](./CONTRIBUTING.md) - 开发者指南
- [UPSTREAM_PRS.md](./UPSTREAM_PRS.md) - 上游 PR 跟踪
- [BUILD.md](./BUILD.md) - 构建指南
- [testing/](./testing/) - 测试文档

### 设计文档（功能提案）
| 文档 | 优先级 | 状态 | 说明 |
|------|--------|------|------|
| [TOOL_EXECUTION_FEEDBACK.md](./design/TOOL_EXECUTION_FEEDBACK.md) | 🔴 高 | 📝 设计完成 | 工具执行即时反馈 |
| [PREVENT_SLEEP_KEEP_RUNNING.md](./design/PREVENT_SLEEP_KEEP_RUNNING.md) | 🔴 高 | 📝 设计完成 | 关屏保持运行 |
| [AI_AUTONOMOUS_DEVELOPMENT.md](./design/AI_AUTONOMOUS_DEVELOPMENT.md) | 🟡 中-高 | 📝 设计完成 | 自动化测试系统 |
| [CONTEXT_SIZE_DISPLAY.md](./design/CONTEXT_SIZE_DISPLAY.md) | 🟢 低-中 | 📝 设计完成 | 上下文 token 显示 |
| [SEARCH_ENHANCEMENT.md](./design/SEARCH_ENHANCEMENT.md) | 🟢 低-中 | 📝 设计完成 | 搜索能力强化 |
