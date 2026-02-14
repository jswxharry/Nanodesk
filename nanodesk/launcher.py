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

    # 1. Inject Nanodesk customization
    from nanodesk import bootstrap

    bootstrap.inject()

    # 2. Start nanobot CLI
    from nanobot.cli.commands import app

    app()


if __name__ == "__main__":
    main()
