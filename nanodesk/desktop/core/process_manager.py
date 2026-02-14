# """Process management for Gateway."""
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal

from .log_handler import get_log_handler

# Global singleton instance
_process_manager: Optional["ProcessManager"] = None


def get_process_manager() -> "ProcessManager":
    """Get or create the global ProcessManager instance (singleton)."""
    global _process_manager
    if _process_manager is None:
        _process_manager = ProcessManager()
    return _process_manager


def find_embedded_python() -> Optional[str]:
    """
    Find the embedded Python interpreter in the bundled app.
    Returns None if not in bundle or embedded Python not found.

    Expected locations (PyInstaller onedir mode):
    - <app_dir>/python/python.exe (embedded Python)
    - <app_dir>/_internal/python.exe (PyInstaller's internal Python)
    """
    if not getattr(sys, "frozen", False):
        return None

    # Get the directory containing the executable
    exe_dir = Path(sys.executable).parent

    # Check for embedded Python directory
    embedded_python = exe_dir / "python" / "python.exe"
    if embedded_python.exists():
        return str(embedded_python)

    # Check for PyInstaller internal Python
    internal_python = exe_dir / "_internal" / "python.exe"
    if internal_python.exists():
        return str(internal_python)

    return None


def is_embedded_mode() -> bool:
    """Check if running in embedded mode (no system Python required)."""
    return find_embedded_python() is not None


class GatewaySubprocessThread(QThread):
    """
    Thread for running gateway as subprocess.
    Works in both development mode and bundled mode with embedded Python.
    """

    log_line = Signal(str)
    finished = Signal(bool, str)

    def __init__(self, python_cmd: str, module: str = "nanodesk.launcher", parent=None):
        super().__init__(parent)
        self.python_cmd = python_cmd
        self.module = module
        self._process: Optional[subprocess.Popen] = None
        self._stop_event = threading.Event()
        self._log_handler = get_log_handler()

    def _log(self, msg: str, level: str = "INFO"):
        """Log to both signal and file."""
        self.log_line.emit(msg)
        self._log_handler.write(msg, level)

    def run(self):
        """Run gateway as subprocess."""
        self._log("Starting gateway subprocess...")
        self._log(f"Using Python: {self.python_cmd}")

        # Verify Python exists
        if not os.path.exists(self.python_cmd):
            error_msg = f"Python interpreter not found: {self.python_cmd}"
            self._log(error_msg, "ERROR")
            self.finished.emit(False, error_msg)
            return

        try:
            # Build command
            cmd = [self.python_cmd, "-m", self.module, "gateway"]
            self._log(f"Command: {' '.join(cmd)}")

            # Set up environment
            env = os.environ.copy()
            python_exe_path = Path(self.python_cmd)

            if getattr(sys, "frozen", False):
                # In bundled mode, ensure embedded Python libs are accessible
                python_root = python_exe_path.parent

                # Add embedded Python paths to PYTHONPATH
                python_paths = [
                    str(python_root),
                    str(python_root / "Lib"),
                    str(python_root / "Lib" / "site-packages"),
                ]

                # Also check for python directory structure
                if (python_root / "python.exe").exists():
                    # We're in <app>/python/python.exe
                    embedded_root = python_root
                else:
                    # We're in PyInstaller _internal
                    embedded_root = python_root

                existing_path = env.get("PYTHONPATH", "")
                new_path = os.pathsep.join(
                    python_paths + ([existing_path] if existing_path else [])
                )
                env["PYTHONPATH"] = new_path

                # Set PATH to include embedded Python for DLLs
                env["PATH"] = str(python_root) + os.pathsep + env.get("PATH", "")

                # Set UTF-8 encoding for Python to avoid GBK codec errors on Windows
                env["PYTHONIOENCODING"] = "utf-8"
                env["PYTHONUTF8"] = "1"

                self._log("PYTHONPATH and UTF-8 encoding set for embedded mode")

            # Start process with UTF-8 encoding
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",  # Replace undecodable chars instead of crashing
                bufsize=1,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

            self._log(f"Gateway PID: {self._process.pid}")

            # Read output line by line with UTF-8 encoding
            try:
                for line in iter(self._process.stdout.readline, ""):
                    if self._stop_event.is_set():
                        break
                    if line:
                        self.log_line.emit(line.rstrip())
            except UnicodeDecodeError as e:
                self._log(f"Unicode decode error (non-fatal): {e}", "WARN")

            # Wait for process to finish
            self._process.wait()
            exit_code = self._process.returncode

            if exit_code == 0:
                self._log("Gateway exited normally")
                self.finished.emit(True, "")
            else:
                error_msg = f"Gateway exited with code {exit_code}"
                self._log(error_msg, "ERROR")
                self.finished.emit(False, error_msg)

        except Exception as e:
            error_msg = str(e)
            self._log(f"Subprocess error: {error_msg}", "ERROR")
            self.finished.emit(False, error_msg)

    def stop(self):
        """Stop the subprocess."""
        self._stop_event.set()
        if self._process and self._process.poll() is None:
            try:
                # Try graceful shutdown first
                import signal

                self._process.send_signal(signal.SIGTERM)
                self._process.wait(timeout=3)
            except:
                # Force kill
                self._process.kill()
                self._process.wait()
        self.wait(5000)


