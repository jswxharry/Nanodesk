# Nanodesk 开发日志

> 记录版本发布历史和功能变更
> 
> 最后更新：2026-02-14

---

## [Unreleased] - develop

### 修复

- **Windows 终端编码兼容** - 自动检测并切换 UTF-8 编码，避免 `UnicodeEncodeError`
  - `launcher.py` - 启动时检测编码，自动切换到 UTF-8
  - `bootstrap.py` - 设置 `PYTHONIOENCODING=utf-8`，替换 `__logo__` 为 ASCII 版本

---

## [v0.2.1] - 2026-02-13

### 新增功能

- **搜索工具** ✅
  - `ddg_search` - DuckDuckGo 搜索（无需 API Key）
  - `browser_search` - 浏览器搜索（Playwright，需手动安装）
  - `browser_fetch` - 浏览器页面抓取（支持 JS 渲染）

- **Git 分支管理**
  - 创建 `develop` 分支作为开发基准
  - 配置 GitHub 分支保护规则
  - 建立 `feature → develop → nanodesk` 工作流
  - 添加 [BRANCHING.md](./BRANCHING.md) 分支管理规范

- **自动化测试**
  - `run_tests.ps1` - 完整测试套件
  - `run_tests_quick.ps1` - 快速测试（CI/CD）

### 上游同步（v0.1.3.post7）

- **内存系统 v2** - 双层架构（热/冷内存）+ grep 检索
- **`/new` 命令** - 跨频道统一的斜杠命令，支持新建会话和内存整合
- **飞书修复** - 卡片消息 Markdown 标题转 div 元素
- **WhatsApp 安全** - Bridge 绑定 localhost，添加可选 Token 认证

### 修复

- 退出时崩溃（`_log_handler` 拼写错误）
- `ddg_search` 包名变更（`duckduckgo-search` → `ddgs`）

### 文档更新

- 新增 [BRANCHING.md](./BRANCHING.md) - Git 分支管理规范
- 新增 [CONTRIBUTING.md](./CONTRIBUTING.md) - 开发者指南
- 新增 [testing/](./testing/) - 测试文档套件
- 精简 WINDOWS_DEV.md、SYNC_WORKFLOW.md 等 5 篇文档（-732 行）
- 脚本分类整理为 build/dev/git/release 四个目录

### 测试

- AI 自动化测试：通过（85.7%）

---

## [v0.2.2-dev] - 2026-02-14

### 理念调整

- **核心理念**: 从"轻量框架"调整为"实用个人助手"
- **原则**: Practicality first, lightweight second（实用优先，轻量为辅）
- **目标**: 开箱即用，保持代码可控
- **记录**: [discussion/2026-02-14-core-philosophy-and-features.md](./discussion/2026-02-14-core-philosophy-and-features.md)

### 设计文档

- 工具执行即时反馈、关屏保持运行、搜索强化等 5 个设计提案
- 手动测试：核心功能全部通过
- 测试报告：[test-report-20260213-final.md](./testing/reports/test-report-20260213-final.md)

---

## [v0.2.0] - 2026-02-12

### 新增功能

- **Windows 桌面应用** - Phase 1 & 2 完成
  - PySide6 GUI 框架
  - 3 步配置向导（Provider → Channel → Confirm）
  - 系统托盘管理（启动/停止/状态）
  - 日志系统（文件轮转 + 查看器对话框）
  - 配置加密（Windows DPAPI）
  - 嵌入 Python 打包（无需用户安装 Python）
  - Inno Setup 安装程序

### 修复

- 系统托盘修复（图标、菜单、GC 问题）
- 应用退出时自动停止 Gateway

### 辅助脚本

- `run_desktop.ps1` - 启动桌面应用（自动 UTF-8 编码）
- `kill_all.ps1` - 强制结束所有 Nanodesk 相关进程
- `release.ps1` - 版本发布（更新版本号 + 创建标签）

### 上游同步（首次）

- edit_file 工具支持
- Chain-of-Thought 反思
- 定时任务 'at' 参数
- 时区显示

### 文档

- 创建待办事项文档 [TODO.md](./TODO.md)
- 添加上游 PR 跟踪文档 [UPSTREAM_PRS.md](./UPSTREAM_PRS.md)

---

## [v0.1.0] - 2026-02-10

### 基础架构

- Nanodesk 项目初始化
- 目录结构（nanodesk/ vs nanobot/ 分离）
- VS Code 配置（调试、设置）
- 基础脚本（sync-upstream, build 等）

### 功能

- 飞书通道（WebSocket、消息收发、Markdown）
- 阿里云百炼 LLM 配置

### 文档

- 开发规范文档（AI_COLLABORATION.md、COMMIT_RULES.md）
- 架构设计文档（ARCHITECTURE.md）
- 飞书配置指南（FEISHU_SETUP.md）
