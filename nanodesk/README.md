# Nanodesk

> 🔀 默认分支：`nanodesk`（工作分支）| 如需贡献代码，请切换到 `main` 分支

个人定制版 nanobot，专为本地桌面端场景优化。

## 简介

Nanodesk 基于 [nanobot](https://github.com/HKUDS/nanobot) 构建，保留了原项目的轻量架构（~4,000 行代码），同时添加个人定制功能：

- ✅ **Windows 桌面应用** - 图形化配置向导，一键启动，系统托盘管理
- 本地桌面工具集成（截图、文件管理...）
- 自定义频道适配
- 个人工作流技能

## 快速开始

### 方式一：Windows 桌面版（推荐）

#### 选项 A：自行打包（推荐）

克隆代码后一键打包，解压即用，无需安装 Python！

```powershell
# 克隆仓库
git clone https://github.com/jswxharry/Nanodesk.git
cd Nanodesk

# 一键打包（包含嵌入 Python）
.\nanodesk\scripts\build_all.ps1 -Clean

# 输出：dist/Nanodesk/ 文件夹
```

**使用步骤：**
1. 打包完成后，进入 `dist/Nanodesk/` 文件夹
2. 运行 `Nanodesk.exe`
3. 首次启动会自动弹出配置向导
4. 配置完成后点击「启动 Gateway」即可使用

#### 选项 B：直接运行（开发者）

如果你有 Python 环境，可以直接运行桌面版：

```powershell
pip install -e .
python -m nanodesk.desktop.main
```

### 方式二：命令行版（开发者）

```bash
# 安装
pip install -e .

# 启动（自动加载你的定制）
nanodesk agent

# 或查看帮助
nanodesk --help
```

## 项目结构

```
nanodesk/
├── __init__.py          # 模块标识
├── bootstrap.py         # 启动注入逻辑
├── launcher.py          # CLI 入口
├── desktop/             # Windows 桌面应用
│   ├── main.py          # GUI 入口
│   ├── windows/         # 窗口组件
│   │   ├── main_window.py    # 主窗口 + 系统托盘
│   │   └── setup_wizard.py   # 配置向导
│   ├── core/            # 核心功能
│   │   ├── config_manager.py  # 配置管理（含加密）
│   │   ├── process_manager.py # Gateway 进程管理
│   │   └── log_handler.py     # 日志系统
│   └── resources/       # 图标等资源
├── channels/            # 你的自定义频道
├── tools/               # 你的自定义工具
├── skills/              # 你的自定义技能
├── providers/           # 你的 LLM 适配
├── patches/             # 必要时的核心补丁
├── scripts/             # 辅助脚本
│   ├── build_all.ps1    # 一键打包桌面版
│   └── prepare_embedded_python.py  # 准备嵌入 Python
└── docs/                # 文档
```

## 桌面应用开发

### 构建桌面版

**一键构建（推荐）：**
```powershell
.\nanodesk\scripts\build_all.ps1 -Clean
```

**输出：**
- `dist/Nanodesk/` - 便携版文件夹
- `dist/Nanodesk-Setup-x.x.x.exe` - 安装程序（需 Inno Setup）

**手动构建：**
```powershell
# 步骤1：准备嵌入 Python（只需一次）
python .\nanodesk\scripts\prepare_embedded_python.py

# 步骤2：构建桌面应用
.\nanodesk\scripts\build_desktop.ps1

# 步骤3：创建安装程序（可选）
iscc .\nanodesk\scripts\setup.iss
```

详见：[BUILD.md](./docs/BUILD.md)

### 添加自定义工具

```python
# nanodesk/tools/my_tool.py
from nanobot.agent.tools.base import Tool

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "描述你的工具"
    
    async def execute(self, **kwargs) -> str:
        return "执行结果"
```

然后在 `bootstrap.py` 中注册：

```python
from nanodesk.tools.my_tool import MyTool
from nanobot.agent.tools.registry import ToolRegistry

ToolRegistry.register(MyTool())
```

### 内置自定义工具（Nanodesk）

> ⚠️ **状态：已添加，待测试**

| 工具 | 说明 | 状态 |
|------|------|------|
| `ddg_search` | DuckDuckGo 搜索（无需 API Key）| 🧪 待测试 |
| `browser_search` | 浏览器搜索（Playwright）| 🧪 待测试 |
| `browser_fetch` | 浏览器页面抓取（支持 JS 渲染）| 🧪 待测试 |

**使用方法：**
```python
# DuckDuckGo 搜索（快速，无需 API Key）
ddg_search, query="最新 AI 新闻", count=5

# 浏览器搜索（支持 JS，较慢）
browser_search, query="Python 教程", engine="google"

# 浏览器抓取动态页面
browser_fetch, url="https://spa-app.example.com"
```

**安装依赖：**
```bash
pip install duckduckgo-search playwright
playwright install chromium
```

### 同步上游更新

```bash
# 拉取最新 nanobot 代码
.\nanodesk\scripts\sync-upstream.ps1
```

### 给原库提 PR

如果你在开发中发现可以贡献给原库的改进：

```bash
# 从 nanodesk 分支提取干净提交
.\nanodesk\scripts\extract-contrib.sh <commit-hash>
```

然后到 GitHub 创建 PR 到 `HKUDS/nanobot`。

## 分支策略

| 分支 | 用途 |
|------|------|
| `main` | 跟踪上游，用于提 PR，不直接开发 |
| `nanodesk` | 主工作分支，包含你的所有定制 |

## 已验证功能

### 通讯频道

| 频道 | 状态 | 文档 |
|------|------|------|
| 飞书 (Feishu) | ✅ 已验证 | [配置指南](./docs/FEISHU_SETUP.md) |

### 桌面应用功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 图形化配置向导 | ✅ 已完成 | 首次启动自动配置 Provider 和 Channel |
| 系统托盘管理 | ✅ 已完成 | 启动/停止 Gateway，查看状态 |
| 日志查看器 | ✅ 已完成 | 实时查看 Gateway 日志 |
| 配置加密 | ✅ 已完成 | DPAPI 加密保护 API Key |
| 便携版打包 | ✅ 已完成 | 无需 Python 环境，解压即用 |
| 安装程序 | ✅ 已完成 | Inno Setup 制作专业安装包 |

### 开发工具

| 功能 | 状态 | 说明 |
|------|------|------|
| 上游同步脚本 | ✅ 已验证 | `./scripts/sync-upstream.ps1` 或 `.sh` |
| VS Code 调试 | ✅ 已验证 | F5 直接启动调试 |
| 代码格式化 | ✅ 已验证 | Ruff 自动格式化 |
| 桌面版构建 | ✅ 已验证 | PowerShell 脚本一键打包 |

## 文档

- [桌面应用构建指南](./docs/BUILD.md) - 桌面版打包和分发完整指南
- [桌面应用开发计划](./docs/DESKTOP_APP_PLAN.md) - Phase 1/2 开发规划（已完成）
- [版本管理](./docs/VERSIONING.md) - 版本号管理和发布流程
- [架构设计](./docs/ARCHITECTURE.md) - 项目结构和 Git 工作流
- [AI 协作指南](./docs/AI_COLLABORATION.md) - Git 工作流和提交规范
- [飞书配置](./docs/FEISHU_SETUP.md) - 飞书机器人完整配置指南
- [上游同步](./docs/SYNC_WORKFLOW.md) - 同步上游更新流程
- [语言策略](./docs/LANGUAGE_POLICY.md) - 代码注释语言规范
- [Windows 开发](./docs/WINDOWS_DEV.md) - Windows 环境开发指南
- [配置指南](./docs/CONFIGURATION.md) - 初始化配置说明
- [待办事项](./docs/TODO.md) - 功能跟踪和开发计划

## 更新记录

| 日期 | 版本 | 内容 |
|------|------|------|
| 2026-02-12 | v0.2.1 | 同步上游更新：交织链式思考、Cron 一次性任务、子代理增强 |
| 2026-02-12 | v0.2.0 | Windows 桌面应用完成，支持嵌入 Python 打包 |
| 2026-02-10 | v0.1.0 | 飞书通道验证完成，基础架构搭建 |

### 上游同步详情

**2026-02-12 同步** - 合并 [nanobot](https://github.com/HKUDS/nanobot) 上游 6 个提交：

| PR | 功能 | 说明 |
|----|------|------|
| #538 | 交织链式思考 | 工具调用后自动反思，提升 Agent 推理能力 |
| #533 | Cron 一次性任务 | 支持 `at` 参数设置 ISO 格式时间，定时执行后自动删除 |
| #543 | 子代理增强 | 新增 edit_file 工具、时间上下文、技能目录提示 |

## License

MIT License（继承自 nanobot）
