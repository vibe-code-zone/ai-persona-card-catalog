#!/usr/bin/env python3
"""
Launcher script for the AI Persona Card Catalog TUI application.
Checks dependencies and launches the main Textual-based persona browser.

Generated with Claude Code (claude-sonnet-4) via collaborative "vibe-coding" sessions.
"""

import subprocess
import sys


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import textual
        import yaml

        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False


def main():
    if not check_dependencies():
        sys.exit(1)

    # Import and run the textual version
    from persona_browser_textual import main as textual_main

    textual_main()


if __name__ == "__main__":
    main()
