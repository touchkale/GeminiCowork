# Chat View Component
"""
Professional chat interface with input area and message display.
Google Material Design 3 inspired.
"""

import customtkinter as ctk
from typing import Optional, Callable, List, Dict, Any
import threading

from .theme import COLORS, FONTS, SPACING, RADIUS, SIZES, ICONS
from .message_bubble import MessageBubble, TypingIndicator
from ..services.gemini_service import gemini_service
from ..services.session_service import session_service


class WelcomeScreen(ctk.CTkFrame):
    """Professional welcome screen with Google-style design."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_suggestion = None
        
        # Center content container
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.42, anchor="center")
        
        # Gradient-style Gemini logo (layered circles for depth)
        logo_container = ctk.CTkFrame(center, fg_color="transparent")
        logo_container.pack(pady=(0, SPACING["lg"]))
        
        # Outer glow effect
        glow = ctk.CTkFrame(
            logo_container,
            fg_color="#1a3a5c",
            width=100,
            height=100,
            corner_radius=50
        )
        glow.pack()
        glow.pack_propagate(False)
        
        # Inner gradient circle
        inner_circle = ctk.CTkFrame(
            glow,
            fg_color="#2563eb",
            width=80,
            height=80,
            corner_radius=40
        )
        inner_circle.place(relx=0.5, rely=0.5, anchor="center")
        inner_circle.pack_propagate(False)
        
        # Gemini sparkle icon
        icon_label = ctk.CTkLabel(
            inner_circle,
            text="✦",
            font=("Segoe UI", 40, "bold"),
            text_color="#FFFFFF"
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Main title with gradient-like styling
        title = ctk.CTkLabel(
            center,
            text="Welcome to Gemini Cowork",
            font=("Segoe UI", 32, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(pady=(SPACING["md"], SPACING["sm"]))
        
        # Subtitle
        subtitle = ctk.CTkLabel(
            center,
            text="Your AI-powered coding assistant",
            font=("Segoe UI", 16),
            text_color="#9CA3AF"
        )
        subtitle.pack(pady=(0, SPACING["sm"]))
        
        # Description
        desc = ctk.CTkLabel(
            center,
            text="I can help you analyze code, manage files, run commands,\nand much more. Just ask!",
            font=("Segoe UI", 14),
            text_color="#6B7280",
            justify="center"
        )
        desc.pack(pady=(0, SPACING["xl"]))
        
        # Suggestion cards in a grid (2x2)
        cards_container = ctk.CTkFrame(center, fg_color="transparent")
        cards_container.pack()
        
        suggestions = [
            {"icon": "📝", "title": "Analyze Code", "desc": "Review and explain code"},
            {"icon": "📁", "title": "Create File", "desc": "Generate new files"},
            {"icon": "🔍", "title": "Search Files", "desc": "Find files by pattern"},
            {"icon": "⚡", "title": "Run Command", "desc": "Execute PowerShell"}
        ]
        
        # First row
        row1 = ctk.CTkFrame(cards_container, fg_color="transparent")
        row1.pack(pady=SPACING["xs"])
        
        for suggestion in suggestions[:2]:
            self._create_suggestion_card(row1, suggestion)
        
        # Second row
        row2 = ctk.CTkFrame(cards_container, fg_color="transparent")
        row2.pack(pady=SPACING["xs"])
        
        for suggestion in suggestions[2:]:
            self._create_suggestion_card(row2, suggestion)
    
    def _create_suggestion_card(self, parent, suggestion: dict):
        """Create a styled suggestion card."""
        card = ctk.CTkButton(
            parent,
            text="",
            fg_color="#1E293B",
            hover_color="#334155",
            width=200,
            height=80,
            corner_radius=12,
            command=lambda: self._on_suggestion(suggestion["title"])
        )
        card.pack(side="left", padx=SPACING["xs"])
        
        # Card content frame
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Icon and text
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack()
        
        icon = ctk.CTkLabel(
            top_row,
            text=suggestion["icon"],
            font=("Segoe UI Emoji", 20),
            text_color="#FFFFFF"
        )
        icon.pack(side="left", padx=(0, 8))
        
        title = ctk.CTkLabel(
            top_row,
            text=suggestion["title"],
            font=("Segoe UI", 14, "bold"),
            text_color="#FFFFFF"
        )
        title.pack(side="left")
        
        desc = ctk.CTkLabel(
            content,
            text=suggestion["desc"],
            font=("Segoe UI", 11),
            text_color="#9CA3AF"
        )
        desc.pack(pady=(4, 0))
    
    def _on_suggestion(self, text: str):
        if self.on_suggestion:
            self.on_suggestion(text)


class ChatInput(ctk.CTkFrame):
    """Professional chat input with send button."""
    
    def __init__(
        self,
        master,
        on_send: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0,
            **kwargs
        )
        
        self.on_send = on_send
        
        # Inner container with padding
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.pack(fill="x", padx=SPACING["lg"], pady=SPACING["md"])
        
        # Input container with border
        input_container = ctk.CTkFrame(
            inner,
            fg_color=COLORS["bg_input"],
            corner_radius=RADIUS["xl"],
            border_width=1,
            border_color=COLORS["border"]
        )
        input_container.pack(fill="x")
        
        # Text input
        self.text_input = ctk.CTkEntry(
            input_container,
            font=(FONTS["family"], FONTS["size_body"]),
            fg_color="transparent",
            text_color=COLORS["text_primary"],
            placeholder_text="Message Gemini Cowork...",
            placeholder_text_color=COLORS["text_tertiary"],
            border_width=0,
            height=48
        )
        self.text_input.pack(side="left", fill="x", expand=True, padx=SPACING["md"])
        self.text_input.bind("<Return>", self._on_enter)
        self.text_input.bind("<FocusIn>", self._on_focus_in)
        self.text_input.bind("<FocusOut>", self._on_focus_out)
        
        # Send button
        self.send_btn = ctk.CTkButton(
            input_container,
            text="➤",
            font=(FONTS["family"], 18),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_on_accent"],
            width=40,
            height=40,
            corner_radius=RADIUS["full"],
            command=self._send
        )
        self.send_btn.pack(side="right", padx=SPACING["xs"], pady=SPACING["xs"])
        
        self.input_container = input_container
    
    def _on_enter(self, event):
        self._send()
        return "break"
    
    def _on_focus_in(self, event):
        self.input_container.configure(border_color=COLORS["border_focus"])
    
    def _on_focus_out(self, event):
        self.input_container.configure(border_color=COLORS["border"])
    
    def _send(self):
        text = self.text_input.get().strip()
        if text and self.on_send:
            self.on_send(text)
            self.text_input.delete(0, "end")
    
    def get_text(self) -> str:
        return self.text_input.get().strip()
    
    def clear(self):
        self.text_input.delete(0, "end")
    
    def set_enabled(self, enabled: bool):
        if enabled:
            self.text_input.configure(state="normal")
            self.send_btn.configure(state="normal")
        else:
            self.text_input.configure(state="disabled")
            self.send_btn.configure(state="disabled")
    
    def focus(self):
        self.text_input.focus_set()


class ChatInterface(ctk.CTkFrame):
    """Main chat interface component."""
    
    def __init__(
        self,
        master,
        on_workspace_needed: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_primary"],
            corner_radius=0,
            **kwargs
        )
        
        self.on_workspace_needed = on_workspace_needed
        self.messages: List[Dict[str, Any]] = []
        self.typing_indicator = None
        self.current_ai_bubble = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        # Header
        header = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            height=SIZES["header_height"],
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Model indicator
        model_frame = ctk.CTkFrame(header, fg_color="transparent")
        model_frame.pack(side="left", padx=SPACING["lg"], pady=SPACING["sm"])
        
        model_icon = ctk.CTkLabel(
            model_frame,
            text="✦",
            font=(FONTS["family"], 16),
            text_color=COLORS["gemini_blue"]
        )
        model_icon.pack(side="left")
        
        model_name = session_service.get_model_name() or "gemini-2.0-flash"
        model_label = ctk.CTkLabel(
            model_frame,
            text=model_name,
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        model_label.pack(side="left", padx=SPACING["xs"])
        
        # Messages area (scrollable)
        self.messages_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"]
        )
        self.messages_frame.pack(fill="both", expand=True)
        
        # Welcome screen
        self.welcome_screen = WelcomeScreen(self.messages_frame)
        self.welcome_screen.pack(fill="both", expand=True)
        self.welcome_screen.on_suggestion = self._on_suggestion
        
        # Input area
        self.chat_input = ChatInput(self, on_send=self._on_send)
        self.chat_input.pack(fill="x", side="bottom")
    
    def _on_suggestion(self, text: str):
        """Handle suggestion chip click."""
        self._on_send(text)
    
    def _on_send(self, text: str):
        """Handle sending a message."""
        if not text.strip():
            return
        
        # Clear input immediately
        self.chat_input.clear()
        
        # Check if Gemini is configured
        if not gemini_service.is_configured():
            self._add_system_message("Please configure your API key in Settings first.")
            return
        
        # Hide welcome screen
        self.welcome_screen.pack_forget()
        
        # Add user message
        self._add_message("user", text)
        
        # Show typing indicator
        self._show_typing()
        
        # Disable input while processing
        self.chat_input.set_enabled(False)
        
        # Process in background
        thread = threading.Thread(target=self._process_message, args=(text,), daemon=True)
        thread.start()
    
    def _process_message(self, text: str):
        """Process message in background thread."""
        try:
            ai_content = ""
            tool_calls = []
            
            for event in gemini_service.send_message(text):
                event_type = event.get("type")
                
                if event_type == "text":
                    ai_content += event.get("content", "")
                    # Update UI - copy current values to avoid closure issues
                    content_copy = ai_content
                    tools_copy = list(tool_calls)
                    self.after(0, lambda c=content_copy, t=tools_copy: self._update_ai_response(c, t))
                
                elif event_type == "tool_call":
                    tool = event.get("tool")
                    if tool:
                        tool_calls.append({
                            "name": tool.name,
                            "args": tool.args,
                            "status": "running"
                        })
                        content_copy = ai_content
                        tools_copy = list(tool_calls)
                        self.after(0, lambda c=content_copy, t=tools_copy: self._update_ai_response(c, t))
                
                elif event_type == "tool_result":
                    tool = event.get("tool")
                    if tool and tool_calls:
                        for tc in tool_calls:
                            if tc["name"] == tool.name:
                                tc["status"] = "success" if tool.result.get("success") else "error"
                                tc["result"] = tool.result
                        content_copy = ai_content
                        tools_copy = list(tool_calls)
                        self.after(0, lambda c=content_copy, t=tools_copy: self._update_ai_response(c, t))
                
                elif event_type == "error":
                    error = event.get("error", "Unknown error")
                    error_copy = str(error)
                    self.after(0, lambda e=error_copy: self._add_system_message(f"Error: {e}"))
                
                elif event_type == "done":
                    pass
            
            # Finalize response
            if ai_content or tool_calls:
                content_copy = ai_content
                tools_copy = list(tool_calls)
                self.after(0, lambda c=content_copy, t=tools_copy: self._finalize_response(c, t))
        
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: self._add_system_message(f"Error: {msg}"))
        
        finally:
            self.after(0, self._reset_input)
    
    def _add_message(self, role: str, content: str, tool_calls: List = None):
        """Add a message bubble."""
        msg = {"role": role, "content": content, "tool_calls": tool_calls or []}
        self.messages.append(msg)
        
        bubble = MessageBubble(
            self.messages_frame,
            role=role,
            content=content,
            tool_calls=tool_calls
        )
        bubble.pack(fill="x", anchor="e" if role == "user" else "w")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def _add_system_message(self, text: str):
        """Add a system/error message."""
        frame = ctk.CTkFrame(self.messages_frame, fg_color="transparent")
        frame.pack(fill="x", pady=SPACING["sm"])
        
        label = ctk.CTkLabel(
            frame,
            text=text,
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["warning"],
            wraplength=500
        )
        label.pack(padx=SPACING["lg"])
    
    def _show_typing(self):
        """Show typing indicator."""
        if self.typing_indicator:
            self.typing_indicator.destroy()
        
        self.typing_indicator = TypingIndicator(self.messages_frame)
        self.typing_indicator.pack(fill="x")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def _hide_typing(self):
        """Hide typing indicator."""
        if self.typing_indicator:
            self.typing_indicator.destroy()
            self.typing_indicator = None
    
    def _update_ai_response(self, content: str, tool_calls: List):
        """Update the current AI response (streaming)."""
        self._hide_typing()
        
        if self.current_ai_bubble:
            self.current_ai_bubble.destroy()
        
        self.current_ai_bubble = MessageBubble(
            self.messages_frame,
            role="ai",
            content=content,
            tool_calls=tool_calls
        )
        self.current_ai_bubble.pack(fill="x", anchor="w")
        
        # Scroll to bottom
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def _finalize_response(self, content: str, tool_calls: List):
        """Finalize the AI response."""
        self._hide_typing()
        
        # Store in messages
        msg = {"role": "ai", "content": content, "tool_calls": tool_calls}
        self.messages.append(msg)
    
    def _reset_input(self):
        """Reset input state."""
        self._hide_typing()
        self.chat_input.set_enabled(True)
        self.chat_input.focus()
    
    def hide_workspace_reminder(self):
        """Hide the workspace reminder if shown."""
        pass
    
    def new_chat(self):
        """Start a new chat."""
        # Clear messages
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        self.messages = []
        self.current_ai_bubble = None
        
        # Show welcome screen
        self.welcome_screen = WelcomeScreen(self.messages_frame)
        self.welcome_screen.pack(fill="both", expand=True)
        self.welcome_screen.on_suggestion = self._on_suggestion
        
        # Clear Gemini history
        gemini_service.clear_history()
