# Gemini API Service
"""
Google Gemini API integration with function calling support.
Implements the agentic loop for tool execution.
"""

import json
import threading
import warnings
from typing import Optional, Callable, Dict, Any, List, Generator
from dataclasses import dataclass, field
from datetime import datetime

# Suppress deprecation warnings from google-generativeai
warnings.filterwarnings("ignore", category=FutureWarning, module="google")

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerateContentResponse
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None

from .file_service import file_service
from .command_service import command_service


# Tool definitions for Gemini function calling
TOOL_DEFINITIONS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file. Returns the file content as text.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The absolute or relative path to the file to read"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates the file if it doesn't exist, or overwrites if it does. Creates parent directories automatically.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List all files and subdirectories in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the directory to list"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "If true, list recursively including subdirectories"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file. IMPORTANT: This action requires user approval. The file is moved to a trash folder, not permanently deleted.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to delete"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "run_command",
        "description": "Execute a PowerShell command on the user's Windows system. IMPORTANT: This action requires user approval. Use for system operations, running scripts, or getting system information.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The PowerShell command to execute"
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "search_files",
        "description": "Search for files matching a pattern in a directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The glob pattern to match (e.g., '*.py', '**/*.txt')"
                },
                "directory": {
                    "type": "string",
                    "description": "The directory to search in"
                }
            },
            "required": ["pattern", "directory"]
        }
    },
    {
        "name": "get_file_info",
        "description": "Get detailed information about a file or directory including size, dates, and type.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file or directory"
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "create_directory",
        "description": "Create a new directory. Creates parent directories if they don't exist.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path of the directory to create"
                }
            },
            "required": ["path"]
        }
    }
]

# Tools that require user approval
APPROVAL_REQUIRED_TOOLS = {"delete_file", "run_command"}


@dataclass
class ToolCall:
    """Represents a tool call from Gemini."""
    name: str
    args: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    approved: Optional[bool] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Message:
    """A message in the conversation."""
    role: str  # "user" or "model"
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class GeminiService:
    """Handles Gemini API interactions with function calling."""
    
    def __init__(self):
        self.api_key: Optional[str] = None
        self.model: Optional[Any] = None
        self.chat: Optional[Any] = None
        self.conversation_history: List[Message] = []
        self.model_name: str = "gemini-2.0-flash"
        self._is_configured = False
        self._approval_callback: Optional[Callable[[ToolCall], bool]] = None
        self._tool_callback: Optional[Callable[[ToolCall], None]] = None
        self._stream_callback: Optional[Callable[[str], None]] = None
        
    def configure(self, api_key: str, model_name: str = "gemini-2.0-flash") -> Dict[str, Any]:
        """
        Configure the Gemini API with an API key.
        
        Args:
            api_key: Google AI API key
            model_name: Name of the model to use
            
        Returns:
            Dict with 'success' and 'error' if failed
        """
        if not GENAI_AVAILABLE:
            return {
                "success": False,
                "error": "google-generativeai package not installed. Run: pip install google-generativeai"
            }
        
        try:
            self.api_key = api_key
            self.model_name = model_name
            
            genai.configure(api_key=api_key)
            
            # Create tool functions for the model
            tools = []
            for tool_def in TOOL_DEFINITIONS:
                tools.append({
                    "function_declarations": [{
                        "name": tool_def["name"],
                        "description": tool_def["description"],
                        "parameters": tool_def["parameters"]
                    }]
                })
            
            # Create the model WITH tools for function calling
            self.model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=self._get_system_prompt(),
                tools=tools
            )
            
            # Start a new chat
            self.chat = self.model.start_chat(history=[])
            self.conversation_history = []
            self._is_configured = True
            
            return {"success": True, "model": model_name}
            
        except Exception as e:
            self._is_configured = False
            error_str = str(e)
            print(f"Gemini configure error: {error_str}")
            return {"success": False, "error": error_str}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI."""
        # Import here to avoid circular imports
        from .session_service import session_service
        
        # Get current workspace paths
        workspaces = session_service.get_workspaces()
        workspace_info = ""
        if workspaces:
            workspace_list = "\n".join(f"  - {path}" for path in workspaces)
            workspace_info = f"""

IMPORTANT - Current workspace folders:
{workspace_list}

When the user refers to "this folder" or "the folder", they mean the workspace folders listed above. 
Always use the FULL PATH from the workspace list when performing file operations.
If only one workspace is selected, use that path by default."""
        else:
            workspace_info = "\n\nNote: No workspace folder is currently selected. Ask the user to add a folder first."
        
        return f"""You are Gemini Cowork, an intelligent AI assistant that helps users with coding and file management tasks on their Windows computer.

You have access to the following tools:
- read_file: Read contents of files
- write_file: Create or modify files
- list_directory: Browse folders
- delete_file: Delete files (requires user approval)
- run_command: Execute PowerShell commands (requires user approval)
- search_files: Find files by pattern
- get_file_info: Get file metadata
- create_directory: Create folders

