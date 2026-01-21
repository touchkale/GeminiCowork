# Settings Dialog
"""
Professional settings dialog with Google Material Design styling.
"""

import customtkinter as ctk
from typing import Optional, Callable, List
import threading

from .theme import COLORS, FONTS, SPACING, RADIUS, SIZES, ICONS, get_button_style
from ..services.session_service import session_service
from ..services.gemini_service import gemini_service

# Try to import genai for model listing
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None


def fetch_available_models(api_key: str) -> List[str]:
    """Fetch available models from the Gemini API."""
    if not GENAI_AVAILABLE or not api_key:
        return get_default_models()
    
    try:
        genai.configure(api_key=api_key)
        models = []
        for model in genai.list_models():
            try:
                supported = getattr(model, 'supported_generation_methods', [])
                if 'generateContent' in supported:
                    name = getattr(model, 'name', '')
                    if name:
                        models.append(name.replace('models/', ''))
            except Exception:
                continue
        
        return sorted(models) if models else get_default_models()
    except Exception as e:
        print(f"Error fetching models: {e}")
        return get_default_models()


def get_default_models() -> List[str]:
    """Get default model list."""
    return [
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-1.0-pro"
    ]


class SettingsDialog(ctk.CTkToplevel):
    """Professional settings dialog."""
    
    def __init__(
        self,
        master,
        on_save: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_save = on_save
        self.available_models = get_default_models()
        
        # Window configuration
        self.title("Settings")
        self.geometry("520x480")
        self.configure(fg_color=COLORS["bg_primary"])
        self.resizable(False, False)
        
        # Center on parent
        self.transient(master)
        self.grab_set()
        
        self._create_widgets()
        self._load_settings()
        
        # Focus
        self.after(100, self.api_key_entry.focus_set)
    
    def _create_widgets(self):
        # Header (simple, no extra close button since window has one)
        header = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            height=56,
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="Settings",
            font=(FONTS["family"], FONTS["size_heading"], "bold"),
            text_color=COLORS["text_primary"]
        ).pack(side="left", padx=SPACING["lg"], pady=SPACING["md"])
        
        # Content area
        content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS["scrollbar"]
        )
        content.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["md"])
        
        # API Key Section
        self._create_section(content, "API Configuration", [
            self._create_api_key_field,
            self._create_model_selector
        ])
        
        # About Section
        self._create_about_section(content)
        
        # Bottom action bar
        action_bar = ctk.CTkFrame(
            self,
            fg_color=COLORS["bg_secondary"],
            height=70,
            corner_radius=0
        )
        action_bar.pack(fill="x", side="bottom")
        action_bar.pack_propagate(False)
        
        action_content = ctk.CTkFrame(action_bar, fg_color="transparent")
        action_content.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["md"])
        
        # Status label
        self.status_label = ctk.CTkLabel(
            action_content,
            text="",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(side="left")
        
        # Save button
        self.save_btn = ctk.CTkButton(
            action_content,
            text="Save Changes",
            font=(FONTS["family"], FONTS["size_body"], "bold"),
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["text_on_accent"],
            width=140,
            height=44,
            corner_radius=RADIUS["sm"],
            command=self._save
        )
        self.save_btn.pack(side="right")
    
    def _create_section(self, parent, title: str, field_creators: list):
        """Create a settings section."""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"]
        )
        section.pack(fill="x", pady=SPACING["sm"])
        
        # Section title
        ctk.CTkLabel(
            section,
            text=title,
            font=(FONTS["family"], FONTS["size_title"], "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=SPACING["md"], pady=(SPACING["md"], SPACING["sm"]))
        
        # Fields
        for creator in field_creators:
            creator(section)
    
    def _create_api_key_field(self, parent):
        """Create API key input field."""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        # Label
        ctk.CTkLabel(
            field_frame,
            text="Gemini API Key",
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")
        
        # Input row
        input_row = ctk.CTkFrame(field_frame, fg_color="transparent")
        input_row.pack(fill="x", pady=SPACING["xs"])
        
        self.api_key_entry = ctk.CTkEntry(
            input_row,
            font=(FONTS["family_mono"], FONTS["size_body"]),
            fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            border_color=COLORS["border"],
            border_width=1,
            placeholder_text="Enter your API key...",
            show="•",
            height=44,
            corner_radius=RADIUS["sm"]
        )
        self.api_key_entry.pack(side="left", fill="x", expand=True, padx=(0, SPACING["sm"]))
        
        # Connect button
        self.connect_btn = ctk.CTkButton(
            input_row,
            text="Test",
            font=(FONTS["family"], FONTS["size_body"]),
            fg_color=COLORS["bg_tertiary"],
            hover_color=COLORS["bg_elevated"],
            text_color=COLORS["text_primary"],
            width=80,
            height=44,
            corner_radius=RADIUS["sm"],
            command=self._test_connection
        )
        self.connect_btn.pack(side="right")
        
        # Show key toggle
        self.show_key = ctk.BooleanVar(value=False)
        show_check = ctk.CTkCheckBox(
            field_frame,
            text="Show API key",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_tertiary"],
            fg_color=COLORS["accent_primary"],
            hover_color=COLORS["accent_hover"],
            variable=self.show_key,
            command=self._toggle_key_visibility,
            height=24
        )
        show_check.pack(anchor="w", pady=(SPACING["xs"], 0))
        
        # Help text
        ctk.CTkLabel(
            field_frame,
            text="Get your API key from Google AI Studio",
            font=(FONTS["family"], FONTS["size_tiny"]),
            text_color=COLORS["text_tertiary"]
        ).pack(anchor="w", pady=(SPACING["xs"], SPACING["sm"]))
    
    def _create_model_selector(self, parent):
        """Create model selection dropdown."""
        field_frame = ctk.CTkFrame(parent, fg_color="transparent")
        field_frame.pack(fill="x", padx=SPACING["md"], pady=SPACING["sm"])
        
        ctk.CTkLabel(
            field_frame,
            text="AI Model",
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")
        
        self.model_var = ctk.StringVar(value="gemini-2.0-flash")
        
        # Improved dropdown with better visibility
        self.model_dropdown = ctk.CTkOptionMenu(
            field_frame,
            values=self.available_models,
            variable=self.model_var,
            font=(FONTS["family"], FONTS["size_body"]),
            fg_color=COLORS["bg_tertiary"],
            button_color=COLORS["accent_primary"],
            button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_tertiary"],
            dropdown_hover_color=COLORS["accent_primary"],
            dropdown_text_color=COLORS["text_primary"],
            text_color=COLORS["text_primary"],
            width=320,
            height=44,
            corner_radius=RADIUS["sm"],
            dynamic_resizing=False
        )
        self.model_dropdown.pack(anchor="w", pady=SPACING["xs"])
        
        ctk.CTkLabel(
            field_frame,
            text="Select the AI model for conversations",
            font=(FONTS["family"], FONTS["size_tiny"]),
            text_color=COLORS["text_tertiary"]
        ).pack(anchor="w", pady=(0, SPACING["md"]))
    
    def _create_about_section(self, parent):
        """Create about section."""
        section = ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["md"]
        )
        section.pack(fill="x", pady=SPACING["sm"])
        
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=SPACING["md"], pady=SPACING["md"])
        
        # App info
        ctk.CTkLabel(
            content,
            text="Gemini Cowork",
            font=(FONTS["family"], FONTS["size_title"], "bold"),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content,
            text="Version 1.0.0",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            content,
            text="AI-powered coding assistant using Google Gemini",
            font=(FONTS["family"], FONTS["size_small"]),
            text_color=COLORS["text_tertiary"]
        ).pack(anchor="w", pady=(SPACING["xs"], 0))
    
    def _toggle_key_visibility(self):
        """Toggle API key visibility."""
        self.api_key_entry.configure(show="" if self.show_key.get() else "•")
    
    def _load_settings(self):
        """Load current settings."""
        session_service.config = session_service._load_config()
        
        api_key = session_service.get_api_key()
        if api_key:
            self.api_key_entry.delete(0, "end")
            self.api_key_entry.insert(0, api_key)
        
        model = session_service.get_model_name()
        if model and model in self.available_models:
            self.model_var.set(model)
    
    def _test_connection(self):
        """Test API connection and fetch models."""
        api_key = self.api_key_entry.get().strip()
        
        if not api_key:
            self._show_status("Please enter an API key", "error")
            return
        
        self.connect_btn.configure(state="disabled", text="...")
        self._show_status("Testing connection...", "info")
        
        def test():
            models = fetch_available_models(api_key)
            self.after(0, lambda: self._on_test_complete(models))
        
        thread = threading.Thread(target=test, daemon=True)
        thread.start()
    
    def _on_test_complete(self, models: List[str]):
        """Handle test completion."""
        self.connect_btn.configure(state="normal", text="Test")
        
        if models:
            self.available_models = models
            self.model_dropdown.configure(values=models)
            
            current = self.model_var.get()
            if current not in models:
                self.model_var.set(models[0])
            
            self._show_status(f"Connected! Found {len(models)} models", "success")
        else:
            self._show_status("Connection failed", "error")
    
    def _show_status(self, message: str, status_type: str = "info"):
        """Show status message."""
        colors = {
            "info": COLORS["text_secondary"],
            "success": COLORS["success"],
            "error": COLORS["error"],
            "warning": COLORS["warning"]
        }
        self.status_label.configure(
            text=message,
            text_color=colors.get(status_type, COLORS["text_secondary"])
        )
    
    def _save(self):
        """Save settings."""
        api_key = self.api_key_entry.get().strip()
        model = self.model_var.get()
        
        if not api_key:
            self._show_status("Please enter an API key", "error")
            return
        
        self.save_btn.configure(state="disabled", text="Saving...")
        
        # Save to session service
        session_service.set_api_key(api_key)
        session_service.set_model_name(model)
        session_service.save_config()
        
        # Configure Gemini
        result = gemini_service.configure(api_key, model)
        
        if result.get("success"):
            self._show_status("Settings saved!", "success")
            
            if self.on_save:
                self.on_save()
            
            self.after(500, self.destroy)
        else:
            error = result.get("error", "Unknown error")
            self._show_status(f"Error: {error[:40]}", "error")
            self.save_btn.configure(state="normal", text="Save Changes")


class ApprovalDialog(ctk.CTkToplevel):
    """Dialog for approving destructive actions."""
    
    def __init__(
        self,
        master,
        action_type: str,
        action_details: str,
        on_approve: Optional[Callable] = None,
        on_deny: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.on_approve = on_approve
        self.on_deny = on_deny
        self.result = False
        
        # Window configuration
        self.title("Approval Required")
        self.geometry("520x300")
        self.configure(fg_color=COLORS["bg_primary"])
        self.resizable(False, False)
        
        self.transient(master)
        self.grab_set()
        
        self._create_widgets(action_type, action_details)
        self.protocol("WM_DELETE_WINDOW", self._deny)
    
    def _create_widgets(self, action_type: str, action_details: str):
        # Warning header
        header = ctk.CTkFrame(
            self,
            fg_color=COLORS["warning"],
            height=56,
            corner_radius=0
        )
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="⚠  Action Requires Approval",
            font=(FONTS["family"], FONTS["size_title"], "bold"),
            text_color=COLORS["bg_primary"]
        ).pack(side="left", padx=SPACING["lg"], pady=SPACING["md"])
        
        # Content
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=SPACING["lg"], pady=SPACING["md"])
        
        ctk.CTkLabel(
            content,
            text=f"The AI wants to perform: {action_type}",
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=COLORS["text_primary"]
        ).pack(anchor="w", pady=SPACING["xs"])
        
        # Details box
        details_frame = ctk.CTkFrame(
            content,
            fg_color=COLORS["bg_secondary"],
            corner_radius=RADIUS["sm"]
        )
        details_frame.pack(fill="x", pady=SPACING["sm"])
        
        ctk.CTkLabel(
            details_frame,
            text=action_details,
            font=(FONTS["family_mono"], FONTS["size_small"]),
            text_color=COLORS["text_accent"],
            wraplength=400,
            justify="left"
        ).pack(padx=SPACING["md"], pady=SPACING["md"], anchor="w")
        
        ctk.CTkLabel(
            content,
            text="Do you want to allow this action?",
            font=(FONTS["family"], FONTS["size_body"]),
            text_color=COLORS["text_secondary"]
        ).pack(anchor="w", pady=SPACING["xs"])
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent", height=60)
        button_frame.pack(fill="x", side="bottom", padx=SPACING["lg"], pady=SPACING["md"])
        button_frame.pack_propagate(False)
        
        deny_btn = ctk.CTkButton(
            button_frame,
            text="DENY",
            font=(FONTS["family"], FONTS["size_body"], "bold"),
            fg_color=COLORS["error"],
            hover_color="#C62828",
            text_color="#FFFFFF",
            width=150,
            height=44,
            corner_radius=RADIUS["sm"],
            command=self._deny
        )
        deny_btn.pack(side="left", expand=True, padx=SPACING["sm"])
        
        approve_btn = ctk.CTkButton(
            button_frame,
            text="APPROVE",
            font=(FONTS["family"], FONTS["size_body"], "bold"),
            fg_color=COLORS["success"],
            hover_color="#2E7D32",
            text_color="#FFFFFF",
            width=150,
            height=44,
            corner_radius=RADIUS["sm"],
            command=self._approve
        )
        approve_btn.pack(side="right", expand=True, padx=SPACING["sm"])
    
    def _approve(self):
        self.result = True
        if self.on_approve:
            self.on_approve()
        self.destroy()
    
    def _deny(self):
        self.result = False
        if self.on_deny:
            self.on_deny()
        self.destroy()
    
    def wait_for_result(self) -> bool:
        self.wait_window()
        return self.result
