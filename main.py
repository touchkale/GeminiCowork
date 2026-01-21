#!/usr/bin/env python3
"""
Gemini Cowork - Native Windows AI Coding Assistant

A Claude Cowork-like application powered by Google Gemini API.
"""

import sys
import os

# Fix console encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui.app import run_app


def main():
    """Main entry point."""
    print("Starting Gemini Cowork...")
    run_app()


if __name__ == "__main__":
    main()
