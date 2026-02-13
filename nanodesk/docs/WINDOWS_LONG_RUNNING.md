# Windows 长时间运行配置指南

> 解决屏幕关闭后 Nanodesk Agent 无法响应的问题

---

## 问题现象

- 屏幕关闭或锁屏后，飞书/Discord 无法联系到 Agent
- 过一段时间后 Agent "假死"，消息无响应
- 必须手动点亮屏幕或重新登录才能恢复

## 根本原因

Windows 电源管理策略会：

1. **屏幕关闭后进入睡眠** - 冻结所有应用
2. **断开网络连接** - 为省电断开 WiFi/以太网
3. **挂起后台进程** - 非活动应用被节流或冻结

---

## 解决方案

### 方案 1: 修改电源计划（推荐，简单）

#### 方法一：控制面板（图形界面）

1. 打开 **控制面板** → **电源选项**
2. 当前计划右侧点击 **更改计划设置**
3. 设置：
   - **关闭显示器**: 从不 或 你希望的时长
   - **使计算机进入睡眠状态**: **从不**
4. 点击 **更改高级电源设置**
5. 展开 **睡眠** → **在此时间后休眠** → 设置为 **从不**
6. 展开 **无线适配器设置** → **节能模式** → 设置为 **最高性能**
7. 确定保存

#### 方法二：命令行（管理员 PowerShell）

```powershell
# 禁止睡眠
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0

# 禁止休眠
powercfg /change hibernate-timeout-ac 0
powercfg /change hibernate-timeout-dc 0

# 关闭显示器但保持运行（单位：分钟，0=从不）
powercfg /change monitor-timeout-ac 10
powercfg /change monitor-timeout-dc 10

# 禁用混合睡眠
powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP HYBRIDSLEEP 0
powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP HYBRIDSLEEP 0

# 应用设置
powercfg /setactive SCHEME_CURRENT
```

> **AC** =  plugged in (插电), **DC** = battery (电池)

---

### 方案 2: 使用任务计划程序（适合服务器场景）

创建计划任务确保 Nanodesk 始终运行：

```powershell
# 创建任务（以当前用户身份，登录即运行）
$action = New-ScheduledTaskAction -Execute "pythonw" -Argument "-m nanodesk.desktop"
$trigger = New-ScheduledTaskTrigger -AtLogon
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "NanodeskAutoStart" -Action $action -Trigger $trigger -Settings $settings -Force
```

**任务设置要点**：
- ✓ **条件** 选项卡 → 取消勾选 "只有在计算机使用交流电源时才启动"
- ✓ **条件** 选项卡 → 取消勾选 "如果计算机改用电池电源，则停止"
- ✓ **设置** 选项卡 → 勾选 "如果任务失败，重新启动间隔"

---

### 方案 3: 阻止系统睡眠（代码层面）

在 `nanodesk/desktop/main.py` 中添加阻止睡眠的功能：

```python
import ctypes
from ctypes import wintypes

# Windows API 常量
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """
    阻止系统进入睡眠状态
    在应用启动时调用
    """
    ctypes.windll.kernel32.SetThreadExecutionState(
        ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
    )
    print("[System] 已阻止系统睡眠")

def allow_sleep():
    """
    恢复系统睡眠（应用退出时调用）
    """
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print("[System] 已恢复系统睡眠")

# 在 MainWindow.__init__ 中调用 prevent_sleep()
# 在 closeEvent 中调用 allow_sleep()
```

**优点**: 不需要用户修改系统设置  
**缺点**: 只在应用运行时有效

---

### 方案 4: 注册为 Windows 服务（高级）

适合无 GUI 的后台模式（gateway only）：

```powershell
# 使用 nssm (Non-Sucking Service Manager)
# 1. 下载 nssm: https://nssm.cc/download
# 2. 安装服务
nssm install NanodeskGateway "C:\Python311\python.exe" "-m nanobot gateway"

# 3. 配置服务
nssm set NanodeskGateway Start SERVICE_AUTO_START
nssm set NanodeskGateway AppStdout C:\logs\nanodesk.log
nssm set NanodeskGateway AppStderr C:\logs\nanodesk_error.log

# 4. 启动服务
net start NanodeskGateway
```

**注意**: 服务模式无法显示 GUI，适合纯 Gateway 场景。

---

## 推荐配置组合

### 场景 A: 个人笔记本（插电使用）

```powershell
# 禁止睡眠但允许关闭屏幕
powercfg /change standby-timeout-ac 0
powercfg /change monitor-timeout-ac 10

# 代码中阻止睡眠
# nanodesk/desktop/main_window.py 添加 SetThreadExecutionState
```

### 场景 B: 专用服务器/台式机

```powershell
# 高性能模式，永不睡眠
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c  # 高性能计划
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```

### 场景 C: 需要省电（笔记本电池）

- 使用方案 3（代码阻止睡眠）
- 允许系统在电池低时睡眠
- 或者使用外部监控服务定期唤醒

---

## 验证配置

### 检查当前电源设置

```powershell
# 查看当前计划的睡眠超时
powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE

# 查看所有设置（保存到文件）
powercfg /query SCHEME_CURRENT > power_settings.txt
notepad power_settings.txt
```

### 测试是否生效

1. 手动关闭屏幕（按显示器电源按钮或 Win+L 锁屏）
2. 等待 5-10 分钟
3. 从另一台设备发送飞书消息
4. 检查 Agent 是否响应

---

## 故障排查

### 现象：设置了从不睡眠，但还是断连

**可能原因**：
1. **Modern Standby (S0 Low Power Idle)** - 新笔记本的"连接待机"
   - 解决: 设备管理器 → 网络适配器 → 电源管理 → 取消 "允许计算机关闭此设备以节约电源"

2. **USB 选择性暂停**
   - 解决: 电源选项 → USB 设置 → USB 选择性暂停 → 已禁用

3. **网卡节能**
   - 解决: 设备管理器 → 网卡 → 高级 → 节能模式 → 关闭

### 现象：远程桌面断开后 Agent 停止

**原因**: Windows 用户会话在 RDP 断开后被挂起

**解决**: 使用 `tscon` 保持会话活跃，或改用服务方式运行

---

## 相关代码修改建议

### 添加系统托盘提示

```python
# nanodesk/desktop/main_window.py

def _show_prevent_sleep_hint(self):
    """首次启动时提示用户配置"""
    self.tray_icon.showMessage(
        "Nanodesk 运行提示",
        "如需长时间运行，请在设置中禁止系统自动睡眠\n"
        "查看文档: nanodesk/docs/WINDOWS_LONG_RUNNING.md",
        QSystemTrayIcon.Information,
        5000
    )
```

### 自动检测电源设置

```python
import subprocess
import re

def check_sleep_settings():
    """检查系统睡眠设置，返回是否需要警告"""
    result = subprocess.run(
        ["powercfg", "/query", "SCHEME_CURRENT", "SUB_SLEEP", "STANDBYIDLE"],
        capture_output=True, text=True
    )
    
    # 解析当前 AC 值
    match = re.search(r"当前交流电源设置索引: (0x[0-9a-f]+)", result.stdout)
    if match:
        value = int(match.group(1), 16)
        if value != 0:  # 非零表示会睡眠
            return False, f"系统将在 {value} 秒后睡眠"
    
    return True, "睡眠已禁用"
```

---

## 参考资源

- [Windows 电源管理文档](https://docs.microsoft.com/en-us/windows/win32/power/power-management-portal)
- [SetThreadExecutionState API](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate)
- [NSSM 服务管理器](https://nssm.cc/)

---

**最后更新**: 2026-02-14
