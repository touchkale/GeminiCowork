# Session Service
"""
Session management for Gemini Cowork.
Handles saving/loading chat sessions and app configuration.
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict


def get_app_data_dir() -> Path:
    """Get the application data directory."""
    app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
    data_dir = Path(app_data) / 'GeminiCowork'
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@dataclass
class AppConfig:
    """Application configuration."""
    api_key: str = ""
    model_name: str = "gemini-2.0-flash"
    workspaces: List[str] = None
    theme: str = "dark"
    window_width: int = 1400
    window_height: int = 850
    # Autonomy mode: "autonomous" = AI acts freely, "supervised" = asks permission for each action
    autonomy_mode: str = "autonomous"
    
    def __post_init__(self):
        if self.workspaces is None:
            self.workspaces = []


@dataclass 
class ChatSession:
    """A saved chat session."""
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Dict[str, Any]]
    workspaces: List[str]


class SessionService:
    """Manages application configuration and chat sessions."""
    
    def __init__(self):
        self.data_dir = get_app_data_dir()
        self.config_path = self.data_dir / 'config.json'
        self.sessions_dir = self.data_dir / 'sessions'
        self.sessions_dir.mkdir(exist_ok=True)
        
        self.config: AppConfig = self._load_config()
        
    def _load_config(self) -> AppConfig:
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                return AppConfig(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return AppConfig()
    
    def save_config(self) -> bool:
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            return True
        except Exception:
            return False
    
    def get_api_key(self) -> str:
        """Get the stored API key."""
        return self.config.api_key
    
    def set_api_key(self, key: str) -> None:
        """Set the API key."""
        self.config.api_key = key
        self.save_config()
    
    def get_workspaces(self) -> List[str]:
        """Get the list of workspace directories."""
        return self.config.workspaces
    
    def add_workspace(self, path: str) -> bool:
        """Add a workspace directory."""
        if path not in self.config.workspaces:
            self.config.workspaces.append(path)
            self.save_config()
            return True
        return False
    
    def remove_workspace(self, path: str) -> bool:
        """Remove a workspace directory."""
        if path in self.config.workspaces:
            self.config.workspaces.remove(path)
            self.save_config()
            return True
        return False
    
    def get_model_name(self) -> str:
        """Get the configured model name."""
        return self.config.model_name
    
    def set_model_name(self, name: str) -> None:
        """Set the model name."""
        self.config.model_name = name
        self.save_config()
    
    def get_autonomy_mode(self) -> str:
        """Get the autonomy mode: 'autonomous' or 'supervised'."""
        return self.config.autonomy_mode
    
    def set_autonomy_mode(self, mode: str) -> None:
        """Set the autonomy mode."""
        if mode in ("autonomous", "supervised"):
            self.config.autonomy_mode = mode
            self.save_config()
    
    def is_supervised_mode(self) -> bool:
        """Check if running in supervised mode (ask for each action)."""
        return self.config.autonomy_mode == "supervised"
    
    # Session management
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def save_session(
        self,
        messages: List[Dict[str, Any]],
        title: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """
        Save a chat session.
        
        Returns:
            The session ID
        """
        if session_id is None:
            session_id = self._generate_session_id()
        
        if title is None:
            # Generate title from first user message
            for msg in messages:
                if msg.get('role') == 'user':
                    content = msg.get('content', '')
                    title = content[:50] + ('...' if len(content) > 50 else '')
                    break
            if not title:
                title = f"Chat {session_id}"
        
        now = datetime.now().isoformat()
        session = ChatSession(
            id=session_id,
            title=title,
            created_at=now,
            updated_at=now,
            messages=messages,
            workspaces=self.config.workspaces.copy()
        )
        
        session_path = self.sessions_dir / f"{session_id}.json"
        with open(session_path, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        return session_id
    
    def load_session(self, session_id: str) -> Optional[ChatSession]:
        """Load a chat session by ID."""
        session_path = self.sessions_dir / f"{session_id}.json"
        if session_path.exists():
            try:
                with open(session_path, 'r') as f:
                    data = json.load(f)
                return ChatSession(**data)
            except (json.JSONDecodeError, TypeError):
                pass
        return None
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        session_path = self.sessions_dir / f"{session_id}.json"
        if session_path.exists():
            session_path.unlink()
            return True
        return False
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all saved sessions (metadata only)."""
        sessions = []
        for path in sorted(self.sessions_dir.glob("*.json"), reverse=True):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                sessions.append({
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "message_count": len(data.get("messages", []))
                })
            except (json.JSONDecodeError, TypeError):
                continue
        return sessions


# Global instance
session_service = SessionService()
