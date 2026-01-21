# File System Service
"""
File system operations for Gemini Cowork.
Provides safe file read/write/delete operations within workspace boundaries.
"""

import os
import shutil
import fnmatch
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class FileService:
    """Handles all file system operations with workspace boundary enforcement."""
    
    def __init__(self):
        self.workspace_paths: List[Path] = []
        
    def set_workspaces(self, paths: List[str]) -> None:
        """Set the allowed workspace directories."""
        self.workspace_paths = [Path(p).resolve() for p in paths]
        
    def add_workspace(self, path: str) -> bool:
        """Add a workspace directory."""
        resolved = Path(path).resolve()
        if resolved.exists() and resolved.is_dir():
            if resolved not in self.workspace_paths:
                self.workspace_paths.append(resolved)
            return True
        return False
    
    def remove_workspace(self, path: str) -> bool:
        """Remove a workspace directory."""
        resolved = Path(path).resolve()
        if resolved in self.workspace_paths:
            self.workspace_paths.remove(resolved)
            return True
        return False
    
    def is_within_workspace(self, path: str) -> bool:
        """Check if a path is within any allowed workspace."""
        if not self.workspace_paths:
            return False
        resolved = Path(path).resolve()
        return any(
            resolved == workspace or workspace in resolved.parents
            for workspace in self.workspace_paths
        )
    
    def _validate_path(self, path: str) -> Path:
        """Validate and resolve a path, ensuring it's within workspace."""
        resolved = Path(path).resolve()
        if not self.is_within_workspace(str(resolved)):
            raise PermissionError(
                f"Access denied: '{path}' is outside of allowed workspaces"
            )
        return resolved
    
    def read_file(self, path: str) -> Dict[str, Any]:
        """
        Read the contents of a file.
        
        Returns:
            Dict with 'success', 'content' or 'error'
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if not file_path.is_file():
                return {"success": False, "error": f"Not a file: {path}"}
            
            # Try reading with different encodings
            for encoding in ['utf-8', 'utf-16', 'latin-1']:
                try:
                    content = file_path.read_text(encoding=encoding)
                    return {
                        "success": True,
                        "content": content,
                        "encoding": encoding,
                        "size": file_path.stat().st_size
                    }
                except UnicodeDecodeError:
                    continue
            
            # If all text encodings fail, read as binary
            content = file_path.read_bytes()
            return {
                "success": True,
                "content": f"[Binary file, {len(content)} bytes]",
                "is_binary": True,
                "size": len(content)
            }
            
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}
    
    def write_file(self, path: str, content: str, create_backup: bool = True) -> Dict[str, Any]:
        """
        Write content to a file. Creates parent directories if needed.
        
        Args:
            path: File path to write
            content: Content to write
            create_backup: If True, create backup of existing file
            
        Returns:
            Dict with 'success' and optionally 'backup_path' or 'error'
        """
        try:
            file_path = self._validate_path(path)
            backup_path = None
            
            # Create backup if file exists
            if create_backup and file_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
                shutil.copy2(file_path, backup_path)
            
            # Create parent directories
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            file_path.write_text(content, encoding='utf-8')
            
            result = {
                "success": True,
                "path": str(file_path),
                "size": file_path.stat().st_size
            }
            if backup_path:
                result["backup_path"] = str(backup_path)
            
            return result
            
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error writing file: {str(e)}"}
    
    def delete_file(self, path: str, to_recycle: bool = True) -> Dict[str, Any]:
        """
        Delete a file. By default moves to a backup location instead of permanent delete.
        
        Args:
            path: File path to delete
            to_recycle: If True, move to backup folder instead of permanent delete
            
        Returns:
            Dict with 'success' and result info
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            if to_recycle:
                # Move to a .deleted folder in workspace root
                workspace = next(
                    (w for w in self.workspace_paths if w in file_path.parents or w == file_path.parent),
                    self.workspace_paths[0]
                )
                deleted_folder = workspace / ".gemini_deleted"
                deleted_folder.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
                dest = deleted_folder / new_name
                
                shutil.move(str(file_path), str(dest))
                
                return {
                    "success": True,
                    "action": "moved_to_trash",
                    "original_path": str(file_path),
                    "trash_path": str(dest)
                }
            else:
                if file_path.is_file():
                    file_path.unlink()
                else:
                    shutil.rmtree(file_path)
                    
                return {
                    "success": True,
                    "action": "permanently_deleted",
                    "path": str(file_path)
                }
                
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error deleting file: {str(e)}"}
    
    def list_directory(self, path: str, recursive: bool = False, max_items: int = 100) -> Dict[str, Any]:
        """
        List contents of a directory.
        
        Args:
            path: Directory path
            recursive: If True, list recursively
            max_items: Maximum items to return
            
        Returns:
            Dict with 'success' and 'items' list
        """
        try:
            dir_path = self._validate_path(path)
            
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            items = []
            count = 0
            
            if recursive:
                iterator = dir_path.rglob("*")
            else:
                iterator = dir_path.iterdir()
            
            for item in iterator:
                if count >= max_items:
                    break
                    
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "path": str(item),
                        "relative_path": str(item.relative_to(dir_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                    count += 1
                except (PermissionError, OSError):
                    continue
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items,
                "total_shown": len(items),
                "truncated": count >= max_items
            }
            
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error listing directory: {str(e)}"}
    
    def search_files(self, pattern: str, directory: str, max_results: int = 50) -> Dict[str, Any]:
        """
        Search for files matching a pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.txt")
            directory: Directory to search in
            max_results: Maximum results to return
            
        Returns:
            Dict with 'success' and 'matches' list
        """
        try:
            dir_path = self._validate_path(directory)
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"Not a directory: {directory}"}
            
            matches = []
            count = 0
            
            for item in dir_path.rglob(pattern):
                if count >= max_results:
                    break
                try:
                    matches.append({
                        "path": str(item),
                        "relative_path": str(item.relative_to(dir_path)),
                        "type": "directory" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    })
                    count += 1
                except (PermissionError, OSError):
                    continue
            
            return {
                "success": True,
                "pattern": pattern,
                "directory": str(dir_path),
                "matches": matches,
                "total_found": len(matches),
                "truncated": count >= max_results
            }
            
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error searching files: {str(e)}"}
    
    def get_file_info(self, path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file or directory.
        
        Returns:
            Dict with file metadata
        """
        try:
            file_path = self._validate_path(path)
            
            if not file_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            stat = file_path.stat()
            
            info = {
                "success": True,
                "path": str(file_path),
                "name": file_path.name,
                "type": "directory" if file_path.is_dir() else "file",
                "size": stat.st_size,
                "size_human": self._human_readable_size(stat.st_size),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            }
            
            if file_path.is_file():
                info["extension"] = file_path.suffix
                
            if file_path.is_dir():
                try:
                    info["item_count"] = len(list(file_path.iterdir()))
                except PermissionError:
                    info["item_count"] = "unknown"
            
            return info
            
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error getting file info: {str(e)}"}
    
    def create_directory(self, path: str) -> Dict[str, Any]:
        """Create a new directory."""
        try:
            dir_path = self._validate_path(path)
            dir_path.mkdir(parents=True, exist_ok=True)
            return {"success": True, "path": str(dir_path)}
        except PermissionError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Error creating directory: {str(e)}"}
    
    @staticmethod
    def _human_readable_size(size: int) -> str:
        """Convert bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"


# Global instance
file_service = FileService()
