# Nanodesk Desktop 开发计划书

> ⚠️ **本文档为历史归档**
> 
> Windows 桌面客户端开发已于 **2026-02-12** 全部完成。
> 
> 当前文档仅保留技术栈和项目结构参考。

---

## 技术栈参考

| 层级 | 技术 | 说明 |
|------|------|------|
| GUI 框架 | PySide6 6.10.2 | Qt6 绑定，现代化界面 |
| 打包工具 | PyInstaller 6.18.0 | 生成单文件夹 exe |
| 安装程序 | Inno Setup 6.x | 专业 Windows 安装包 |
| 配置加密 | Windows DPAPI | 保护 API Key |
| 嵌入 Python | 3.11.9 embed-amd64 | 自包含运行环境 |

---

## 项目结构

```
nanodesk/desktop/
├── main.py                 # 程序入口
├── windows/
│   ├── main_window.py      # 主窗口 + 系统托盘
│   └── setup_wizard.py     # 配置向导
├── core/
│   ├── config_manager.py   # 配置管理（加密）
│   ├── process_manager.py  # Gateway 进程管理
│   └── log_handler.py      # 日志系统
└── resources/              # 图标等资源
```

---

## 构建指南

详见 [BUILD.md](./BUILD.md)

```powershell
# 一键打包
.\nanodesk\scripts\build_all.ps1 -Clean
```

---

## 历史完成记录

| Phase | 功能 | 状态 | 完成日期 |
|-------|------|------|----------|
| Phase 1 | 图形化配置向导 | ✅ 已完成 | 2026-02-12 |
| Phase 1 | 系统托盘启动器 | ✅ 已完成 | 2026-02-12 |
| Phase 1 | 多模型 Provider 配置 | ✅ 已完成 | 2026-02-12 |
| Phase 2 | 日志系统 | ✅ 已完成 | 2026-02-12 |
| Phase 2 | 配置加密（DPAPI）| ✅ 已完成 | 2026-02-12 |
| Phase 2 | 嵌入 Python 打包 | ✅ 已完成 | 2026-02-12 |
| Phase 2 | Inno Setup 安装程序 | ✅ 已完成 | 2026-02-12 |
