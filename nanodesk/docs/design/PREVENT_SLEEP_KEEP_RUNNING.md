# 屏幕关闭但保持运行 - 简化版设计

> 实现 Windows 下屏幕可关闭，但 Nanodesk Agent 继续运行的功能

**提案状态**: 📝 待实现  
**优先级**: 高  
**预计时间**: 0.5 天  
**设计状态**: ✅ 已定稿  

---

## 核心原则

**插电 + Gateway 运行 = 阻止睡眠，其他情况 = 允许睡眠**

保护笔记本电池，接电时才保持运行。

---

## 用户场景

```
场景 A: 台式机 / 笔记本插电
      ↓
操作: 启动 Gateway，关闭显示器
      ↓
结果: ✅ 接电中，阻止睡眠，Agent 继续运行

场景 B: 笔记本用电池
      ↓
操作: 启动 Gateway
      ↓
结果: ⚠️ 提示用户"未接电，不阻止睡眠"
      ↓
用户: 插上电源或继续（此时关屏会睡眠）
```

---

## 技术方案

### Windows API

```c
ES_CONTINUOUS | ES_SYSTEM_REQUIRED    // 阻止睡眠，但允许关屏
```

- `ES_SYSTEM_REQUIRED` - 保持系统运行 ✓
- `ES_DISPLAY_REQUIRED` - 保持屏幕开启 ✗（不需要）

### 实现（极简）

```python
# nanodesk/desktop/core/power_manager.py
"""Windows 电源管理 - 插电时才阻止睡眠"""

import ctypes
import atexit
import threading
from dataclasses import dataclass
from loguru import logger

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


@dataclass
class PowerStatus:
    """电源状态"""
    on_ac_power: bool      # 是否接交流电源（插电）
    battery_percent: int   # 电量百分比（0-100，台式机为100）


# ctypes 结构体定义（模块级别，避免重复定义）
class _SYSTEM_POWER_STATUS(ctypes.Structure):
    """Windows SYSTEM_POWER_STATUS 结构体"""
    _fields_ = [
        ("ACLineStatus", ctypes.c_ubyte),
        ("BatteryFlag", ctypes.c_ubyte),
        ("BatteryLifePercent", ctypes.c_ubyte),
        ("Reserved1", ctypes.c_ubyte),
        ("BatteryLifeTime", ctypes.c_ulong),
        ("BatteryFullLifeTime", ctypes.c_ulong),
    ]


# 全局状态
_last_ac_status: bool | None = None
_is_preventing: bool = False
_monitor_started: bool = False
_lock = threading.Lock()


def get_power_status() -> PowerStatus:
    """获取当前电源状态"""
    try:
        status = _SYSTEM_POWER_STATUS()
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(status)):
            on_ac = status.ACLineStatus == 1
            battery = status.BatteryLifePercent if status.BatteryLifePercent <= 100 else 100
            return PowerStatus(on_ac_power=on_ac, battery_percent=battery)
    except Exception as e:
        logger.warning(f"[Power] 获取电源状态失败: {e}")
    
    # 默认按插电处理（保守策略）
    return PowerStatus(on_ac_power=True, battery_percent=100)


def should_prevent_sleep() -> tuple[bool, str]:
    """
    判断是否应阻止睡眠
    
    Returns:
        (是否阻止, 原因说明)
    """
    status = get_power_status()
    
    if not status.on_ac_power:
        return False, f"未接电源（电量 {status.battery_percent}%），不阻止睡眠以保护电池"
    
    return True, f"已接电源，阻止睡眠以维持 Gateway 运行"


def prevent_sleep() -> bool:
    """
    尝试阻止系统睡眠（线程安全）
    
    Returns:
        是否成功阻止
    """
    global _is_preventing
    
    should_prevent, reason = should_prevent_sleep()
    
    with _lock:
        if not should_prevent:
            if _is_preventing:
                # 之前阻止了，现在需要恢复
                allow_sleep()
            else:
                logger.info(f"[Power] {reason}")
            return False
        
        if _is_preventing:
            # 已经在阻止，无需重复
            return True
        
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            )
            _is_preventing = True
            logger.info(f"[Power] {reason}")
            return True
        except Exception as e:
            logger.error(f"[Power] 阻止睡眠失败: {e}")
            return False


def allow_sleep():
    """恢复系统睡眠（线程安全）"""
    global _is_preventing
    
    with _lock:
        if not _is_preventing:
            return
        
        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            _is_preventing = False
            logger.info("[Power] 已恢复系统睡眠")
        except Exception as e:
            logger.error(f"[Power] 恢复睡眠失败: {e}")


def check_power_change():
    """
    检查电源状态变化，自动调整睡眠设置
    由定时器每 5 分钟调用一次
    
    注意：锁外调用 prevent_sleep/allow_sleep，避免死锁
    """
    global _last_ac_status
    
    status = get_power_status()
    current_ac = status.on_ac_power
    should_update = False
    
    with _lock:
        # 首次运行，记录状态
        if _last_ac_status is None:
            _last_ac_status = current_ac
            return
        
        # 状态变化
        if current_ac != _last_ac_status:
            should_update = True
            _last_ac_status = current_ac
    
    # 锁外执行，避免死锁
    if should_update:
        if current_ac:
            # 从电池变为插电
            logger.info("[Power] 检测到电源接入，自动阻止睡眠")
            prevent_sleep()
        else:
            # 从插电变为电池
            logger.warning(f"[Power] 检测到电源断开（电量 {status.battery_percent}%），自动恢复睡眠")
            allow_sleep()


def start_power_monitor(interval_seconds: int = 300):
    """
    启动电源监控
    
    Args:
        interval_seconds: 检查间隔（秒），默认 5 分钟，测试时可设为 5
    """
    global _monitor_started, _last_ac_status
    
    with _lock:
        if _monitor_started:
            logger.debug("[Power] 电源监控已在运行，跳过")
            return
        _monitor_started = True
        _last_ac_status = None  # 重置状态，强制重新检测
    
    def monitor_loop():
        while True:
            threading.Event().wait(interval_seconds)
            check_power_change()
    
    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info(f"[Power] 电源监控已启动（每 {interval_seconds} 秒检查）")


# 确保退出时恢复睡眠
def _cleanup():
    """退出清理"""
    with _lock:
        if _is_preventing:
            logger.info("[Power] 程序退出，恢复系统睡眠")
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            except:
                pass

atexit.register(_cleanup)
```

