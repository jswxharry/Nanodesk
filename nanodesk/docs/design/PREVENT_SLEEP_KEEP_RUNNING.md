# 屏幕关闭但保持运行设计提案

> 实现 Windows 下屏幕可关闭，但 Nanodesk Agent 继续运行的功能

**提案状态**: 📝 设计阶段  
**优先级**: 高  
**影响范围**: `nanodesk/desktop/`, `nanobot/agent/`

---

## 目标

### 用户场景

```
用户: 晚上让 Agent 运行，我想关屏幕省电
      ↓
操作: 关闭显示器 / Win+L 锁屏
      ↓
结果: 屏幕黑了，但 Agent 继续运行，飞书消息能正常回复
      ↓
早上: 开屏，看到 Agent 一整晚处理的消息记录
```

### 核心需求

| 功能 | 必须 | 说明 |
|------|------|------|
| 允许关闭屏幕 | ✅ | 显示器节能，延长寿命 |
| 阻止系统睡眠 | ✅ | CPU/网络保持活跃 |
| 自动恢复 | ✅ | 应用退出时恢复系统默认行为 |
| 可配置 | 可选 | 用户可选择是否启用 |

---

## 技术方案

### Windows API: SetThreadExecutionState

```c
// 阻止睡眠但允许关闭屏幕
ES_CONTINUOUS | ES_SYSTEM_REQUIRED        // ✅ 推荐

// 阻止睡眠且阻止关闭屏幕  
ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED  // ❌ 不让关屏
```

**关键区别**:
- `ES_SYSTEM_REQUIRED` - 保持系统运行（必须）
- `ES_DISPLAY_REQUIRED` - 保持屏幕开启（我们**不需要**这个）

### 实现架构

```
┌─────────────────────────────────────────────────────────┐
│                    Nanodesk Desktop                      │
│  ┌─────────────────┐         ┌──────────────────────┐  │
│  │   MainWindow    │         │   PowerManager       │  │
│  │  ┌───────────┐  │         │  ┌────────────────┐  │  │
│  │  │ __init__  │──┼────────>│  │ prevent_sleep()│  │  │
│  │  └───────────┘  │         │  └────────────────┘  │  │
│  │         │       │         │           │          │  │
│  │  ┌──────▼──────┐│         │  ┌────────▼─────────┐│  │
│  │  │ closeEvent  ││────────>│  │ allow_sleep()    ││  │
│  │  └─────────────┘│         │  └──────────────────┘│  │
│  └─────────────────┘         └──────────────────────┘  │
│                              │                          │
│                              ▼                          │
│                    SetThreadExecutionState()            │
└─────────────────────────────────────────────────────────┘
```

---

## 详细设计

### 1. 电源管理模块

```python
# nanodesk/desktop/core/power_manager.py
"""Windows 电源管理，保持后台运行但允许关屏"""

import ctypes
from ctypes import wintypes
from loguru import logger

# Windows API 常量
ES_AWAYMODE_REQUIRED = 0x00000040
ES_CONTINUOUS = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
ES_SYSTEM_REQUIRED = 0x00000001


class PowerManager:
    """
    管理 Windows 电源状态，确保 Agent 在后台持续运行
    
    特性:
    - 阻止系统进入睡眠 (S3/S4)
    - 允许关闭显示器 (不影响 ES_DISPLAY_REQUIRED)
    - 应用退出时自动恢复
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if PowerManager._initialized:
            return
        self._is_preventing = False
        PowerManager._initialized = True
    
    def prevent_sleep(self, allow_screen_off: bool = True) -> bool:
        """
        阻止系统睡眠
        
        Args:
            allow_screen_off: True=允许关闭屏幕, False=保持屏幕开启
        
        Returns:
            是否成功
        """
        try:
            flags = ES_CONTINUOUS | ES_SYSTEM_REQUIRED
            
            if not allow_screen_off:
                flags |= ES_DISPLAY_REQUIRED
                logger.info("[PowerManager] 阻止睡眠 + 保持屏幕开启")
            else:
                logger.info("[PowerManager] 阻止睡眠，允许关闭屏幕")
            
            result = ctypes.windll.kernel32.SetThreadExecutionState(flags)
            
            if result == 0:
                logger.error("[PowerManager] SetThreadExecutionState 调用失败")
                return False
            
            self._is_preventing = True
            return True
            
        except Exception as e:
            logger.error(f"[PowerManager] 阻止睡眠失败: {e}")
            return False
    
    def allow_sleep(self) -> bool:
        """
        恢复系统默认睡眠行为
        应用退出时必须调用
        """
        try:
            result = ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            
            if result == 0:
                logger.error("[PowerManager] 恢复睡眠设置失败")
                return False
            
            self._is_preventing = False
            logger.info("[PowerManager] 已恢复系统睡眠设置")
            return True
            
        except Exception as e:
            logger.error(f"[PowerManager] 恢复睡眠失败: {e}")
            return False
    
    @property
    def is_preventing(self) -> bool:
        """当前是否正在阻止睡眠"""
        return self._is_preventing


# 全局实例
power_manager = PowerManager()
```

