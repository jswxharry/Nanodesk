"""Nanodesk Launcher - Entry point

Loads customization and starts nanobot CLI.
"""

import sys


def _setup_windows_encoding():
    """Windows encoding fix: force UTF-8 to avoid Unicode errors."""
    if sys.platform != "win32":
        return

    import io

    # Check if encoding fix is needed
    needs_fix = sys.stdout.encoding != "utf-8" or sys.stderr.encoding != "utf-8"

    if needs_fix:
        # Reconfigure stdout/stderr to UTF-8
        if sys.stdout.encoding != "utf-8":
            sys.stdout = io.TextIOWrapper(
                sys.stdout.buffer, encoding="utf-8", errors="replace"
            )
        if sys.stderr.encoding != "utf-8":
            sys.stderr = io.TextIOWrapper(
                sys.stderr.buffer, encoding="utf-8", errors="replace"
            )

        # Notify user (shown once when not UTF-8)
        print(
            "[INFO] Terminal encoding is not UTF-8, auto-switched to prevent garbled output",
            file=sys.stderr,
        )
        print(
            "[INFO] To fix permanently, run: [Environment]::SetEnvironmentVariable('PYTHONIOENCODING', 'utf-8', 'User')",
            file=sys.stderr,
        )
        print(file=sys.stderr)


def main():
    """Main entry point."""
    # 0. Setup encoding first (before any output)
    _setup_windows_encoding()

    # 1. Add project root to path (before any imports)
    import sys
    from pathlib import Path
    root = Path(__file__).parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # 2. Inject Nanodesk customization (BEFORE importing nanobot)
    from nanodesk import bootstrap
    bootstrap.inject()

    # 3. Start nanobot CLI (AFTER injection)
    from nanobot.cli.commands import app
    app()


if __name__ == "__main__":
    main()
