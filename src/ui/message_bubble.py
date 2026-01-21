# Message Bubble Component
"""
Professional message bubbles for chat interface.
Google Material Design 3 inspired with code block support.
"""

import customtkinter as ctk
from typing import Optional, List, Dict, Any
import re

try:
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer
    from pygments.formatters import HtmlFormatter
    PYGMENTS_AVAILABLE = True
except ImportError:
    PYGMENTS_AVAILABLE = False

from .theme import COLORS, FONTS, SPACING, RADIUS, ICONS


class CodeBlock(ctk.CTkFrame):
    """A syntax-highlighted code block with copy functionality."""
    
    def __init__(
        self,
        master,
        code: str,
        language: str = "python",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["code_bg"],
            corner_radius=RADIUS["sm"],
            **kwargs
        )
        
        self.code = code
        
        # Header with language and copy button
        header = ctk.CTkFrame(self, fg_color=COLORS["bg_elevated"], height=32, corner_radius=0)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Language label
        lang_label = ctk.CTkLabel(
            header,
            text=language or "code",
            font=(FONTS["family_mono"], FONTS["size_tiny"]),
            text_color=COLORS["text_tertiary"]
        )
        lang_label.pack(side="left", padx=SPACING["md"])
        
        # Copy button
        copy_btn = ctk.CTkButton(
            header,
            text="Copy",
            font=(FONTS["family"], FONTS["size_tiny"]),
            fg_color="transparent",
            hover_color=COLORS["bg_tertiary"],
            text_color=COLORS["text_secondary"],
            width=50,
            height=24,
            corner_radius=RADIUS["xs"],
            command=self._copy_code
        )
        copy_btn.pack(side="right", padx=SPACING["sm"])
        
        # Code content
        code_frame = ctk.CTkFrame(self, fg_color="transparent")
        code_frame.pack(fill="both", expand=True, padx=SPACING["md"], pady=SPACING["sm"])
        
        # Display code (simple text for now)
        code_label = ctk.CTkLabel(
            code_frame,
            text=code,
            font=(FONTS["family_mono"], FONTS["size_small"]),
            text_color=COLORS["text_primary"],
            justify="left",
            anchor="nw",
            wraplength=600
        )
        code_label.pack(fill="both", expand=True, anchor="nw")
    
    def _copy_code(self):
        """Copy code to clipboard."""
        self.clipboard_clear()
        self.clipboard_append(self.code)


class ToolCallCard(ctk.CTkFrame):
    """Card displaying a tool/function call."""
    
    def __init__(
        self,
        master,
        tool_name: str,
        tool_args: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        status: str = "pending",  # pending, running, success, error, denied
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_tertiary"],
            corner_radius=RADIUS["sm"],
            **kwargs
        )
        
        # Status colors
        status_colors = {
            "pending": COLORS["text_tertiary"],
            "running": COLORS["warning"],
            "success": COLORS["success"],
            "error": COLORS["error"],
            "denied": COLORS["error"],
        }
        
        status_icons = {
            "pending": "○",
            "running": "◌",
            "success": "✓",
            "error": "✕",
            "denied": "⊘",
        }
        
        # Header row
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], SPACING["xs"]))
        
        # Status icon
        status_label = ctk.CTkLabel(
            header,
            text=status_icons.get(status, "○"),
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=status_colors.get(status, COLORS["text_secondary"]),
            width=20
        )
        status_label.pack(side="left")
        
        # Tool name
        name_label = ctk.CTkLabel(
            header,
            text=tool_name,
            font=(FONTS["family_mono"], FONTS["size_small"], "bold"),
            text_color=COLORS["text_accent"]
        )
        name_label.pack(side="left", padx=SPACING["xs"])
        
        # Arguments (collapsed view)
        if tool_args:
            args_text = ", ".join(f"{k}={repr(v)[:30]}" for k, v in list(tool_args.items())[:3])
            if len(args_text) > 60:
                args_text = args_text[:60] + "..."
            
            args_label = ctk.CTkLabel(
                self,
                text=args_text,
                font=(FONTS["family_mono"], FONTS["size_tiny"]),
                text_color=COLORS["text_tertiary"],
                anchor="w"
            )
            args_label.pack(fill="x", padx=SPACING["md"], pady=(0, SPACING["sm"]))