---

## 集成点

### 1. Desktop 启动 Gateway 时

```python
# nanodesk/desktop/windows/main_window.py

from nanodesk.desktop.core.power_manager import prevent_sleep, allow_sleep

class MainWindow(QMainWindow):
    
    def start_gateway(self):
        """启动 Gateway 时根据电源状态决定是否阻止睡眠"""
        # ... 启动代码 ...
        
        from nanodesk.desktop.core.power_manager import should_prevent_sleep, start_power_monitor
        
        # 启动电源监控
        start_power_monitor()
        
        should_prevent, reason = should_prevent_sleep()
        
        if should_prevent:
            prevent_sleep()
            self.tray_icon.showMessage(
                "Nanodesk",
                "🟢 Gateway 已启动\n已接电源，可关闭屏幕保持运行",
                QSystemTrayIcon.Information,
                5000
            )
        else:
            self.tray_icon.showMessage(
                "Nanodesk",
                f"⚠️ Gateway 已启动\n{reason}",
                QSystemTrayIcon.Warning,
                5000
            )
    
    def stop_gateway(self):
        """停止 Gateway 时恢复睡眠"""
        # ... 停止代码 ...
        
        allow_sleep()
        
        self.tray_icon.showMessage(
            "Nanodesk",
            "🔴 Gateway 已停止\n电脑将正常进入睡眠",
            QSystemTrayIcon.Information,
            3000
        )
```

### 2. Gateway 子进程自身（保险机制）

