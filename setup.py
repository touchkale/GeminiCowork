"""
cx_Freeze setup script for Gemini Cowork
Creates a Windows executable
"""

import sys
from cx_Freeze import setup, Executable

# Dependencies
build_exe_options = {
    "packages": [
        "customtkinter",
        "google.generativeai", 
        "PIL",
        "pygments",
        "tkinter",
        "json",
        "pathlib",
        "threading",
        "queue",
        "subprocess",
        "shutil",
        "datetime",
        "dataclasses",
    ],
    "excludes": [
        "test",
        "unittest", 
        "xmlrpc",
        "pydoc",
        "doctest",
    ],
    "include_files": [],
    "optimize": 2,
}

# Base for Windows GUI app (no console)
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="GeminiCowork",
    version="1.0.0",
    description="AI Coding Assistant powered by Google Gemini",
    author="Raj Sharma",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="GeminiCowork.exe",
            icon=None,  # Add icon path here if available
        )
    ],
)
