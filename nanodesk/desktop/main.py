"""Entry point for Nanodesk Desktop."""

import sys
import os

# Disable Windows dark mode for Qt application before any Qt imports
os.environ['QT_QPA_PLATFORMTHEME'] = ''  # Disable platform theme
os.environ['QT_STYLE_OVERRIDE'] = 'Fusion'  # Force Fusion style
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'

# Fix for PyInstaller: set Qt plugin path before importing Qt
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
    os.environ['QT_PLUGIN_PATH'] = os.path.join(bundle_dir, 'PySide6', 'plugins')
    os.environ['QML2_IMPORT_PATH'] = os.path.join(bundle_dir, 'PySide6', 'qml')


def main():
    """Main entry point."""
    import asyncio
    from PySide6.QtAsyncio import QAsyncioEventLoopPolicy
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QPalette, QColor
    
    # Create application with Fusion style
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName("Nanodesk")
    app.setApplicationVersion("1.0.0")
    
    # Force light palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
    app.setPalette(palette)
    
    # Set async event loop policy
    asyncio.set_event_loop_policy(QAsyncioEventLoopPolicy())
    
    # Import and create main window (after app is created)
    from nanodesk.desktop.windows.main_window import MainWindow
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
