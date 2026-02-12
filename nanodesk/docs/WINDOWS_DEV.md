# Windows 开发指南

Nanodesk 针对 Windows + VS Code + Kimi Code 环境优化。

## 环境要求

- Windows 10/11
- Python 3.11+
- VS Code + Kimi Code 插件
- Git for Windows

## 快速开始

### 1. 初始化开发环境

```powershell
# 打开 PowerShell（在项目根目录）
.\nanodesk\scripts\init-venv.ps1
```

这会创建 `.venv` 虚拟环境并安装依赖。

### 2. VS Code 配置

VS Code 会自动加载 `.vscode/` 配置：
- 推荐扩展已配置
- 调试配置（F5 直接启动）
- 格式化保存（Ruff）

### 3. 运行项目

**方式 1：VS Code 调试（推荐）**
- `Ctrl+Shift+D` 打开调试面板
- 选择 "Nanodesk Agent" 或 "Nanodesk Gateway"
- 按 `F5` 启动

**方式 2：终端**
```powershell
.venv\Scripts\Activate.ps1
nanodesk agent
```

## Windows 特定功能

### PowerShell 脚本

| 脚本 | 用途 |
|------|------|
| `init-venv.ps1` | 初始化虚拟环境 |
| `sync-upstream.ps1` | 同步上游代码 |
| `extract-contrib.ps1` | 提取贡献提交 |

### 路径处理

始终使用 `pathlib`：
```python
from pathlib import Path

# 配置目录
config_dir = Path.home() / ".nanobot"
config_file = config_dir / "config.json"

# 工作空间
workspace = Path("workspace").resolve()
```

## 调试技巧

### VS Code 断点调试

1. 在代码行左侧点击设置断点
2. 按 `F5` 启动调试
3. 使用调试面板查看变量、调用栈

### 查看日志

```powershell
# 运行时查看日志
nanodesk agent --logs

# 详细模式
nanodesk gateway --verbose
```

### 常见问题

**问题：PowerShell 执行策略阻止脚本**
```powershell
# 以管理员身份运行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**问题：路径包含空格**
```powershell
# 使用引号包裹路径
& ".venv\Scripts\python.exe" "nanodesk\launcher.py"
```

## 跨平台注意事项

### 避免 Windows 独占代码

如果功能要贡献给上游，避免：
- `win32api` 等 Windows 专属库
- 硬编码 `C:\` 路径
- PowerShell 脚本（没有等效的 bash）

### 推荐做法

```python
# ✅ 跨平台
import platform
if platform.system() == "Windows":
    # Windows 特定代码
    pass
else:
    # Unix/Mac 代码
    pass
```

## Kimi Code 集成

Kimi Code 会读取 `.kimi/prompts.md` 获取项目上下文。

提示 Kimi 时注意：
- Windows 功能 → `nanodesk/`
- 跨平台功能 → 评估贡献给 `nanobot/`
- VS Code 配置 → `.vscode/`

## 文件模板

### 新建 Windows 工具

```python
# nanodesk/tools/windows_tool.py
from pathlib import Path
import platform
from nanobot.agent.tools.base import Tool

class WindowsTool(Tool):
    @property
    def name(self) -> str:
        return "windows_tool"
    
    @property
    def description(self) -> str:
        return "Windows specific tool"
    
    async def execute(self, **kwargs) -> str:
        if platform.system() != "Windows":
            return "Error: This tool only works on Windows"
        
        # Windows specific code
        return "Done"
```

## VS Code + Kimi Code 开发工作流

### 1. 首次打开项目

```powershell
# 在项目根目录执行
code .
```

VS Code 会自动提示安装推荐扩展，点击"安装全部"：
- **Python** + **Pylance** - Python 语言支持
- **Ruff** - 代码格式化和检查
- **Debugpy** - 调试支持
- **Even Better TOML** - 配置文件编辑
- **Kimi Code** - AI 编程助手

### 2. 启动调试（F5）

**方式一：调试面板（推荐开发）**

```
Ctrl+Shift+D  # 打开调试面板
```

选择配置：
- **Nanodesk Agent** - 交互式聊天模式
- **Nanodesk Gateway** - 后台网关服务
- **Nanodesk Onboard** - 初始化配置向导
- **Current File** - 调试当前 Python 文件

按 `F5` 启动，会自动：
1. 激活虚拟环境 (`.venv\Scripts\python.exe`)
2. 加载 `nanodesk.bootstrap` 注入定制
3. 在集成终端运行

**方式二：终端运行（快速测试）**

```powershell
Ctrl+`  # 打开集成终端（自动进入项目目录）

# 虚拟环境已自动配置，直接运行
nanodesk agent
# 或
python -m nanodesk agent
```

### 3. 代码编写与格式化

保存文件时 **自动执行**：
- Ruff 格式化（行长度 100）
- 自动导入排序
- 基础类型检查