### 2. 配置选项

```python
# nanodesk/config.py 或 nanobot/config/schema.py

class DesktopConfig(BaseModel):
    """桌面应用配置"""
    
    prevent_sleep: bool = True
    """阻止系统自动睡眠，保持 Agent 运行"""
    
    allow_screen_off: bool = True  
    """允许关闭显示器（仅阻止系统睡眠）"""
    
    auto_start: bool = False
    """Windows 启动时自动运行"""

```

### 3. 集成到主窗口

```python
# nanodesk/desktop/windows/main_window.py

from nanodesk.desktop.core.power_manager import power_manager

class MainWindow(QMainWindow):
    def __init__(self, config: DesktopConfig):
        super().__init__()
        self.config = config
        
        # ... 其他初始化 ...
        
        # 初始化电源管理
        self._init_power_management()
    
    def _init_power_management(self):
        """初始化电源管理，阻止睡眠但允许关屏"""
        if not self.config.prevent_sleep:
            logger.info("[Power] 电源管理已禁用（配置）")
            return
            
        success = power_manager.prevent_sleep(
            allow_screen_off=self.config.allow_screen_off
        )
        
        if success:
            # 日志记录
            logger.info("[Power] 已阻止系统睡眠，允许关闭屏幕")
            
            # 显示托盘提示
            self.tray_icon.showMessage(
                "Nanodesk",
                "🟢 Agent 已启动\n"
                "已阻止系统睡眠，关闭屏幕后 Agent 仍会继续运行",
                QSystemTrayIcon.Information,
                5000
            )
            
            # 可选：添加到消息历史，让用户在聊天窗口也能看到
            self._append_system_message(
                "✅ Agent 已启动\n"
                "💡 提示：系统已配置为阻止睡眠但允许关闭屏幕。\n"
                "   您可以放心关闭显示器，Agent 将在后台继续运行。"
            )
        else:
            logger.warning("[Power] 无法设置电源管理，系统可能会在关屏后睡眠")
            self.tray_icon.showMessage(
                "Nanodesk",
                "⚠️ 电源管理设置失败\n"
                "关闭屏幕后 Agent 可能会停止运行",
                QSystemTrayIcon.Warning,
                5000
            )
    
    def closeEvent(self, event):
        """关闭窗口时恢复电源设置"""
        # 恢复睡眠
        if power_manager.is_preventing:
            success = power_manager.allow_sleep()
            
            if success:
                logger.info("[Power] Agent 已停止，已恢复系统睡眠设置")
                self.tray_icon.showMessage(
                    "Nanodesk",
                    "🔴 Agent 已停止\n"
                    "已恢复系统睡眠设置，电脑将正常进入睡眠",
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                logger.warning("[Power] 恢复系统睡眠设置失败")
        
        # ... 其他清理 ...
        event.accept()
```

### 4. 设置面板集成

