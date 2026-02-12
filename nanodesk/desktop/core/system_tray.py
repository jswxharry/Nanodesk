"""System tray icon and menu."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


def _get_icon_path() -> str:
    """Get the path to the application icon."""
    # Try multiple locations
    possible_paths = [
        # Development: relative to this file
        Path(__file__).parent.parent / "resources" / "icons" / "logo.ico",
        # Packaged: relative to executable
        Path(__file__).parent.parent.parent.parent / "resources" / "icons" / "logo.ico",
        # PyInstaller: _internal folder
        Path(__file__).parent.parent / "_internal" / "resources" / "icons" / "logo.ico",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path)
    
    # Fallback: return first path even if not exists (will show default icon)
    return str(possible_paths[0])


class SystemTray(QSystemTrayIcon):
    """System tray icon with context menu."""
    
    # Signals
    show_window = Signal()
    toggle_gateway = Signal()
    view_logs = Signal()
    open_settings = Signal()
    quit_app = Signal()
    
    # Keep references to prevent garbage collection
    _menu = None
    _actions = []
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set tooltip
        self.setToolTip("Nanodesk - Stopped")
        
        # Build menu first
        self._build_menu()
        
        # Set icon (after menu is built)
        icon_path = _get_icon_path()
        if Path(icon_path).exists():
            self.setIcon(QIcon(icon_path))
        else:
            # Use default icon if logo.ico not found
            self.setIcon(QIcon.fromTheme("application-x-executable"))
        
        # Connect activated signal (click on icon)
        self.activated.connect(self._on_activated)
        
        # Ensure menu is accessible
        self.setVisible(True)
    
    def _build_menu(self):
        """Build context menu."""
        self._menu = QMenu()
        self._actions = []  # Clear old references
        
        def add_action(text, signal=None, enabled=True):
            """Helper to create action and keep reference."""
            action = QAction(text)
            action.setEnabled(enabled)
            if signal:
                action.triggered.connect(signal)
            self._menu.addAction(action)
            self._actions.append(action)
            return action
        
        # Title/status (non-clickable)
        self._status_action = add_action("🛑 Stopped", enabled=False)
        
        self._menu.addSeparator()
        
        # Toggle gateway
        self._toggle_action = add_action("▶ 启动 Gateway", self.toggle_gateway.emit)
        
        self._menu.addSeparator()
        
        # Show window
        add_action("打开主窗口", self.show_window.emit)
        
        # View logs
        add_action("查看日志", self.view_logs.emit)
        
        # Settings
        add_action("重新配置...", self.open_settings.emit)
        
        self._menu.addSeparator()
        
        # Quit
        add_action("退出", self.quit_app.emit)
        
        self.setContextMenu(self._menu)
    
    def update_status(self, is_running: bool):
        """Update tray icon and menu based on status."""
        if is_running:
            self._status_action.setText("🟢 Running")
            self._toggle_action.setText("⏹ 停止 Gateway")
            self.setToolTip("Nanodesk - Running")
        else:
            self._status_action.setText("🛑 Stopped")
            self._toggle_action.setText("▶ 启动 Gateway")
            self.setToolTip("Nanodesk - Stopped")
    
    def _on_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Left click - show window
            self.show_window.emit()