**手动格式化**：
```powershell
# 检查问题
ruff check .

# 自动修复
ruff check . --fix

# 格式化
ruff format .
```

### 4. 与 Kimi Code 配合

#### 刷新项目上下文

新会话或项目结构变更时：
```
Ctrl+Shift+P → Kimi: Init Context
# 或输入 /init
```

Kimi 会读取：
- `.kimi/prompts.md` - 项目特定提示词
- `nanodesk/docs/AI_COLLABORATION.md` - AI 协作指南和代码归属决策
- `AGENTS.md` - 项目结构

#### 常用 Kimi 指令

| 指令 | 用途 |
|------|------|
| `/init` | 刷新项目上下文 |
| `/fix` | 修复当前文件问题 |
| `/test` | 为选中代码生成测试 |
| 选中代码 + 右键"Explain" | 解释代码 |

#### 开发新功能示例

**步骤 1**：新建文件 `nanodesk/tools/screenshot.py`

**步骤 2**：告诉 Kimi 需求：
```
帮我在这个文件创建一个 Windows 截图工具：
- 继承自 Tool 基类
- 使用 PIL/Pillow 截图
- 保存到工作目录
- 返回文件路径
```

**步骤 3**：保存文件（Ruff 自动格式化）

**步骤 4**：注册到 `bootstrap.py`：
```python
from nanodesk.tools.screenshot import ScreenshotTool
ToolRegistry.register(ScreenshotTool())
```

**步骤 5**：`F5` 启动调试测试

### 5. 调试技巧

#### 设置断点

```python
# 代码中插入断点
import pdb; pdb.set_trace()

# 或 VS Code 行号左侧点击红点
```

#### 调试快捷键

| 快捷键 | 功能 |
|--------|------|
| `F5` | 启动/继续 |
| `F10` | 单步跳过 |
| `F11` | 单步进入 |
| `Shift+F11` | 单步跳出 |
| `F9` | 切换断点 |
| `Ctrl+Shift+F5` | 重新启动 |
| `Shift+F5` | 停止 |

#### 查看调试信息

调试时左侧面板显示：
- **变量** - 本地和全局变量
- **调用栈** - 函数调用链
- **监视** - 自定义表达式
- **断点** - 所有断点列表

### 6. 文件导航快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+P` | 快速打开文件 |
| `Ctrl+Shift+F` | 全局搜索（自动排除 .venv） |
| `Ctrl+Shift+O` | 跳到符号（函数/类） |
| `F12` | 跳转到定义 |
| `Alt+F12` | 速览定义（不跳转） |
| `Ctrl+Shift+P` | 命令面板 |

### 7. 推荐布局

```
┌─────────────┬─────────────┐
│   资源管理器  │    编辑器    │
│  (文件树)    │   (代码)    │
│             │             │
├─────────────┤             │
│   大纲/调试  │             │
│  (变量/调用栈)│             │
└─────────────┴─────────────┘
        终端 (底部)
```

切换布局：`Ctrl+Shift+P` → "视图: 切换外观"

### 8. 关键文件快速访问

| 文件 | 用途 | 快速打开 |
|------|------|---------|
| `nanodesk/bootstrap.py` | 注册工具/频道 | `Ctrl+P` → bootstrap |
| `nanodesk/launcher.py` | 启动入口 | `Ctrl+P` → launcher |
| `pyproject.toml` | 依赖配置 | `Ctrl+P` → pyproject |
| `~/.nanobot/config.json` | 运行配置 | 外部文件 |
| `nanodesk/docs/AI_COLLABORATION.md` | AI 协作指南 | `Ctrl+P` → AI_COLL |

### 9. 常见问题

**Q: 终端提示 "无法加载虚拟环境"**
```powershell
# 手动激活
.venv\Scripts\Activate.ps1

# 或修改 PowerShell 执行策略（管理员）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: 调试报错 "ModuleNotFoundError"**
```powershell
# 确保安装了 editable 模式
pip install -e .
```

**Q: Ruff 格式化不符合预期**
```json
// 检查 .vscode/settings.json 配置
"editor.defaultFormatter": "charliermarsh.ruff",
"editor.formatOnSave": true
```

**Q: Kimi 不了解项目结构**
```
1. 使用 /init 刷新上下文
2. 或手动打开 nanodesk/docs/AI_COLLABORATION.md 让 Kimi 阅读
3. 确保 .kimi/prompts.md 已提交到 git
```

**Q: 如何调试自定义工具？**
```python
# 在工具代码中设置断点
async def execute(self, **kwargs) -> str:
    import pdb; pdb.set_trace()  # 断点
    # ... 你的代码
```

## 参考

- [Python on Windows](https://docs.python.org/3/using/windows.html)
- [VS Code Python](https://code.visualstudio.com/docs/python/python-tutorial)
- [PowerShell 执行策略](https://docs.microsoft.com/powershell/module/microsoft.powershell.security/set-executionpolicy)
- [VS Code 调试](https://code.visualstudio.com/docs/python/debugging)