```python
# nanodesk/desktop/widgets/settings_dialog.py

class SettingsDialog(QDialog):
    def __init__(self, config: DesktopConfig):
        super().__init__()
        self.config = config
        self._setup_ui()
    
    def _setup_ui(self):
        # ... 其他设置 ...
        
        # 电源管理设置组
        power_group = QGroupBox("电源管理")
        power_layout = QVBoxLayout()
        
        self.prevent_sleep_check = QCheckBox("阻止系统睡眠")
        self.prevent_sleep_check.setChecked(self.config.prevent_sleep)
        self.prevent_sleep_check.setToolTip(
            "允许关闭屏幕，但防止系统进入睡眠状态，确保 Agent 持续运行"
        )
        
        self.screen_off_check = QCheckBox("允许关闭显示器")
        self.screen_off_check.setChecked(self.config.allow_screen_off)
        self.screen_off_check.setEnabled(self.config.prevent_sleep)
        self.screen_off_check.setToolTip(
            "勾选后屏幕可以正常关闭以节省电量"
        )
        
        # 联动：只有阻止睡眠时，允许关屏选项才有效
        self.prevent_sleep_check.toggled.connect(
            self.screen_off_check.setEnabled
        )
        
        power_layout.addWidget(self.prevent_sleep_check)
        power_layout.addWidget(self.screen_off_check)
        power_group.setLayout(power_layout)
        
        self.layout().addWidget(power_group)
    
    def save_settings(self):
        self.config.prevent_sleep = self.prevent_sleep_check.isChecked()
        self.config.allow_screen_off = self.screen_off_check.isChecked()
        self.config.save()
        
        # 立即应用更改
        if self.config.prevent_sleep:
            power_manager.prevent_sleep(self.config.allow_screen_off)
        else:
            power_manager.allow_sleep()
```

---

## 验证测试

### 测试用例

```python
# tests/test_power_manager.py

import time
import pytest
from nanodesk.desktop.core.power_manager import power_manager


class TestPowerManager:
    def test_prevent_sleep_allow_screen_off(self):
        """测试阻止睡眠但允许关屏"""
        result = power_manager.prevent_sleep(allow_screen_off=True)
        assert result is True
        assert power_manager.is_preventing is True
        
        # 恢复
        power_manager.allow_sleep()
        assert power_manager.is_preventing is False
    
    def test_singleton(self):
        """测试单例模式"""
        pm1 = PowerManager()
        pm2 = PowerManager()
        assert pm1 is pm2
```

### 手动验证步骤

1. **启动 Nanodesk**
   - 观察日志: `[PowerManager] 阻止睡眠，允许关闭屏幕`

2. **关闭显示器**
   - 按显示器电源按钮或 Win+L 锁屏

3. **等待 5 分钟**
   - 从另一台设备发送飞书消息

4. **验证响应**
   - Agent 应该正常回复

5. **检查系统状态**
   ```powershell
   powercfg /requests
   # 应该显示 Nanodesk 正在阻止睡眠
   ```

---

## 用户提示设计

### 启动时提示

**系统托盘气泡**:
```
🟢 Agent 已启动
已阻止系统睡眠，关闭屏幕后 Agent 仍会继续运行
```

**聊天窗口系统消息** (可选):
```
✅ Agent 已启动
💡 提示：系统已配置为阻止睡眠但允许关闭屏幕。
   您可以放心关闭显示器，Agent 将在后台继续运行。
   
   如需修改此设置，请前往：设置 → 电源管理
```

### 停止时提示

**系统托盘气泡**:
```
🔴 Agent 已停止
已恢复系统睡眠设置，电脑将正常进入睡眠
```

### 设置变更提示

当用户在设置面板修改电源选项时:
```python
if prevent_sleep_enabled:
    show_message("已启用阻止睡眠，关闭屏幕后 Agent 将继续运行")
else:
    show_message("已禁用阻止睡眠，关闭屏幕后系统将正常睡眠")
```

---

## 实施步骤

```
Phase 1: 核心功能 (1-2 天)
├── 创建 power_manager.py 模块
├── 集成到 MainWindow (含启动/停止提示)
└── 基础测试

Phase 2: 配置界面 (2-3 天)  
├── 添加配置项
├── 设置面板集成
└── 配置持久化

Phase 3: 优化 (1 天)
├── 添加系统托盘提示
├── 完善日志
└── 边界情况处理
```

---

## 风险与应对

| 风险 | 影响 | 应对 |
|------|------|------|
| API 调用失败 | 功能失效 | 失败时记录日志，不影响主程序 |
| 忘记恢复睡眠 | 电池耗尽 | 确保 closeEvent 和 __del__ 中恢复 |
| 多实例冲突 | 行为异常 | 单例模式 + 进程级锁 |

---

## 下一步

1. **确认方案**: 是否需要配置界面，还是默认开启即可？
2. **开始实现**: 我可以先实现 Phase 1（核心功能）
3. **测试验证**: 在你的机器上测试关屏后是否仍能保持运行

需要我立即开始实现吗？
