# Nanodesk Desktop 开发计划书

> Windows 桌面客户端开发规划
> 
> 版本: 2.0 | 日期: 2026-02-12 | 平台: **Windows 10/11 only**
> 
> 定位：普通用户（非技术背景），降低使用门槛

---

## 1. 项目目标

为普通用户提供一键安装、图形化配置的 Nanodesk 桌面客户端，降低技术门槛。

### 核心功能完成情况

| Phase | 功能 | 状态 | 完成日期 |
|-------|------|------|----------|
| **Phase 1** | 图形化配置向导（首次启动） | ✅ 已完成 | 2026-02-12 |
| **Phase 1** | 系统托盘启动器（启动/停止/状态） | ✅ 已完成 | 2026-02-12 |
| **Phase 1** | 多模型 Provider 配置 | ✅ 已完成 | 2026-02-12 |
| **Phase 1** | 进程管理（Gateway 生命周期） | ✅ 已完成 | 2026-02-12 |
| **Phase 2** | 日志系统（文件轮转 + 查看器） | ✅ 已完成 | 2026-02-12 |
| **Phase 2** | 配置加密（DPAPI） | ✅ 已完成 | 2026-02-12 |
| **Phase 2** | 嵌入 Python 打包 | ✅ 已完成 | 2026-02-12 |
| **Phase 2** | 安装程序（Inno Setup） | ✅ 已完成 | 2026-02-12 |

---

## 2. 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| GUI 框架 | PySide6 6.10.2 | Qt6 绑定，现代化界面，中文支持好 |
| 打包工具 | PyInstaller 6.18.0 | 生成单文件夹 exe |
| 安装程序 | Inno Setup 6.x | 专业 Windows 安装包 |
| 配置加密 | Windows DPAPI | 保护 API Key |
| 进程管理 | QThread + subprocess | 异步管理后台进程（避免 asyncio 冲突） |
| 嵌入 Python | 3.11.9 embed-amd64 | 自包含，无需用户安装 Python |

---

## 3. 项目结构

```
nanodesk/
├── desktop/                    # 桌面应用代码
│   ├── __init__.py
│   ├── main.py                 # 程序入口
│   ├── app.py                  # QApplication 实例
│   ├── windows/
│   │   ├── main_window.py      # 主窗口（托盘 + 状态卡片）
│   │   └── setup_wizard.py     # 配置向导（3步骤）
│   ├── widgets/
│   │   └── __init__.py
│   ├── core/
│   │   ├── config_manager.py   # 配置管理（读写/加密）
│   │   ├── process_manager.py  # Gateway 进程管理（QThread）
│   │   ├── log_handler.py      # 日志系统（轮转 + 查看器）
│   │   └── system_tray.py      # 系统托盘图标
│   └── resources/
│       ├── icons/
│       │   └── logo.ico        # 应用图标
│       └── create_icon.py      # 图标生成脚本
├── scripts/
│   ├── build_all.ps1           # 一键打包脚本
│   ├── build_desktop.ps1       # PyInstaller 构建
│   ├── prepare_embedded_python.py  # 准备嵌入 Python
│   └── setup.iss               # Inno Setup 脚本
└── docs/
    └── BUILD.md                # 构建指南
```

---

## 4. 界面原型

### 4.1 配置向导（已完成）

**Step 1: LLM Provider**
- 支持 DashScope/OpenAI/Ollama
- API Key 输入框（密码显示）
- 模型选择下拉框

**Step 2: 通讯频道**
- 飞书机器人启用/禁用
- App ID / App Secret 输入
- 加密存储凭证

**Step 3: 确认**
- 配置摘要显示
- 保存并启动

### 4.2 主窗口（已完成）

- **状态卡片**: Gateway 状态、Feishu 状态（彩色指示灯）
- **控制按钮**: 启动/停止 Gateway、查看日志、打开设置
- **系统托盘**: 右键菜单（显示/隐藏、启动、停止、退出）

---

## 5. 关键实现

### 5.1 配置加密（DPAPI）

```python
# nanodesk/desktop/core/config_manager.py
import win32crypt

def encrypt_api_key(api_key: str) -> str:
    """使用 Windows DPAPI 加密 API Key"""
    data = api_key.encode('utf-8')
    encrypted = win32crypt.CryptProtectData(data, None, None, None, 0)
    return base64.b64encode(encrypted).decode('utf-8')
```

### 5.2 嵌入 Python 打包

**原理：** 下载 Windows embeddable Python，安装依赖后打包到应用中。

**运行时优先级：**
1. `dist/Nanodesk/python/python.exe`（嵌入 Python）
2. `dist/Nanodesk/_internal/python.exe`（PyInstaller 内部）
3. 系统 Python（开发模式）

**环境变量设置：**
- `PYTHONIOENCODING=utf-8` - 强制 UTF-8 编码
- `PYTHONUTF8=1` - Python 3.7+ UTF-8 模式

### 5.3 进程管理（QThread）

为避免 PyInstaller 打包后的 asyncio 事件循环冲突，使用 QThread 管理子进程：

```python
class GatewaySubprocessThread(QThread):
    log_line = Signal(str)
    finished = Signal(bool, str)
    
    def run(self):
        self._process = subprocess.Popen(
            [python_cmd, "-m", "nanodesk.launcher", "gateway"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env
        )
        # 读取输出...
```

---

## 6. 打包和分发

### 6.1 包大小

| 类型 | 大小 | 说明 |
|------|------|------|
| 解压后 | ~404 MB | 嵌入 Python + 所有依赖 |
| ZIP 压缩 | ~163 MB | 便携版（用户下载）|
| 安装程序 | ~150-160 MB | Inno Setup（预计）|

### 6.2 分发方式

**便携版：**
```powershell
Compress-Archive -Path dist\Nanodesk -DestinationPath Nanodesk-Portable.zip
```

**安装程序：**
```powershell
iscc nanodesk\scripts\setup.iss
```

---

## 7. 已知问题

| 问题 | 状态 | 解决方案 |
|------|------|----------|
| Windows 深色模式显示问题 | ⚠️ 缓解 | 使用 ClassicStyle + 强制浅色调色板 |
| 包体积较大 | ✅ 接受 | 嵌入 Python 导致，功能完整优先 |
| 首次启动较慢 | ✅ 接受 | 嵌入 Python 解压/初始化 |

---

## 8. 后续优化（可选）

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 单文件版 | ⭐ | UPX 压缩，启动更慢但体积更小 |
| 精简依赖 | ⭐⭐ | 移除不需要的 channel SDK |
| 自动更新 | ⭐⭐ | 检查 GitHub Releases 更新 |
| 多语言 | ⭐ | 英文界面支持 |

---

## 9. 参考文档

- [BUILD.md](./BUILD.md) - 完整构建指南
- [README.md](../README.md) - 项目总览

---

**状态**: ✅ Phase 1 & 2 已完成 | **最后更新**: 2026-02-12
