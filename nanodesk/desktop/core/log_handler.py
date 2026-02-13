"""Log handling for desktop application."""

from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, Signal


class LogHandler(QObject):
    """Handle application logging to file with GUI integration."""

    log_received = Signal(str)  # New log line

    def __init__(self, log_dir: Path = None):
        super().__init__()

        if log_dir is None:
            log_dir = Path.home() / ".nanobot" / "logs"

        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._current_log_file: Optional[Path] = None
        self._file_handle: Optional[object] = None

    def start_session(self) -> Path:
        """Start a new logging session."""
        # Close previous session
        self.end_session()

        # Create new log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_log_file = self.log_dir / f"nanodesk_{timestamp}.log"

        self._file_handle = open(self._current_log_file, "w", encoding="utf-8")

        self.write("=" * 50)
        self.write("Nanodesk Desktop Session Started")
        self.write(f"Time: {datetime.now().isoformat()}")
        self.write("=" * 50)

        return self._current_log_file

    def end_session(self):
        """End current logging session."""
        if self._file_handle:
            self.write("=" * 50)
            self.write("Session Ended")
            self.write("=" * 50)
            self._file_handle.close()
            self._file_handle = None

        self._current_log_file = None

    def write(self, message: str, level: str = "INFO"):
        """Write log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] [{level}] {message}"

        # Write to file
        if self._file_handle:
            self._file_handle.write(log_line + "\n")
            self._file_handle.flush()

        # Emit signal for GUI
        self.log_received.emit(log_line)

        # Also print to console
        print(log_line)

    def get_latest_log_file(self) -> Optional[Path]:
        """Get the most recent log file."""
        log_files = list(self.log_dir.glob("nanodesk_*.log"))
        if not log_files:
            return None
        return max(log_files, key=lambda p: p.stat().st_mtime)

    def get_log_files(self) -> list[Path]:
        """Get all log files sorted by time (newest first)."""
        log_files = list(self.log_dir.glob("nanodesk_*.log"))
        return sorted(log_files, key=lambda p: p.stat().st_mtime, reverse=True)

    def read_log_file(self, log_file: Path, tail_lines: int = 100) -> str:
        """Read log file content."""
        if not log_file.exists():
            return ""

        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if tail_lines > 0 and len(lines) > tail_lines:
                    lines = lines[-tail_lines:]
                return "".join(lines)
        except Exception as e:
            return f"Error reading log: {e}"


# Singleton instance
_log_handler = None


def get_log_handler() -> LogHandler:
    """Get singleton LogHandler instance."""
    global _log_handler
    if _log_handler is None:
        _log_handler = LogHandler()
    return _log_handler
