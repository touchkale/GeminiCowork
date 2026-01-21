# src/ui/__init__.py
"""UI components for Gemini Cowork"""

from .theme import COLORS, FONTS, SPACING, RADIUS, SIZES, ICONS
from .app import GeminiCoworkApp, run_app
from .sidebar import Sidebar
from .chat_view import ChatInterface
from .message_bubble import MessageBubble, TypingIndicator
from .dialogs import SettingsDialog, ApprovalDialog

__all__ = [
    'COLORS', 'FONTS', 'SPACING', 'RADIUS', 'SIZES', 'ICONS',
    'GeminiCoworkApp', 'run_app',
    'Sidebar',
    'ChatInterface',
    'MessageBubble', 'TypingIndicator',
    'SettingsDialog', 'ApprovalDialog',
]
