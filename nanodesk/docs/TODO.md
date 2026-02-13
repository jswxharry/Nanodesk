# Nanodesk 待办事项

> 记录项目待办功能和上游跟踪
> 
> 最后更新：2026-02-12

---

## 待办功能 📋

| 优先级 | 功能 | 状态 | 备注 |
|--------|------|------|------|
| ⭐⭐⭐ | **Windows 桌面版** | ✅ **已完成** | GUI + 配置向导 + 系统托盘 + 日志系统 + 嵌入 Python 打包 |
| ⭐ | 飞书语音 | 🔄 回滚待审 | 需开通 `im:resource` 权限 |
| ⭐⭐ | Windows 截图工具 | 📋 待开发 | 飞书指令截图 |
| ⭐ | 本地文件管理 | 📋 待开发 | 读取本地文件 |
| ⭐ | 钉钉通道 | 📋 评估中 | 备选通道 |
| ⭐ | Discord | ❌ 搁置 | 需代理 |
| ⭐⭐ | **搜索工具测试** | 🧪 **待测试** | ddg_search, browser_search, browser_fetch |

**平台策略**: 专注 Windows 桌面版，覆盖 80% 普通用户。Linux/macOS 用户继续使用 CLI。

**上游跟踪**: [UPSTREAM_PRS.md](./UPSTREAM_PRS.md)
- 🔴 PR #257 - Token Usage Tracking
- 🔴 PR #171 - MCP Support  
- 🟡 PR #272 - Custom Provider

---

## 桌面应用打包指南 📦

### 一键打包

```powershell
# 完整构建（清理 + 准备嵌入 Python + 打包）
.\nanodesk\scripts\build_all.ps1 -Clean

# 增量构建（跳过嵌入 Python 准备，快很多）
.\nanodesk\scripts\build_all.ps1
```

**输出位置：**
- `dist/Nanodesk/` - 便携版文件夹
- `dist/Nanodesk-Setup-x.x.x.exe` - 安装程序（需 Inno Setup）

### 手动打包步骤

```powershell
# 步骤1：准备嵌入 Python（首次或 pyproject.toml 变更后）
python .\nanodesk\scripts\prepare_embedded_python.py

# 步骤2：构建桌面应用
.\nanodesk\scripts\build_desktop.ps1

# 步骤3：创建安装程序（可选）
iscc .\nanodesk\scripts\setup.iss
```

### 创建便携版压缩包

```powershell
# PowerShell 方式（较慢）
Compress-Archive -Path dist\Nanodesk -DestinationPath Nanodesk-Portable.zip

# Python 方式（推荐）
cd dist
python -c "import zipfile, os; zf = zipfile.ZipFile('Nanodesk-Portable.zip', 'w', zipfile.ZIP_DEFLATED); [zf.write(os.path.join(root, f), os.path.relpath(os.path.join(root, f), 'Nanodesk')) for root, dirs, files in os.walk('Nanodesk') for f in files]; zf.close(); print(f'Compressed: {os.path.getsize(\"Nanodesk-Portable.zip\")/1024/1024:.2f} MB')"
```

### 包大小参考

| 格式 | 大小 | 说明 |
|------|------|------|
| 解压后 | ~404 MB | 嵌入 Python + 依赖（40,474 文件）|
| ZIP 压缩 | ~163 MB | 便携版下载 |
| 安装程序 | ~150-160 MB | Inno Setup |

---

## 已完成 ✅

- [x] Nanodesk 基础架构（目录结构、VS Code、脚本）
- [x] 飞书通道（WebSocket、消息收发、Markdown）
- [x] 阿里云百炼 LLM 配置
- [x] 开发规范文档（AI_COLLABORATION.md、COMMIT_RULES.md）
- [x] 上游 PR 跟踪文档
- [x] **Windows 桌面应用**（2026-02-12 完成）
  - [x] PySide6 GUI 框架
  - [x] 3 步配置向导（Provider → Channel → Confirm）
  - [x] 系统托盘管理（启动/停止/状态）
  - [x] 日志系统（文件轮转 + 查看器对话框）
  - [x] 配置加密（Windows DPAPI）
  - [x] 嵌入 Python 打包（无需用户安装 Python）
  - [x] Inno Setup 安装程序
- [x] 同步上游改进（2026-02-12）
  - [x] edit_file 工具支持
  - [x] Chain-of-Thought 反思
  - [x] 定时任务 'at' 参数
  - [x] 时区显示

---

## 快速参考

```powershell
# 启动桌面应用（开发模式，自动 UTF-8）
.\nanodesk\scripts\run_desktop.ps1

# 启动 Gateway（开发模式）
nanodesk gateway --verbose

# 强制关闭所有 Nanodesk 进程
.\nanodesk\scripts\kill_all.ps1

# 同步上游
.\nanodesk\scripts\sync-upstream.ps1

# 飞书指令
@机器人 你好    # 群聊
直接发消息      # 私聊
```

### 开发辅助脚本

| 脚本 | 用途 |
|------|------|
| `run_desktop.ps1` | 启动桌面应用（自动设置 UTF-8 编码） |
| `kill_all.ps1` | 强制结束所有 Nanodesk 相关进程 |
| `build_all.ps1` | 一键打包桌面版（含嵌入 Python） |
| `release.ps1` | 版本发布（更新版本号 + 创建标签） |

**文档索引**: 
- [BUILD.md](./BUILD.md) - 桌面应用构建和打包指南
- [DESKTOP_APP_PLAN.md](./DESKTOP_APP_PLAN.md) - 桌面应用开发计划（Phase 1 & 2 已完成）
- [VERSIONING.md](./VERSIONING.md) - 版本管理和发布流程
- [UPSTREAM_PRS.md](./UPSTREAM_PRS.md) - 上游 PR 跟踪
- [FEISHU_SETUP.md](./FEISHU_SETUP.md) - 飞书配置指南
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 项目架构
- [AI_COLLABORATION.md](./AI_COLLABORATION.md) - AI 协作指南

---

## 更新记录

| 日期 | 内容 |
|------|------|
| 2026-02-12 | 添加搜索工具（ddg_search, browser_search, browser_fetch）- **待测试** |
| 2026-02-12 | 系统托盘修复（图标、菜单、GC 问题）|
| 2026-02-12 | 添加辅助脚本（run_desktop.ps1, kill_all.ps1, release.ps1）|
| 2026-02-12 | 应用退出时自动停止 Gateway |
| 2026-02-12 | 版本管理（v0.2.0）和版本显示 |
| 2026-02-12 | Windows 桌面应用 Phase 1 & 2 完成，支持嵌入 Python 打包 |
| 2026-02-12 | 同步上游改进（edit_file、CoT、at 参数、时区）|
| 2026-02-12 | 创建待办事项文档 |
| 2026-02-12 | 添加上游 PR 跟踪文档 |
