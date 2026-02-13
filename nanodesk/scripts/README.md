# Nanodesk 脚本目录

> 辅助脚本按功能分类存放

---

## 目录结构

```
scripts/
├── build/           # 构建打包脚本
│   ├── build_all.ps1              # 一键完整构建（推荐）
│   ├── build_desktop.ps1          # PyInstaller 构建
│   ├── build_desktop_with_deps.ps1 # 带依赖构建
│   ├── prepare_embedded_python.py # 准备嵌入 Python
│   ├── setup.iss                  # Inno Setup 安装程序
│   ├── install_deps.bat           # 依赖安装
│   └── test_embedded.ps1          # 嵌入环境测试
│
├── dev/             # 开发辅助脚本
│   ├── run_desktop.ps1            # 启动桌面应用（开发模式）
│   ├── run_tests.ps1              # 完整测试套件
│   ├── run_tests_quick.ps1        # 快速测试（CI/CD）
│   ├── kill_all.ps1               # 结束所有进程
│   └── init-venv.ps1              # 初始化虚拟环境
│
├── git/             # Git 工作流脚本
│   ├── sync-upstream.ps1          # 同步上游（PowerShell）
│   ├── sync-upstream.sh           # 同步上游（Bash）
│   ├── extract-contrib.ps1        # 提取贡献代码（PowerShell）
│   └── extract-contrib.sh         # 提取贡献代码（Bash）
│
└── release/         # 发布管理脚本
    └── release.ps1                # 版本发布
```

---

## 快速参考

| 场景 | 命令 |
|------|------|
| **完整构建** | ` .\nanodesk\scripts\build\build_all.ps1 -Clean` |
| **运行测试** | ` .\nanodesk\scripts\dev\run_tests.ps1` |
| **快速测试** | ` .\nanodesk\scripts\dev\run_tests_quick.ps1` |
| **同步上游** | ` .\nanodesk\scripts\git\sync-upstream.ps1` |
| **版本发布** | ` .\nanodesk\scripts\release\release.ps1` |

---

## 使用说明

### PowerShell 执行策略

首次使用 PowerShell 脚本前，可能需要设置执行策略：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 参数说明

大部分脚本支持 `-Help` 或 `-?` 查看详细用法：

```powershell
.\nanodesk\scripts\build\build_all.ps1 -?
```