class MessageBubble(ctk.CTkFrame):
    """A professional chat message bubble."""
    
    def __init__(
        self,
        master,
        role: str,  # "user" or "ai"
        content: str = "",
        tool_calls: Optional[List[Dict]] = None,
        **kwargs
    ):
        # Different styling for user vs AI
        is_user = role == "user"
        
        super().__init__(
            master,
            fg_color="transparent",
            **kwargs
        )
        
        # Container with max width
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(
            fill="x",
            padx=SPACING["lg"],
            pady=SPACING["sm"],
            anchor="e" if is_user else "w"
        )
        
        # Avatar and message row
        row = ctk.CTkFrame(container, fg_color="transparent")
        row.pack(fill="x", anchor="e" if is_user else "w")
        
        if not is_user:
            # AI avatar
            avatar = ctk.CTkFrame(
                row,
                fg_color=COLORS["gemini_blue"],
                width=32,
                height=32,
                corner_radius=RADIUS["full"]
            )
            avatar.pack(side="left", anchor="n", padx=(0, SPACING["sm"]))
            avatar.pack_propagate(False)
            
            avatar_text = ctk.CTkLabel(
                avatar,
                text="✦",
                font=(FONTS["family"], 14),
                text_color="#FFFFFF"
            )
            avatar_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Message content
        msg_frame = ctk.CTkFrame(
            row,
            fg_color=COLORS["user_bubble"] if is_user else COLORS["ai_bubble"],
            corner_radius=RADIUS["lg"]
        )
        msg_frame.pack(side="right" if is_user else "left", anchor="e" if is_user else "w")
        
        # Parse and render content
        if content:
            self._render_content(msg_frame, content, is_user)
        
        # Tool calls
        if tool_calls and not is_user:
            tools_frame = ctk.CTkFrame(msg_frame, fg_color="transparent")
            tools_frame.pack(fill="x", padx=SPACING["sm"], pady=SPACING["sm"])
            
            for tc in tool_calls:
                tool_card = ToolCallCard(
                    tools_frame,
                    tool_name=tc.get("name", "unknown"),
                    tool_args=tc.get("args", {}),
                    result=tc.get("result"),
                    status=tc.get("status", "success")
                )
                tool_card.pack(fill="x", pady=SPACING["xs"])
    
    def _render_content(self, parent, content: str, is_user: bool):
        """Parse and render message content with code blocks."""
        # Split content by code blocks
        code_pattern = r'```(\w*)\n?([\s\S]*?)```'
        parts = re.split(code_pattern, content)
        
        current_text = ""
        i = 0
        
        while i < len(parts):
            part = parts[i]
            
            # Check if this is a language identifier (comes after code block match)
            if i > 0 and i % 3 == 1:
                # This is the language
                language = part or "text"
                code = parts[i + 1] if i + 1 < len(parts) else ""
                
                # Render any pending text
                if current_text.strip():
                    self._add_text(parent, current_text.strip(), is_user)
                    current_text = ""
                
                # Render code block
                code_block = CodeBlock(parent, code.strip(), language)
                code_block.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])
                
                i += 2
            else:
                current_text += part
                i += 1
        
        # Render remaining text
        if current_text.strip():
            self._add_text(parent, current_text.strip(), is_user)
    
    def _add_text(self, parent, text: str, is_user: bool):
        """Add a text label."""
        text_label = ctk.CTkLabel(
            parent,
            text=text,
            font=(FONTS["family"], FONTS["size_body"]),
            text_color="#FFFFFF" if is_user else COLORS["text_primary"],
            justify="left" if not is_user else "right",
            anchor="w" if not is_user else "e",
            wraplength=500
        )
        text_label.pack(
            fill="x",
            padx=SPACING["md"],
            pady=SPACING["sm"],
            anchor="w" if not is_user else "e"
        )


class TypingIndicator(ctk.CTkFrame):
    """Animated typing indicator for AI responses."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        # Container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
        
        # Avatar
        avatar = ctk.CTkFrame(
            container,
            fg_color=COLORS["gemini_blue"],
            width=32,
            height=32,
            corner_radius=RADIUS["full"]
        )
        avatar.pack(side="left", anchor="n", padx=(0, SPACING["sm"]))
        avatar.pack_propagate(False)
        
        avatar_text = ctk.CTkLabel(
            avatar,
            text="✦",
            font=(FONTS["family"], 14),
            text_color="#FFFFFF"
        )
        avatar_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Typing bubble
        bubble = ctk.CTkFrame(
            container,
            fg_color=COLORS["ai_bubble"],
            corner_radius=RADIUS["lg"]
        )
        bubble.pack(side="left")
        
        # Dots
        self.dots_label = ctk.CTkLabel(
            bubble,
            text="●  ●  ●",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_tertiary"]
        )
        self.dots_label.pack(padx=SPACING["md"], pady=SPACING["sm"])
        
        self._animate()
    
    def _animate(self):
        """Animate the typing dots."""
        current = self.dots_label.cget("text")
        states = ["●  ○  ○", "○  ●  ○", "○  ○  ●", "●  ●  ●"]
        try:
            idx = states.index(current)
            next_state = states[(idx + 1) % len(states)]
        except ValueError:
            next_state = states[0]
        
        self.dots_label.configure(text=next_state)
        self.after(400, self._animate)
