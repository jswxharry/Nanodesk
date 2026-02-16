"""Gateway runner for bundled application.

This module is used to start the Gateway from the bundled executable.
"""

import os
import sys

# Add the bundle directory to path if running from PyInstaller
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
else:
    # Development mode - add project root
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def main():
    """Start the Gateway."""
    # Inject nanodesk customizations FIRST (before any nanobot imports)
    import sys
    from pathlib import Path
    
    # Add project root to path
    root = Path(__file__).parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    
    # Now inject
    from nanodesk import bootstrap
    bootstrap.inject()

    # Import and run gateway command (AFTER injection)
    from click.testing import CliRunner
    from nanobot.cli.commands import app

    # Run gateway command
    runner = CliRunner()
    result = runner.invoke(app, ["gateway"])

    if result.exit_code != 0:
        print(f"Gateway exited with code: {result.exit_code}")
        if result.exception:
            raise result.exception


if __name__ == "__main__":
    main()