```python
# nanodesk/bootstrap.py

def _is_gateway_mode() -> bool:
    """检测是否在 Gateway 模式下运行"""
    import sys
    return "gateway" in sys.argv

def inject():
    # ... 现有注入代码 ...
    
    # 确保只有一个 Gateway 实例（防止多开冲突）
def _ensure_single_gateway():
    """使用 socket 端口锁确保单实例"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 28790))  # Gateway 专用端口
        sock.listen(1)
        return sock  # 保持引用，进程退出自动释放
    except socket.error:
        print("Gateway 已在运行")
        import sys
        sys.exit(1)

def inject():
    # ... 现有注入代码 ...
    
    if _is_gateway_mode():
        # 1. 先确保单实例（防止多开冲突）
        _gateway_lock = _ensure_single_gateway()
        
        # 2. 然后启动电源管理
        if sys.platform == "win32":
            from nanodesk.desktop.core.power_manager import prevent_sleep, start_power_monitor
            prevent_sleep()
            start_power_monitor()  # 启动电源监控轮询
```

---

## 文件变更

| 文件 | 操作 | 说明 |
|------|------|------|
| `nanodesk/desktop/core/power_manager.py` | 新增 | 电源检测 + 睡眠控制 |
| `nanodesk/desktop/windows/main_window.py` | 修改 | 根据电源状态显示不同提示 |
| `nanodesk/bootstrap.py` | 修改 | Gateway 模式检测 + 单实例锁 + 电源管理 |

---

## 验证测试

### 手动验证步骤

#### 测试 A: 插电模式
```powershell
# 1. 确保电脑接电源
# 2. 启动 Gateway
# 观察日志: [Power] 已接电源，阻止睡眠以维持 Gateway 运行

# 3. 检查系统状态
powercfg /requests
# 应显示: [PROCESS] \Device\...\python.exe

# 4. 关闭显示器，Agent 继续运行 ✓
```

#### 测试 B: 电池模式
```powershell
# 1. 拔掉电源（笔记本）
# 2. 启动 Gateway
# 观察日志: [Power] 未接电源（电量 XX%），不阻止睡眠以保护电池
# 托盘提示: ⚠️ 未接电源...

# 3. 检查系统状态
powercfg /requests
# 应无任何阻止请求

# 4. 关屏后电脑会正常睡眠 ✓
```

---

## 边界情况处理

| 情况 | 行为 |
|------|------|
| 程序崩溃 | atexit 确保恢复睡眠（最佳努力） |
| 强制杀进程 | 可能无法恢复，下次启动自动重置 |
| 多开 Gateway | ✅ **单实例锁阻止**，端口 28790 占用（多配置需求暂不支持） |
| 运行中拔掉电源 | ✅ 自动检测（5分钟轮询），恢复睡眠 |
| 运行中插上电源 | ✅ 自动检测，阻止睡眠 |
| 系统强制睡眠 | Windows 会覆盖 API，无法阻止 |

---

## 设计决策记录

| 考虑点 | 决策 | 原因 |
|--------|------|------|
| 是否需要配置项？ | ❌ 否 | 插电自动阻止，拔电自动允许 |
| 是否需要设置面板？ | ❌ 否 | 无需用户干预 |
| 是否需要手动开关？ | ❌ 否 | 插电即阻止，拔电即允许 |
| 是否检测 CronJob？ | ❌ 否 | Gateway 运行时检测即可 |
| 是否区分电源/电池？ | ✅ 是 | 保护笔记本电池 |
| 是否支持多配置？ | ❌ 否 | 当前架构不支持，单实例足够 |
| 单实例实现方式 | ✅ Socket 端口锁 | 简单可靠，跨进程有效 |

---

## 与原版设计的差异

| 原版 | 当前简化版 |
|------|-----------|
| PowerManager 类 + 单例 | 函数 + 电源检测 |
| 配置项 `prevent_sleep`, `allow_screen_off` | 无配置，自动判断 |
| 设置面板集成 | 无设置面板 |
| 托盘菜单开关 | 无手动开关 |
| 电池模式检测 | ✅ **插电检测** |
| CronJob 检测 | 不检测 |
| 5 个 Phase（5天） | **1 个 Phase（0.5天）** |

---

## 下一步

- [ ] 实现 `power_manager.py`
- [ ] 修改 `main_window.py` 集成
- [ ] 修改 `bootstrap.py` 检测
- [ ] 本地测试验证
