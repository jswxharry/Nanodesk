"""QApplication setup for Nanodesk Desktop."""

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


class NanodeskApp(QApplication):
    """Custom QApplication for Nanodesk."""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Application metadata
        self.setApplicationName("Nanodesk")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Nanodesk")
        
        # Enable high DPI support
        self.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Setup global font
        font = QFont("Microsoft YaHei", 10)
        self.setFont(font)
        
        # Set application style
        self.setStyle("Fusion")
        
        # Load stylesheet
        self._load_stylesheet()
    
    def _load_stylesheet(self):
        """Load application stylesheet with light theme."""
        # Force light theme to ensure visibility on both light/dark Windows modes
        self.setStyleSheet("""
            /* Base */
            QWidget {
                background-color: #ffffff;
                color: #333333;
            }
            
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            /* Group Box */
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #ffffff;
                color: #333333;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #333333;
            }
            
            /* Buttons */
            QPushButton {
                background-color: #e0e0e0;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px 16px;
                color: #333333;
            }
            
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
            
            /* Input Fields */
            QLineEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                color: #333333;
            }
            
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 8px;
                color: #333333;
            }
            
            QComboBox:focus {
                border: 1px solid #4CAF50;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
            }
            
            /* Wizard */
            QWizard {
                background-color: #ffffff;
            }
            
            QWizardPage {
                background-color: #ffffff;
            }
            
            QWizardPage QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            
            QWizardPage QLabel {
                color: #000000;
                background-color: transparent;
                font-size: 12px;
            }
            
            /* Text Edit */
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                color: #333333;
            }
            
            /* Labels */
            QLabel {
                color: #000000;
                background-color: transparent;
            }
            
            /* Check Box */
            QCheckBox {
                color: #333333;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #f0f0f0;
                color: #333333;
            }
            
            /* Menu */
            QMenu {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #cccccc;
            }
            
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            
            /* Scroll Bar */
            QScrollBar:vertical {
                background-color: #f0f0f0;
                width: 12px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #c0c0c0;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #a0a0a0;
            }
        """)
