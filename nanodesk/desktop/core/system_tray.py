"""System tray icon and menu."""

from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon


class SystemTray(QSystemTrayIcon):
    """System tray icon with context menu."""
    
    # Signals
    show_window = Signal()
    toggle_gateway = Signal()
    view_logs = Signal()
    open_settings = Signal()
    quit_app = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set tooltip
        self.setToolTip("Nanodesk - Stopped")
        
        # Build menu
        self._build_menu()
        
        # Connect activated signal (click on icon)
        self.activated.connect(self._on_activated)
    
    def _build_menu(self):
        """Build context menu."""
        menu = QMenu()
        
        # Title/status (non-clickable)
        self._status_action = QAction("🛑 Stopped")
        self._status_action.setEnabled(False)
        menu.addAction(self._status_action)
        
        menu.addSeparator()
        
        # Toggle gateway
        self._toggle_action = QAction("▶ 启动 Gateway")
        self._toggle_action.triggered.connect(self.toggle_gateway.emit)
        menu.addAction(self._toggle_action)
        
        menu.addSeparator()
        
        # Show window
        show_action = QAction("打开主窗口")
        show_action.triggered.connect(self.show_window.emit)
        menu.addAction(show_action)
        
        # View logs
        logs_action = QAction("查看日志")
        logs_action.triggered.connect(self.view_logs.emit)
        menu.addAction(logs_action)
        
        # Settings
        settings_action = QAction("重新配置...")
        settings_action.triggered.connect(self.open_settings.emit)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("退出")
        quit_action.triggered.connect(self.quit_app.emit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
    
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
