"""Windows 电源管理 - 插电时才阻止睡眠

Gateway 运行时保持系统活跃，但允许关闭显示器。
只在接电源时阻止睡眠，保护笔记本电池。
"""

import atexit
import ctypes
import threading
from dataclasses import dataclass
from loguru import logger

ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001


@dataclass
class PowerStatus:
    """电源状态"""
    on_ac_power: bool  # 是否接交流电源（插电）
    battery_percent: int  # 电量百分比（0-100，台式机为100）


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
            battery = (
                status.BatteryLifePercent
                if status.BatteryLifePercent <= 100
                else 100
            )
            return PowerStatus(on_ac_power=on_ac, battery_percent=battery)
    except Exception as e:
        logger.warning(f"[Power] Failed to get power status: {e}")

    # Default to AC power (conservative strategy)
    return PowerStatus(on_ac_power=True, battery_percent=100)


def should_prevent_sleep() -> tuple[bool, str]:
    """
    判断是否应阻止睡眠

    Returns:
        (是否阻止, 原因说明)
    """
    status = get_power_status()

    if not status.on_ac_power:
        return (
            False,
            f"On battery ({status.battery_percent}%), allowing sleep to protect battery",
        )

    return True, "On AC power, preventing sleep to keep Gateway running"


def prevent_sleep() -> bool:
    """
    Try to prevent system sleep (thread-safe)

    Returns:
        Whether successfully prevented
    """
    global _is_preventing

    should_prevent, reason = should_prevent_sleep()

    with _lock:
        if not should_prevent:
            if _is_preventing:
                # Was preventing, now need to allow
                allow_sleep()
            else:
                logger.info(f"[Power] {reason}")
            return False

        if _is_preventing:
            # Already preventing, no need to repeat
            return True

        try:
            ctypes.windll.kernel32.SetThreadExecutionState(
                ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            )
            _is_preventing = True
            logger.info(f"[Power] {reason}")
            return True
        except Exception as e:
            logger.error(f"[Power] Failed to prevent sleep: {e}")
            return False


def allow_sleep():
    """Allow system sleep (thread-safe)"""
    global _is_preventing

    with _lock:
        if not _is_preventing:
            return

        try:
            ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            _is_preventing = False
            logger.info("[Power] System sleep allowed")
        except Exception as e:
            logger.error(f"[Power] Failed to allow sleep: {e}")


def check_power_change():
    """
    Check power status change and adjust sleep settings
    Called by timer every 5 minutes

    Note: Call prevent_sleep/allow_sleep outside lock to avoid deadlock
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
            logger.warning(
                f"[Power] 检测到电源断开（电量 {status.battery_percent}%），自动恢复睡眠"
            )
            allow_sleep()


def start_power_monitor(interval_seconds: int = 300):
    """
    Start power monitoring

    Args:
        interval_seconds: Check interval in seconds, default 5 minutes, can be 5 for testing
    """
    global _monitor_started, _last_ac_status

    with _lock:
        if _monitor_started:
            logger.debug("[Power] Power monitor already running, skipping")
            return
        _monitor_started = True
        _last_ac_status = None  # Reset status to force re-detection

    def monitor_loop():
        while True:
            threading.Event().wait(interval_seconds)
            check_power_change()

    thread = threading.Thread(target=monitor_loop, daemon=True)
    thread.start()
    logger.info(f"[Power] Power monitor started (checking every {interval_seconds}s)")


# Ensure sleep is allowed on exit
def _cleanup():
    """Cleanup on exit"""
    with _lock:
        if _is_preventing:
            logger.info("[Power] Application exiting, allowing system sleep")
            try:
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            except Exception:
                pass


atexit.register(_cleanup)
