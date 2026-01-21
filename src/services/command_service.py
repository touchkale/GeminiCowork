# Command Execution Service
"""
PowerShell command execution for Gemini Cowork.
Provides safe command execution with output streaming.
"""

import subprocess
import threading
import queue
import os
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    success: bool


class CommandService:
    """Handles PowerShell command execution with streaming output."""
    
    # Commands that are always blocked
    BLOCKED_PATTERNS = [
        "format",
        "del /s",
        "rd /s",
        "rmdir /s",
        "Remove-Item -Recurse -Force /",
        "Remove-Item -Recurse -Force C:",
        "Stop-Computer",
        "Restart-Computer",
        "shutdown",
    ]
    
    def __init__(self):
        self.command_history: List[CommandResult] = []
        self.current_process: Optional[subprocess.Popen] = None
        self.working_directory: Optional[str] = None
        
    def set_working_directory(self, path: str) -> bool:
        """Set the working directory for command execution."""
        if os.path.isdir(path):
            self.working_directory = path
            return True
        return False
    
    def is_command_safe(self, command: str) -> tuple[bool, str]:
        """
        Check if a command is safe to execute.
        Returns (is_safe, reason).
        """
        command_lower = command.lower()
        
        for pattern in self.BLOCKED_PATTERNS:
            if pattern.lower() in command_lower:
                return False, f"Blocked pattern detected: {pattern}"
        
        # Additional safety checks
        if "| out-file" in command_lower and "c:\\windows" in command_lower:
            return False, "Cannot write to system directories"
            
        return True, "Command appears safe"
    
    def run_command(
        self,
        command: str,
        timeout: int = 60,
        on_output: Optional[Callable[[str], None]] = None,
        cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a PowerShell command.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            on_output: Callback for streaming output
            cwd: Working directory (overrides default)
            
        Returns:
            Dict with 'success', 'output', 'error', 'exit_code'
        """
        start_time = datetime.now()
        
        try:
            # Use provided cwd or default working directory
            work_dir = cwd or self.working_directory or os.getcwd()
            
            # Create the process
            self.current_process = subprocess.Popen(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                cwd=work_dir,
                text=True,
                bufsize=1,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Read output with streaming
            def read_stream(stream, lines_list, callback):
                for line in iter(stream.readline, ''):
                    if line:
                        lines_list.append(line)
                        if callback:
                            callback(line)
                stream.close()
            
            stdout_thread = threading.Thread(
                target=read_stream,
                args=(self.current_process.stdout, stdout_lines, on_output)
            )
            stderr_thread = threading.Thread(
                target=read_stream,
                args=(self.current_process.stderr, stderr_lines, None)
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            # Wait for completion with timeout
            exit_code = self.current_process.wait(timeout=timeout)
            
            stdout_thread.join(timeout=1)
            stderr_thread.join(timeout=1)
            
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            result = CommandResult(
                command=command,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                duration_ms=duration,
                success=exit_code == 0
            )
            self.command_history.append(result)
            
            return {
                "success": exit_code == 0,
                "exit_code": exit_code,
                "output": stdout,
                "error": stderr if stderr else None,
                "duration_ms": duration
            }
            
        except subprocess.TimeoutExpired:
            if self.current_process:
                self.current_process.kill()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "exit_code": -1
            }
        finally:
            self.current_process = None
    
    def run_command_simple(self, command: str, cwd: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a command and return result (no streaming).
        Simpler version for quick commands.
        """
        return self.run_command(command, timeout=30, cwd=cwd)
    
    def cancel_current(self) -> bool:
        """Cancel the currently running command."""
        if self.current_process:
            try:
                self.current_process.kill()
                return True
            except:
                pass
        return False
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent command history."""
        return [
            {
                "command": r.command,
                "success": r.success,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms
            }
            for r in self.command_history[-limit:]
        ]


# Global instance
command_service = CommandService()
