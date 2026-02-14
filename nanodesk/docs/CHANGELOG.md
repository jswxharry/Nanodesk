# Nanodesk 开发日志

> 记录版本发布历史和功能变更
> 
> 最后更新：2026-02-15

---

## [Unreleased] - develop

### 修复

- **Windows 终端编码兼容** - 自动检测并切换 UTF-8 编码，避免 `UnicodeEncodeError`
  - `launcher.py` - 启动时检测编码，自动切换到 UTF-8
  - `bootstrap.py` - 设置 `PYTHONIOENCODING=utf-8`，替换 `__logo__` 为 ASCII 版本

---

## [v0.2.2] - 2026-02-15

### 新增功能

- **Windows 电源管理** - Gateway 运行时阻止睡眠，关屏保持运行
  - AC 电源：自动阻止系统睡眠（5 分钟轮询检测电源变化）
  - 电池模式：允许正常睡眠，保护电池
  - 系统托盘通知：显示当前电源状态和睡眠行为
  - 文件：`power_manager.py` (~150 行)

- **Gateway 单实例锁** - 防止重复启动多个 Gateway
  - Socket 端口 28790 绑定实现
  - 第二个实例自动检测并退出
  - 进程崩溃/退出后端口自动释放

### 修复

- **日志重复打印** - 移除 `log_message` 信号重复连接
  - `main_window.py` - 统一使用 `log_received` 信号
  - `process_manager.py` - 移除冗余信号发射

### 测试

- **自动化测试**：通过 10/10
  - `test_power_management.py` - 电源管理模块测试
  - 包含：单实例锁、线程安全、API 测试等

- **手动测试**：通过 3/3
  1. 插电阻止睡眠 - powercfg 验证
  2. 电池允许睡眠 - 电源计划验证
  3. 单实例锁 - 双终端启动验证

### 文档

- **测试报告**：`test-report-20260215-v0.2.2-power-management.md`
- **AGENTS.md**：更新 `core_agent_lines.sh` 路径
- **AI_COLLABORATION.md**：更新脚本路径
- **BRANCHING.md**：更新脚本路径

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
