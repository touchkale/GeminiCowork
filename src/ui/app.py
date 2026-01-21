# Main Application Window
"""
Main application window for Gemini Cowork.
Professional Google-style interface.
"""

import customtkinter as ctk
from typing import Optional
import threading

from .theme import COLORS, FONTS, SPACING, RADIUS, SIZES, WINDOW
from .sidebar import Sidebar
from .chat_view import ChatInterface
from .dialogs import SettingsDialog, ApprovalDialog
from ..services.session_service import session_service
from ..services.gemini_service import gemini_service, ToolCall
from ..services.file_service import file_service


class GeminiCoworkApp(ctk.CTk):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Gemini Cowork")
        self.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.minsize(WINDOW['min_width'], WINDOW['min_height'])
        
        # Set dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure window colors
        self.configure(fg_color=COLORS["bg_primary"])
        
        # Set window icon (if available)
        try:
            self.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Initialize services
        self._init_services()
        
        # Create UI
        self._create_widgets()
        
        # Set up approval callback
        self._setup_approval()
        
        # Check if API key is configured
        self.after(500, self._check_configuration)
    
    def _init_services(self):
        """Initialize backend services."""
        # Force reload config from file
        session_service.config = session_service._load_config()
        
        # Load config and configure Gemini if API key exists
        api_key = session_service.get_api_key()
        model = session_service.get_model_name()
        
        print(f"Loaded config - API key present: {bool(api_key)}, Model: {model}")
        
        if api_key:
            result = gemini_service.configure(api_key, model)
            print(f"Gemini configuration result: {result}")
        
        # Load workspaces into file service
        for workspace in session_service.get_workspaces():
            file_service.add_workspace(workspace)
    
    def _create_widgets(self):
        """Create the main UI layout."""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = Sidebar(
            main_container,
            on_workspace_change=self._on_workspace_change,
            on_session_load=self._on_session_load,
            on_settings_click=self._open_settings,
            on_new_chat=self._on_new_chat
        )
        self.sidebar.pack(side="left", fill="y")
        
        # Main content area
        content = ctk.CTkFrame(main_container, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True)
        
        # Chat interface
        self.chat = ChatInterface(
            content,
            on_workspace_needed=self._open_folder_picker
        )
        self.chat.pack(fill="both", expand=True)
    
    def _setup_approval(self):
        """Set up the approval callback for destructive actions."""
        def approval_callback(tool_call: ToolCall) -> bool:
            # This needs to run on the main thread
            result = [False]
            event = threading.Event()
            
            def show_dialog():
                # Determine action type and details
                if tool_call.name == "run_command":
                    action_type = "command execution"
                    details = tool_call.args.get("command", "Unknown command")
                elif tool_call.name == "delete_file":
                    action_type = "file deletion"
                    details = tool_call.args.get("path", "Unknown file")
                else:
                    action_type = tool_call.name
                    details = str(tool_call.args)
                
                dialog = ApprovalDialog(
                    self,
                    action_type=action_type,
                    action_details=details
                )
                result[0] = dialog.wait_for_result()
                event.set()
            
            # Schedule on main thread
            self.after(0, show_dialog)
            event.wait()
            
            return result[0]
        
        gemini_service.set_approval_callback(approval_callback)
    
    def _check_configuration(self):
        """Check if the app is configured properly."""
        if not session_service.get_api_key():
            # Show settings dialog
            self._open_settings()
    
    def _on_workspace_change(self):
        """Handle workspace changes."""
        pass
    
    def _on_session_load(self, session_id: str):
        """Load a saved session."""
        session = session_service.load_session(session_id)
        if session:
            # Load workspaces
            for workspace in session.workspaces:
                file_service.add_workspace(workspace)
            
            # TODO: Load messages into chat
            pass
    
    def _on_new_chat(self):
        """Start a new chat."""
        self.chat.new_chat()
    
    def _open_settings(self):
        """Open the settings dialog."""
        def on_save():
            # Refresh sidebar if needed
            self.sidebar.refresh()
        
        SettingsDialog(self, on_save=on_save)
    
    def _open_folder_picker(self):
        """Open the folder picker from sidebar."""
        self.sidebar._add_workspace()


def run_app():
    """Run the Gemini Cowork application."""
    app = GeminiCoworkApp()
    app.mainloop()