class ProcessManager(QObject):
    """Manage nanobot gateway process."""

    # Signals
    status_changed = Signal(str, bool)  # service_name, is_running
    error_occurred = Signal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self._gateway_thread: Optional[GatewaySubprocessThread] = None
        self._is_running = False
        self._log_handler = get_log_handler()

    @property
    def is_running(self) -> bool:
        """Check if gateway is running."""
        return self._is_running

    def _on_log_line(self, line: str):
        """Handle log line from thread."""
        self._log_handler.write(line, "INFO")

    def _on_finished(self, success: bool, error: str):
        """Handle thread finished."""
        self._is_running = False
        self.status_changed.emit("gateway", False)

        if not success and error:
            self.error_occurred.emit(error)

    def start_gateway(self) -> bool:
        """Start the gateway."""
        if self._is_running:
            return True

        self._log_handler.start_session()
        self._log_handler.write("Starting Gateway...")

        try:
            # Determine which Python to use
            python_cmd = None
            mode = "unknown"

            # Priority 1: Check for embedded Python (bundled mode)
            embedded_python = find_embedded_python()
            if embedded_python:
                python_cmd = embedded_python
                mode = "embedded"
                self._log_handler.write(f"Using embedded Python: {python_cmd}")

            # Priority 2: Check if we're in PyInstaller bundle (use its internal Python)
            elif getattr(sys, "frozen", False):
                exe_dir = Path(sys.executable).parent
                internal_python = exe_dir / "_internal" / "python.exe"

                if internal_python.exists():
                    python_cmd = str(internal_python)
                    mode = "pyinstaller_internal"
                    self._log_handler.write(f"Using PyInstaller internal Python: {python_cmd}")
                else:
                    # Last resort: try system Python
                    python_cmd = shutil.which("python") or shutil.which("python3")
                    mode = "system"
                    self._log_handler.write(f"Using system Python: {python_cmd}")

            # Priority 3: Development mode - use current Python
            else:
                python_cmd = sys.executable
                mode = "development"
                self._log_handler.write(f"Development mode: {python_cmd}")

            if not python_cmd:
                error_msg = "未找到 Python 解释器"
                self._log_handler.write(error_msg, "ERROR")
                self.error_occurred.emit(error_msg)
                return False

            # Verify Python is executable
            if not os.path.exists(python_cmd):
                error_msg = f"Python 解释器不存在: {python_cmd}"
                self._log_handler.write(error_msg, "ERROR")
                self.error_occurred.emit(error_msg)
                return False

            # In development/system mode, check if nanobot is available
            if mode in ("development", "system"):
                try:
                    self._log_handler.write("Checking nanobot availability...")
                    result = subprocess.run(
                        [python_cmd, "-c", "import nanobot; print('OK')"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode != 0:
                        error_msg = "缺少 nanobot 模块。请运行: pip install -e ."
                        self._log_handler.write(error_msg, "ERROR")
                        self._log_handler.write(f"Error: {result.stderr}", "ERROR")
                        self.error_occurred.emit(error_msg)
                        return False
                    self._log_handler.write("Nanobot check passed")
                except Exception as e:
                    self._log_handler.write(f"Dependency check warning: {e}", "WARN")
            else:
                # Embedded mode - assume nanobot is included
                self._log_handler.write("Embedded mode - assuming nanobot is bundled")

            # Create and start thread
            self._gateway_thread = GatewaySubprocessThread(python_cmd, parent=self)
            self._gateway_thread.log_line.connect(self._on_log_line)
            self._gateway_thread.finished.connect(self._on_finished)

            self._gateway_thread.start()
            self._is_running = True
            self.status_changed.emit("gateway", True)

            self._log_handler.write(f"Gateway started (mode: {mode})")
            return True

        except Exception as e:
            error_msg = f"启动失败: {e}"
            self._log_handler.write(error_msg, "ERROR")
            self.error_occurred.emit(error_msg)
            return False

    def stop_gateway(self):
        """Stop the gateway."""
        if not self._is_running or not self._gateway_thread:
            return

        self._log_handler.write("Stopping Gateway...")
        self._gateway_thread.stop()
        self._gateway_thread = None
        self._is_running = False
        self.status_changed.emit("gateway", False)
        self._log_handler.write("Gateway stopped")
