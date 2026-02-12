"""Main window for Nanodesk Desktop."""

from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGroupBox, QStatusBar, QMessageBox,
    QDialog, QTextEdit, QDialogButtonBox, QListWidget
)

from nanodesk.desktop.core.config_manager import get_config_manager
from nanodesk.desktop.core.process_manager import get_process_manager
from nanodesk.desktop.core.log_handler import get_log_handler
from nanodesk.desktop.core.system_tray import SystemTray
from nanodesk.desktop.windows.setup_wizard import SetupWizard


class StatusCard(QGroupBox):
    """Status card widget."""
    
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        self.status_label = QLabel("🛑 已停止")
        self.status_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.status_label)
        
        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("color: gray;")
        layout.addWidget(self.detail_label)
        
        self.setLayout(layout)
    
    def set_status(self, running: bool, detail: str = ""):
        """Update status display."""
        if running:
            self.status_label.setText("🟢 运行中")
            self.status_label.setStyleSheet("font-size: 16px; color: green;")
        else:
            self.status_label.setText("🛑 已停止")
            self.status_label.setStyleSheet("font-size: 16px; color: red;")
        
        self.detail_label.setText(detail)


class LogViewerDialog(QDialog):
    """Dialog for viewing logs."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("查看日志")
        self.setMinimumSize(800, 600)
        
        self._setup_ui()
        self._load_log_files()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("日志文件:"))
        self.file_list = QListWidget()
        self.file_list.setMaximumWidth(300)
        self.file_list.currentItemChanged.connect(self._on_file_selected)
        file_layout.addWidget(self.file_list)
        
        # Log content
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        file_layout.addWidget(self.log_text)
        
        layout.addLayout(file_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(self.reject)
        
        refresh_btn = buttons.addButton("刷新", QDialogButtonBox.ButtonRole.ActionRole)
        refresh_btn.clicked.connect(self._refresh)
        
        open_folder_btn = buttons.addButton("打开目录", QDialogButtonBox.ButtonRole.ActionRole)
        open_folder_btn.clicked.connect(self._open_log_dir)
        
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def _load_log_files(self):
        """Load list of log files."""
        log_handler = get_log_handler()
        log_files = log_handler.get_log_files()
        
        self.file_list.clear()
        for log_file in log_files:
            self.file_list.addItem(log_file.name)
        
        # Select first item
        if self.file_list.count() > 0:
            self.file_list.setCurrentRow(0)
    
    def _on_file_selected(self):
        """Show selected log file content."""
        item = self.file_list.currentItem()
        if not item:
            return
        
        log_handler = get_log_handler()
        log_files = log_handler.get_log_files()
        
        for log_file in log_files:
            if log_file.name == item.text():
                content = log_handler.read_log_file(log_file)
                self.log_text.setPlainText(content)
                break
    
    def _refresh(self):
        """Refresh log list and content."""
        self._load_log_files()
    
    def _open_log_dir(self):
        """Open log directory in explorer."""
        import subprocess
        log_dir = get_log_handler().log_dir
        subprocess.Popen(f'explorer "{log_dir}"')


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Nanodesk Desktop")
        self.resize(600, 500)
        self.setMinimumSize(500, 400)
        
        # Initialize components
        self.config_manager = get_config_manager()
        self.process_manager = get_process_manager()
        self.log_handler = get_log_handler()
        self.tray = SystemTray(self)
        
        # Setup UI
        self._setup_ui()
        self._setup_tray()
        self._setup_shortcuts()
        self._connect_signals()
        
        # Check first run
        self._check_first_run()
    
    def _setup_ui(self):
        """Setup user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("🐢 Nanodesk Desktop")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)
        
        # Status cards
        status_layout = QHBoxLayout()
        
        self.gateway_card = StatusCard("Gateway 服务")
        status_layout.addWidget(self.gateway_card)
        
        layout.addLayout(status_layout)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ 启动")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #45a049; }
        """)
        self.start_btn.clicked.connect(self._on_start)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #da190b; }
        """)
        self.stop_btn.clicked.connect(self._on_stop)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Quick actions
        quick_layout = QHBoxLayout()
        
        open_dir_btn = QPushButton("📂 打开工作目录")
        open_dir_btn.clicked.connect(self._open_workspace)
        quick_layout.addWidget(open_dir_btn)
        
        view_logs_btn = QPushButton("📝 查看日志")
        view_logs_btn.clicked.connect(self._view_logs)
        quick_layout.addWidget(view_logs_btn)
        
        config_btn = QPushButton("⚙️ 重新配置")
        config_btn.clicked.connect(self._open_settings)
        quick_layout.addWidget(config_btn)
        
        layout.addLayout(quick_layout)
        
        # Log preview
        log_group = QGroupBox("最近日志")
        log_layout = QVBoxLayout()
        self.log_preview = QTextEdit()
        self.log_preview.setReadOnly(True)
        self.log_preview.setMaximumHeight(150)
        log_layout.addWidget(self.log_preview)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        central.setLayout(layout)
    
    def _setup_tray(self):
        """Setup system tray."""
        self.tray.show()
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # Ctrl+Q to quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self.close)
        
        # Ctrl+R to restart
        restart_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        restart_shortcut.activated.connect(self._on_restart)
    
    def _connect_signals(self):
        """Connect signals and slots."""
        # Tray signals
        self.tray.show_window.connect(self.show)
        self.tray.toggle_gateway.connect(self._on_toggle_gateway)
        self.tray.view_logs.connect(self._view_logs)
        self.tray.open_settings.connect(self._open_settings)
        self.tray.quit_app.connect(self._on_quit)
        
        # Process manager signals
        self.process_manager.status_changed.connect(self._on_status_changed)
        self.process_manager.error_occurred.connect(self._on_error)
        self.process_manager.log_message.connect(self._on_log_message)
        
        # Log handler
        self.log_handler.log_received.connect(self._on_log_message)
    
    def _check_first_run(self):
        """Check if first run and show wizard."""
        if self.config_manager.is_first_run():
            self._open_settings()
    
    @Slot()
    def _on_start(self):
        """Start gateway."""
        self.status_bar.showMessage("正在启动 Gateway...")
        
        # Start gateway (synchronous, runs in background thread)
        result = self.process_manager.start_gateway()
        if not result:
            self.status_bar.showMessage("Gateway 启动失败")
    
    @Slot()
    def _on_stop(self):
        """Stop gateway."""
        self.status_bar.showMessage("正在停止 Gateway...")
        self.process_manager.stop_gateway()
    
    @Slot()
    def _on_restart(self):
        """Restart gateway."""
        self.status_bar.showMessage("正在重启 Gateway...")
        self.process_manager.restart_gateway()
    
    @Slot()
    def _on_toggle_gateway(self):
        """Toggle gateway on/off."""
        if self.process_manager.is_running:
            self._on_stop()
        else:
            self._on_start()
    
    @Slot(str, bool)
    def _on_status_changed(self, service: str, running: bool):
        """Handle status change."""
        if service == "gateway":
            self.gateway_card.set_status(running, "端口: 18790" if running else "")
            self.tray.update_status(running)
            
            self.start_btn.setEnabled(not running)
            self.stop_btn.setEnabled(running)
            
            if running:
                self.status_bar.showMessage("Gateway 运行中")
            else:
                self.status_bar.showMessage("Gateway 已停止")
    
    @Slot(str)
    def _on_error(self, message: str):
        """Handle error."""
        QMessageBox.critical(self, "错误", message)
        self.status_bar.showMessage(f"错误: {message}")
    
    @Slot(str)
    def _on_log_message(self, message: str):
        """Handle log message."""
        # Append to log preview
        self.log_preview.append(message)
        # Scroll to bottom
        scrollbar = self.log_preview.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    @Slot()
    def _open_workspace(self):
        """Open workspace directory."""
        config = self.config_manager.load()
        workspace = config["agents"]["defaults"]["workspace"]
        Path(workspace).mkdir(parents=True, exist_ok=True)
        
        import subprocess
        subprocess.Popen(f'explorer "{workspace}"')
    
    @Slot()
    def _view_logs(self):
        """View logs."""
        dialog = LogViewerDialog(self)
        dialog.exec()
    
    @Slot()
    def _open_settings(self):
        """Open settings wizard."""
        wizard = SetupWizard(self)
        wizard.config_saved.connect(lambda: self.status_bar.showMessage("配置已保存"))
        wizard.exec()
    
    @Slot()
    def _on_quit(self):
        """Quit application."""
        # Stop gateway if running
        if self.process_manager.is_running:
            import asyncio
            asyncio.create_task(self.process_manager.stop_gateway())
        
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle close event - minimize to tray instead."""
        event.ignore()
        self.hide()
        self.tray.showMessage(
            "Nanodesk",
            "程序已最小化到系统托盘",
            SystemTray.MessageIcon.Information,
            2000
        )