Guidelines:
1. Be helpful and proactive in understanding what the user needs
2. Use tools when necessary to complete tasks
3. Always explain what you're doing and why
4. For destructive actions (delete, commands), clearly state what will happen
5. If you encounter errors, explain them and suggest solutions
6. Format code blocks with proper syntax highlighting
7. Be concise but thorough
8. ALWAYS use the full paths from the workspace list below when working with files
{workspace_info}"""

    def is_configured(self) -> bool:
        """Check if the service is configured and ready."""
        return self._is_configured and self.model is not None
    
    def set_approval_callback(self, callback: Callable[[ToolCall], bool]) -> None:
        """Set callback for tool approval requests."""
        self._approval_callback = callback
    
    def set_tool_callback(self, callback: Callable[[ToolCall], None]) -> None:
        """Set callback for tool execution updates."""
        self._tool_callback = callback
    
    def set_stream_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for streaming text output."""
        self._stream_callback = callback
    
    def _execute_tool(self, tool_call: ToolCall) -> Dict[str, Any]:
        """Execute a tool and return the result."""
        name = tool_call.name
        args = tool_call.args
        
        try:
            if name == "read_file":
                return file_service.read_file(args["path"])
            
            elif name == "write_file":
                return file_service.write_file(args["path"], args["content"])
            
            elif name == "list_directory":
                recursive = args.get("recursive", False)
                return file_service.list_directory(args["path"], recursive=recursive)
            
            elif name == "delete_file":
                return file_service.delete_file(args["path"])
            
            elif name == "run_command":
                return command_service.run_command_simple(args["command"])
            
            elif name == "search_files":
                return file_service.search_files(args["pattern"], args["directory"])
            
            elif name == "get_file_info":
                return file_service.get_file_info(args["path"])
            
            elif name == "create_directory":
                return file_service.create_directory(args["path"])
            
            else:
                return {"success": False, "error": f"Unknown tool: {name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _request_approval(self, tool_call: ToolCall) -> bool:
        """Request user approval for a tool call."""
        if self._approval_callback:
            return self._approval_callback(tool_call)
        return False  # Deny by default if no callback
    
    def send_message(self, user_message: str) -> Generator[Dict[str, Any], None, None]:
        """
        Send a message and handle the agentic loop with tool calls.
        Yields events for streaming UI updates.
        
        Yields:
            Dict events: 'text', 'tool_call', 'tool_result', 'error', 'done'
        """
        if not self.is_configured():
            yield {"type": "error", "error": "Gemini is not configured. Please add your API key in settings."}
            return
        
        # Add user message to history
        user_msg = Message(role="user", content=user_message)
        self.conversation_history.append(user_msg)
        
        try:
            # Send message to Gemini
            response = self.chat.send_message(user_message)
            
            # Process response in agentic loop
            while True:
                # Check for function calls
                function_calls = []
                text_parts = []
                
                for part in response.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        fc = part.function_call
                        function_calls.append(ToolCall(
                            name=fc.name,
                            args=dict(fc.args) if fc.args else {}
                        ))
                    elif hasattr(part, 'text') and part.text:
                        text_parts.append(part.text)
                
                # If there's text, yield it
                if text_parts:
                    text = ''.join(text_parts)
                    yield {"type": "text", "content": text}
                
                # If no function calls, we're done
                if not function_calls:
                    break
                
                # Process function calls
                tool_results = []
                
                for tool_call in function_calls:
                    # Notify UI about tool call
                    yield {"type": "tool_call", "tool": tool_call}
                    
                    if self._tool_callback:
                        self._tool_callback(tool_call)
                    
                    # Check if approval is required based on autonomy mode
                    # Import here to avoid circular imports
                    from .session_service import session_service
                    
                    # In supervised mode, ALL tools require approval
                    # In autonomous mode, only destructive tools require approval
                    requires_approval = (
                        session_service.is_supervised_mode() or 
                        tool_call.name in APPROVAL_REQUIRED_TOOLS
                    )
                    
                    if requires_approval:
                        approved = self._request_approval(tool_call)
                        tool_call.approved = approved
                        
                        if not approved:
                            tool_call.result = {
                                "success": False,
                                "error": "User denied this action"
                            }
                            yield {"type": "tool_denied", "tool": tool_call}
                            tool_results.append({
                                "name": tool_call.name,
                                "response": tool_call.result
                            })
                            continue
                    
                    # Execute the tool
                    result = self._execute_tool(tool_call)
                    tool_call.result = result
                    
                    yield {"type": "tool_result", "tool": tool_call, "result": result}
                    
                    tool_results.append({
                        "name": tool_call.name,
                        "response": result
                    })
                
                # Send tool results back to Gemini
                if tool_results:
                    # Format results for Gemini
                    result_parts = []
                    for tr in tool_results:
                        result_parts.append(genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=tr["name"],
                                response={"result": json.dumps(tr["response"])}
                            )
                        ))
                    
                    response = self.chat.send_message(result_parts)
            
            # Create assistant message with final content
            final_text = ''.join(text_parts) if text_parts else ""
            ai_msg = Message(role="model", content=final_text)
            self.conversation_history.append(ai_msg)
            
            yield {"type": "done", "message": ai_msg}
            
        except Exception as e:
            error_msg = str(e)
            yield {"type": "error", "error": error_msg}
    
    def send_message_sync(self, user_message: str) -> Dict[str, Any]:
        """
        Synchronous version of send_message.
        Returns the final result.
        """
        result = {
            "text": "",
            "tool_calls": [],
            "success": True,
            "error": None
        }
        
        for event in self.send_message(user_message):
            if event["type"] == "text":
                result["text"] += event["content"]
            elif event["type"] in ("tool_call", "tool_result"):
                result["tool_calls"].append(event.get("tool"))
            elif event["type"] == "error":
                result["success"] = False
                result["error"] = event["error"]
        
        return result
    
    def clear_history(self) -> None:
        """Clear conversation history and start fresh."""
        self.conversation_history = []
        if self.model:
            self.chat = self.model.start_chat(history=[])
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as serializable dicts."""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "tool_calls": [
                    {
                        "name": tc.name,
                        "args": tc.args,
                        "result": tc.result,
                        "approved": tc.approved
                    }
                    for tc in msg.tool_calls
                ]
            }
            for msg in self.conversation_history
        ]


# Global instance
gemini_service = GeminiService()
