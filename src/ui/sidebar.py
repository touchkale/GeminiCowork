# Sidebar Component
"""
Professional sidebar with workspace management and chat history.
Google Material Design 3 inspired.
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Optional, Callable, List

from .theme import COLORS, FONTS, SPACING, RADIUS, SIZES, ICONS, get_button_style
from ..services.session_service import session_service
from ..services.file_service import file_service


class IconButton(ctk.CTkButton):
    """A minimal icon button for the sidebar."""
    
    def __init__(self, master, icon: str, tooltip: str = "", **kwargs):
        defaults = {
            "text": icon,
            "font": (FONTS["family"], 16),
            "width": 40,
            "height": 40,
            "corner_radius": RADIUS["sm"],
            "fg_color": "transparent",
            "hover_color": COLORS["bg_elevated"],
            "text_color": COLORS["text_secondary"],
        }
        defaults.update(kwargs)
        super().__init__(master, **defaults)


class SidebarSection(ctk.CTkFrame):
    """A collapsible section in the sidebar."""
    
    def __init__(
        self, 
        master, 
        title: str,
        icon: str = "",
        collapsed: bool = False,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.collapsed = collapsed
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        header.pack(fill="x", pady=(SPACING["sm"], 0))
        header.pack_propagate(False)
        
        # Title with icon
        title_text = f"{icon}  {title}" if icon else title
        self.title_label = ctk.CTkLabel(
            header,
            text=title_text,
            font=(FONTS["family"], FONTS["size_small"], "bold"),
            text_color=COLORS["text_tertiary"],
            anchor="w"
        )
        self.title_label.pack(side="left", padx=SPACING["md"])
        
        # Content container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        if not collapsed:
            self.content.pack(fill="x", pady=SPACING["xs"])
    
    def toggle(self):
        """Toggle section visibility."""
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.content.pack_forget()
        else:
            self.content.pack(fill="x", pady=SPACING["xs"])


class WorkspaceItem(ctk.CTkFrame):
    """A workspace folder item."""
    
    def __init__(
        self,
        master,
        path: str,
        on_remove: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master, 
            fg_color="transparent",
            height=36,
            **kwargs
        )
        self.pack_propagate(False)
        
        self.path = path
        
        # Folder icon
        icon_label = ctk.CTkLabel(
            self,
            text=ICONS["folder"],
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=COLORS["text_secondary"],
            width=24
        )
        icon_label.pack(side="left", padx=(SPACING["md"], SPACING["xs"]))
        
        # Folder name (just the last part)
        folder_name = path.split("\\")[-1] if "\\" in path else path.split("/")[-1]
        name_label = ctk.CTkLabel(
            self,
            text=folder_name,
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True, padx=SPACING["xs"])
        
        # Remove button (appears on hover)
        if on_remove:
            remove_btn = ctk.CTkButton(
                self,
                text=ICONS["close"],
                width=24,
                height=24,
                font=(FONTS["family"], 10),
                fg_color="transparent",
                hover_color=COLORS["error"],
                text_color=COLORS["text_tertiary"],
                corner_radius=RADIUS["xs"],
                command=lambda: on_remove(path)
            )
            remove_btn.pack(side="right", padx=SPACING["sm"])


class ChatHistoryItem(ctk.CTkFrame):
    """A chat history item."""
    
    def __init__(
        self,
        master,
        session_id: str,
        title: str,
        on_click: Optional[Callable] = None,
        on_delete: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color="transparent",
            height=40,
            corner_radius=RADIUS["sm"],
            **kwargs
        )
        self.pack_propagate(False)
        
        self.session_id = session_id
        self.on_click = on_click
        
        # Make entire frame clickable
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        # Chat icon
        icon_label = ctk.CTkLabel(
            self,
            text=ICONS["chat"],
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_secondary"],
            width=20
        )
        icon_label.pack(side="left", padx=(SPACING["md"], SPACING["xs"]))
        icon_label.bind("<Button-1>", self._handle_click)
        
        # Title (truncated)
        display_title = title[:25] + "..." if len(title) > 25 else title
        self.title_label = ctk.CTkLabel(
            self,
            text=display_title,
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_primary"],
            anchor="w"
        )
        self.title_label.pack(side="left", fill="x", expand=True, padx=SPACING["xs"])
        self.title_label.bind("<Button-1>", self._handle_click)
        
        # Delete button
        if on_delete:
            delete_btn = ctk.CTkButton(
                self,
                text=ICONS["delete"],
                width=24,
                height=24,
                font=(FONTS["family"], 10),
                fg_color="transparent",
                hover_color=COLORS["error"],
                text_color=COLORS["text_tertiary"],
                corner_radius=RADIUS["xs"],
                command=lambda: on_delete(session_id)
            )
            delete_btn.pack(side="right", padx=SPACING["xs"])
    
    def _handle_click(self, event=None):
        if self.on_click:
            self.on_click(self.session_id)
    
    def _on_enter(self, event=None):
        self.configure(fg_color=COLORS["bg_elevated"])
    
    def _on_leave(self, event=None):
        self.configure(fg_color="transparent")


class Sidebar(ctk.CTkFrame):
    """Professional sidebar component."""
    
    def __init__(
        self,
        master,
        on_workspace_change: Optional[Callable] = None,
        on_session_load: Optional[Callable] = None,
        on_settings_click: Optional[Callable] = None,
        on_new_chat: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=COLORS["bg_secondary"],
            width=SIZES["sidebar_width"],
            corner_radius=0,
            **kwargs
        )
        self.pack_propagate(False)
        
        self.on_workspace_change = on_workspace_change
        self.on_session_load = on_session_load
        self.on_settings_click = on_settings_click
        self.on_new_chat = on_new_chat
        
        self._create_widgets()
        self._load_data()
    
    def _create_widgets(self):
        # Header with logo
        header = ctk.CTkFrame(self, fg_color="transparent", height=SIZES["header_height"])
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Gemini logo/brand
        brand_frame = ctk.CTkFrame(header, fg_color="transparent")
        brand_frame.pack(side="left", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Gemini icon with gradient effect (using text)
        logo_label = ctk.CTkLabel(
            brand_frame,
            text="✦",
            font=(FONTS["family"], 24),
            text_color=COLORS["gemini_blue"]
        )
        logo_label.pack(side="left")
        
        app_name = ctk.CTkLabel(
            brand_frame,
            text="Gemini Cowork",
            font=(FONTS["family"], FONTS["size_title"], "bold"),
            text_color=COLORS["text_primary"]
        )
        app_name.pack(side="left", padx=(SPACING["xs"], 0))
        
        # New chat button
        new_chat_btn = ctk.CTkButton(
            self,
            text="+ New Chat",
            font=(FONTS["family"], FONTS["size_body"]),
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text_primary"],
            height=42,
            corner_radius=RADIUS["full"],
            command=self._new_chat
        )
        new_chat_btn.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Divider
        divider = ctk.CTkFrame(self, fg_color=COLORS["border_subtle"], height=1)
        divider.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Scrollable content
        scroll_content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"],
            scrollbar_button_hover_color=COLORS["scrollbar_hover"]
        )
        scroll_content.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Workspaces section
        self.workspaces_section = SidebarSection(scroll_content, "WORKSPACES", ICONS["folder"])
        self.workspaces_section.pack(fill="x")
        
        self.workspaces_container = self.workspaces_section.content
        
        # Add workspace button
        add_ws_btn = ctk.CTkButton(
            self.workspaces_container,
            text="+ Add folder",
            font=(FONTS["family"], FONTS["size_small"]),
            fg_color="transparent",
            hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text_secondary"],
            height=32,
            anchor="w",
            command=self._add_workspace
        )
        add_ws_btn.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])
        
        # Recent chats section
        self.history_section = SidebarSection(scroll_content, "RECENT", ICONS["chat"])
        self.history_section.pack(fill="x", pady=SPACING["md"])
        
        self.history_container = self.history_section.content
        
        # Bottom actions
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent", height=110)
        bottom_frame.pack(fill="x", side="bottom")
        bottom_frame.pack_propagate(False)
        
        # Divider
        divider2 = ctk.CTkFrame(bottom_frame, fg_color=COLORS["border_subtle"], height=1)
        divider2.pack(fill="x")
        
        # Autonomy mode toggle
        mode_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=SPACING["md"], pady=(SPACING["sm"], 0))
        
        mode_label = ctk.CTkLabel(
            mode_frame,
            text="Supervised Mode",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        mode_label.pack(side="left")
        
        # Get current mode
        is_supervised = session_service.is_supervised_mode()
        self.mode_var = ctk.BooleanVar(value=is_supervised)
        
        mode_switch = ctk.CTkSwitch(
            mode_frame,
            text="",
            variable=self.mode_var,
            onvalue=True,
            offvalue=False,
            fg_color=COLORS["bg_elevated"],
            progress_color=COLORS["accent_primary"],
            button_color=COLORS["text_primary"],
            button_hover_color=COLORS["accent_hover"],
            width=40,
            command=self._toggle_mode
        )
        mode_switch.pack(side="right")
        
        # Mode description
        mode_desc = ctk.CTkLabel(
            bottom_frame,
            text="Ask before each action" if is_supervised else "Auto-run safe actions",
            font=(FONTS["family"], FONTS["size_tiny"]),
            text_color=COLORS["text_tertiary"]
        )
        mode_desc.pack(anchor="w", padx=SPACING["md"])
        self.mode_desc_label = mode_desc
        
        # Settings button
        settings_btn = ctk.CTkButton(
            bottom_frame,
            text=f"{ICONS['settings']}  Settings",
            font=(FONTS["family"], FONTS["size_body"]),
            fg_color="transparent",
            hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text_secondary"],
            height=44,
            anchor="w",
            command=self._open_settings
        )
        settings_btn.pack(fill="x", padx=SPACING["sm"], pady=SPACING["xs"])
    
    def _load_data(self):
        """Load workspaces and chat history."""
        self._load_workspaces()
        self._load_sessions()
    
    def _load_workspaces(self):
        """Load workspace items."""
        # Clear existing (except add button)
        for widget in list(self.workspaces_container.winfo_children()):
            if isinstance(widget, WorkspaceItem):
                widget.destroy()
        
        # Add workspace items
        for path in session_service.get_workspaces():
            item = WorkspaceItem(
                self.workspaces_container,
                path,
                on_remove=self._remove_workspace
            )
            item.pack(fill="x", pady=1)
    
    def _load_sessions(self):
        """Load chat history."""
        # Clear existing
        for widget in list(self.history_container.winfo_children()):
            widget.destroy()
        
        # Add session items
        sessions = session_service.list_sessions()[:10]  # Show last 10
        
        if not sessions:
            empty_label = ctk.CTkLabel(
                self.history_container,
                text="No recent chats",
                font=(FONTS["family"], FONTS["size_small"]),
                text_color=COLORS["text_tertiary"]
            )
            empty_label.pack(pady=SPACING["md"])
        else:
            for session in sessions:
                item = ChatHistoryItem(
                    self.history_container,
                    session["id"],
                    session["title"],
                    on_click=self._load_session,
                    on_delete=self._delete_session
                )
                item.pack(fill="x", pady=1)
    
    def _add_workspace(self):
        """Add a new workspace folder."""
        folder = filedialog.askdirectory(title="Select Workspace Folder")
        if folder:
            session_service.add_workspace(folder)
            file_service.add_workspace(folder)
            self._load_workspaces()
            if self.on_workspace_change:
                self.on_workspace_change()
    
    def _remove_workspace(self, path: str):
        """Remove a workspace folder."""
        session_service.remove_workspace(path)
        file_service.remove_workspace(path)
        self._load_workspaces()
        if self.on_workspace_change:
            self.on_workspace_change()
    
    def _load_session(self, session_id: str):
        """Load a chat session."""
        if self.on_session_load:
            self.on_session_load(session_id)
    
    def _delete_session(self, session_id: str):
        """Delete a chat session."""
        session_service.delete_session(session_id)
        self._load_sessions()
    
    def _new_chat(self):
        """Start a new chat."""
        if self.on_new_chat:
            self.on_new_chat()
    
    def _open_settings(self):
        """Open settings dialog."""
        if self.on_settings_click:
            self.on_settings_click()
    
    def refresh(self):
        """Refresh sidebar data."""
        self._load_data()
    
    def has_workspaces(self) -> bool:
        """Check if any workspaces are configured."""
        return len(session_service.get_workspaces()) > 0
    
    def _toggle_mode(self):
        """Toggle between autonomous and supervised mode."""
        is_supervised = self.mode_var.get()
        mode = "supervised" if is_supervised else "autonomous"
        session_service.set_autonomy_mode(mode)
        
        # Update description text
        desc = "Ask before each action" if is_supervised else "Auto-run safe actions"
        self.mode_desc_label.configure(text=desc)
