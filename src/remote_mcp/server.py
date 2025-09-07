#!/usr/bin/env python3
"""
Atlas Toolset MCP Server v3 - Modular architecture with enhanced features
"""

import os
import asyncio
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse
import uvicorn

# Import features
from .features import (
    CalculatorEngine,
    TextAnalyzerEngine,
    TaskManagerEngine,
    TimeEngine,
    PathConverterEngine
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atlas-toolset")

# Initialize MCP server
mcp = FastMCP("Atlas Toolset MCP")
mcp.description = "Enhanced utility toolset with calculator, text analysis, task management, time, path converter, and filesystem features"

# Initialize feature engines
calculator = CalculatorEngine()
text_analyzer = TextAnalyzerEngine()
task_manager = TaskManagerEngine()
time_engine = TimeEngine()
path_converter = PathConverterEngine()

# ============================================================================
# FILESYSTEM CONFIGURATION
# ============================================================================

# Configure allowed directories for filesystem operations
ALLOWED_DIRECTORIES = []
env_dirs = os.environ.get("ALLOWED_DIRECTORIES", "")
if env_dirs:
    ALLOWED_DIRECTORIES = [Path(d.strip()).resolve() for d in env_dirs.split(",")]
else:
    # Default to common safe directories
    home = Path.home()
    ALLOWED_DIRECTORIES = [
        home / "Documents",
        home / "Downloads",
        Path("/tmp"),
        Path("/projects") if Path("/projects").exists() else None,
    ]
    ALLOWED_DIRECTORIES = [d for d in ALLOWED_DIRECTORIES if d and d.exists()]

# Track deleted files (fake deletion ONLY - no real deletion for safety)
# Real file deletion is intentionally NOT supported to prevent data loss
DELETED_FILES = set()
DELETED_FILES_METADATA = {}

def convert_to_linux_path(path_str: str) -> str:
    """
    Convert path to Linux format if needed, using the PathConverterEngine.
    Returns the path in Linux format for internal processing.
    """
    # Use the path_converter instance to detect and convert
    detected_type = path_converter._detect_path_type(path_str)
    
    # If it's already Linux format, return as-is
    if detected_type == "linux":
        return path_str
    
    # Convert Windows to Linux
    return path_converter._windows_to_linux(path_str)

def is_path_allowed(path: Path) -> bool:
    """Check if a path is within allowed directories"""
    try:
        path = path.resolve()
        for allowed_dir in ALLOWED_DIRECTORIES:
            if path.is_relative_to(allowed_dir):
                return True
        return False
    except Exception:
        return False

def validate_path(path_str: str) -> Path:
    """Validate and return a Path object if allowed"""
    # Convert to Linux format first
    converted_path = convert_to_linux_path(path_str)
    path = Path(converted_path).expanduser().resolve()
    if not is_path_allowed(path):
        raise ValueError(f"Access denied: path {path} is outside allowed directories")
    # Check if file is marked as deleted
    if str(path) in DELETED_FILES:
        raise FileNotFoundError(f"File {path} has been marked as deleted")
    return path

def validate_parent_path(path_str: str) -> Path:
    """Validate parent directory for new files"""
    # Convert to Linux format first
    converted_path = convert_to_linux_path(path_str)
    path = Path(converted_path).expanduser().resolve()
    parent = path.parent
    if not is_path_allowed(parent):
        raise ValueError(f"Access denied: parent directory {parent} is outside allowed directories")
    return path

# ============================================================================
# SYSTEM INFO
# ============================================================================

@mcp.tool()
async def system_info() -> Dict[str, Any]:
    """Get system information and server status"""
    return {
        "server_name": "Atlas Toolset MCP",
        "version": "3.1.0",
        "timestamp": datetime.now().isoformat(),
        "transport": "streamable-http",
        "features": {
            "calculator": {
                "version": calculator.version,
                "capabilities": ["basic", "scientific", "statistical", "financial"]
            },
            "text_analyzer": {
                "version": text_analyzer.version,
                "modes": ["basic", "detailed", "readability", "sentiment", "keywords"]
            },
            "task_manager": {
                "version": task_manager.version,
                "capabilities": ["priorities", "categories", "dependencies", "time_tracking"]
            },
            "time": {
                "version": time_engine.version,
                "formats": ["italian", "iso", "us"],
                "shortcuts": ["now", "yesterday", "tomorrow", "EoD", "EoM", "last_month", "next_month"]
            },
            "path_converter": {
                "version": path_converter.version,
                "mappings": [f"{path_converter.windows_root.rstrip(chr(92))} <--> {path_converter.linux_root}"],
                "capabilities": ["auto-detect", "multiple_paths", "validation"],
                "configured_drive": path_converter.windows_drive
            },
            "filesystem": {
                "version": "1.1.0",
                "allowed_directories": [str(d) for d in ALLOWED_DIRECTORIES],
                "deleted_files_count": len(DELETED_FILES),
                "deletion_mode": "fake_only",
                "auto_path_conversion": True,
                "path_converter_mapping": f"{path_converter.windows_root.rstrip(chr(92))} <--> {path_converter.linux_root}",
                "note": "All deletions are reversible - files are never actually removed. Paths are auto-converted between Windows/Linux formats."
            }
        }
    }

# ============================================================================
# FILESYSTEM TOOLS
# ============================================================================

@mcp.tool()
async def fs_read_file(path: str) -> Dict[str, Any]:
    """
    Read the complete contents of a file from the file system. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Only works within allowed directories.
    
    Args:
        path: Path to the file to read
    """
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            return {"error": f"Path {path} is not a file"}
        
        content = file_path.read_text(encoding="utf-8")
        return {
            "content": content,
            "path": str(file_path),
            "size": len(content),
            "encoding": "utf-8"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_read_multiple_files(paths: List[str]) -> Dict[str, Any]:
    """
    Read the contents of multiple files simultaneously. This is more efficient than reading files one by one when you need to analyze or compare multiple files. Each file's content is returned with its path as a reference. Failed reads for individual files won't stop the entire operation. Only works within allowed directories.
    
    Args:
        paths: List of file paths to read
    """
    results = {}
    errors = {}
    
    for path_str in paths:
        try:
            file_path = validate_path(path_str)
            if not file_path.is_file():
                errors[path_str] = f"Path {path_str} is not a file"
                continue
            
            content = file_path.read_text(encoding="utf-8")
            results[path_str] = {
                "content": content,
                "size": len(content),
                "encoding": "utf-8"
            }
        except Exception as e:
            errors[path_str] = str(e)
    
    return {
        "files": results,
        "errors": errors,
        "total_files": len(paths),
        "successful": len(results),
        "failed": len(errors)
    }

@mcp.tool()
async def fs_write_file(path: str, content: str) -> Dict[str, Any]:
    """
    Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories.
    
    Args:
        path: Path where to write the file
        content: Content to write to the file
    """
    try:
        file_path = validate_parent_path(path)
        
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write content
        file_path.write_text(content, encoding="utf-8")
        
        # Remove from deleted files if it was marked as deleted
        if str(file_path) in DELETED_FILES:
            DELETED_FILES.remove(str(file_path))
            DELETED_FILES_METADATA.pop(str(file_path), None)
        
        return {
            "success": True,
            "path": str(file_path),
            "size": len(content),
            "message": f"Successfully wrote {len(content)} bytes to {file_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_edit_file(
    path: str,
    edits: List[Dict[str, str]],
    dry_run: bool = False
) -> Dict[str, Any]:
    """
    Make line-based edits to a text file. Each edit replaces exact line sequences with new content. Returns a git-style diff showing the changes made. Only works within allowed directories.
    
    Args:
        path: Path to the file to edit
        edits: List of edits, each with 'old_text' and 'new_text'
        dry_run: If True, preview changes without applying them
    """
    try:
        file_path = validate_path(path)
        if not file_path.is_file():
            return {"error": f"Path {path} is not a file"}
        
        original_content = file_path.read_text(encoding="utf-8")
        modified_content = original_content
        
        changes_made = []
        for edit in edits:
            old_text = edit.get("old_text", "")
            new_text = edit.get("new_text", "")
            
            if old_text in modified_content:
                modified_content = modified_content.replace(old_text, new_text)
                changes_made.append({
                    "old": old_text[:50] + "..." if len(old_text) > 50 else old_text,
                    "new": new_text[:50] + "..." if len(new_text) > 50 else new_text
                })
        
        if not dry_run and changes_made:
            file_path.write_text(modified_content, encoding="utf-8")
        
        return {
            "success": True,
            "path": str(file_path),
            "changes_made": len(changes_made),
            "dry_run": dry_run,
            "edits": changes_made,
            "message": f"{'Preview of' if dry_run else 'Applied'} {len(changes_made)} edits to {file_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_create_directory(path: str) -> Dict[str, Any]:
    """
    Create a new directory or ensure a directory exists. Can create multiple nested directories in one operation. If the directory already exists, this operation will succeed silently. Perfect for setting up directory structures for projects or ensuring required paths exist. Only works within allowed directories.
    
    Args:
        path: Path of the directory to create
    """
    try:
        dir_path = validate_parent_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return {
            "success": True,
            "path": str(dir_path),
            "exists": True,
            "message": f"Directory {dir_path} created/verified successfully"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_list_directory(path: str) -> Dict[str, Any]:
    """
    Get a detailed listing of all files and directories in a specified path. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is essential for understanding directory structure and finding specific files within a directory. Only works within allowed directories.
    
    Args:
        path: Path of the directory to list
    """
    try:
        dir_path = validate_path(path)
        if not dir_path.is_dir():
            return {"error": f"Path {path} is not a directory"}
        
        items = []
        for item in sorted(dir_path.iterdir()):
            # Skip if marked as deleted
            if str(item) in DELETED_FILES:
                continue
                
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            items.append(f"{item_type} {item.name}")
        
        return {
            "path": str(dir_path),
            "items": items,
            "total": len(items),
            "files": sum(1 for i in items if i.startswith("[FILE]")),
            "directories": sum(1 for i in items if i.startswith("[DIR]"))
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_directory_tree(path: str) -> Dict[str, Any]:
    """
    Get a recursive tree view of files and directories as a JSON structure. Each entry includes 'name', 'type' (file/directory), and 'children' for directories. Files have no children array, while directories always have a children array (which may be empty). The output is formatted with 2-space indentation for readability. Only works within allowed directories.
    
    Args:
        path: Root path for the directory tree
    """
    try:
        root_path = validate_path(path)
        if not root_path.is_dir():
            return {"error": f"Path {path} is not a directory"}
        
        def build_tree(dir_path: Path) -> Dict[str, Any]:
            tree = {
                "name": dir_path.name,
                "type": "directory",
                "path": str(dir_path),
                "children": []
            }
            
            try:
                for item in sorted(dir_path.iterdir()):
                    # Skip if marked as deleted
                    if str(item) in DELETED_FILES:
                        continue
                        
                    if item.is_dir():
                        tree["children"].append(build_tree(item))
                    else:
                        tree["children"].append({
                            "name": item.name,
                            "type": "file",
                            "path": str(item),
                            "size": item.stat().st_size
                        })
            except PermissionError:
                tree["error"] = "Permission denied"
            
            return tree
        
        tree = build_tree(root_path)
        return {
            "tree": tree,
            "root": str(root_path)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_move_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Move or rename files and directories. Can move files between directories and rename them in a single operation. If the destination exists, the operation will fail. Works across different directories and can be used for simple renaming within the same directory. Both source and destination must be within allowed directories.
    
    Args:
        source: Source path
        destination: Destination path
    """
    try:
        src_path = validate_path(source)
        dst_path = validate_parent_path(destination)
        
        if not src_path.exists():
            return {"error": f"Source path {source} does not exist"}
        
        if dst_path.exists():
            return {"error": f"Destination path {destination} already exists"}
        
        # Create parent directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file/directory
        shutil.move(str(src_path), str(dst_path))
        
        # Update deleted files tracking if source was in it
        if str(src_path) in DELETED_FILES:
            DELETED_FILES.remove(str(src_path))
            DELETED_FILES.add(str(dst_path))
            if str(src_path) in DELETED_FILES_METADATA:
                DELETED_FILES_METADATA[str(dst_path)] = DELETED_FILES_METADATA.pop(str(src_path))
        
        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dst_path),
            "message": f"Successfully moved {src_path} to {dst_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_copy_file(source: str, destination: str) -> Dict[str, Any]:
    """
    Copy a file to a new location. The destination can be a file path or a directory. If destination is a directory, the file will be copied with the same name. Only works within allowed directories.
    
    Args:
        source: Source file path
        destination: Destination path (file or directory)
    """
    try:
        src_path = validate_path(source)
        
        if not src_path.is_file():
            return {"error": f"Source path {source} is not a file"}
        
        # Determine destination path
        converted_dst = convert_to_linux_path(destination)
        dst_path = Path(converted_dst).expanduser().resolve()
        if dst_path.is_dir():
            dst_path = dst_path / src_path.name
        
        dst_path = validate_parent_path(str(dst_path))
        
        # Create parent directory if needed
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy the file
        shutil.copy2(str(src_path), str(dst_path))
        
        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dst_path),
            "size": dst_path.stat().st_size,
            "message": f"Successfully copied {src_path} to {dst_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_copy_directory(
    source: str, 
    destination: str,
    exclude_patterns: List[str] = None
) -> Dict[str, Any]:
    """
    Copy a directory recursively to a new location. Can exclude files matching specific patterns. Only works within allowed directories.
    
    Args:
        source: Source directory path
        destination: Destination directory path
        exclude_patterns: List of patterns to exclude (e.g., ['*.tmp', '__pycache__'])
    """
    try:
        src_path = validate_path(source)
        
        if not src_path.is_dir():
            return {"error": f"Source path {source} is not a directory"}
        
        dst_path = validate_parent_path(destination)
        
        # Create ignore function for patterns
        def ignore_patterns(dir_path, names):
            if not exclude_patterns:
                return set()
            
            ignored = set()
            for name in names:
                full_path = Path(dir_path) / name
                # Check if marked as deleted
                if str(full_path) in DELETED_FILES:
                    ignored.add(name)
                    continue
                # Check patterns
                for pattern in exclude_patterns:
                    if Path(name).match(pattern):
                        ignored.add(name)
                        break
            return ignored
        
        # Copy the directory
        shutil.copytree(
            str(src_path), 
            str(dst_path),
            ignore=ignore_patterns if exclude_patterns else None,
            dirs_exist_ok=True
        )
        
        # Count copied items
        file_count = sum(1 for _ in dst_path.rglob("*") if _.is_file())
        dir_count = sum(1 for _ in dst_path.rglob("*") if _.is_dir())
        
        return {
            "success": True,
            "source": str(src_path),
            "destination": str(dst_path),
            "files_copied": file_count,
            "directories_created": dir_count,
            "excluded_patterns": exclude_patterns or [],
            "message": f"Successfully copied directory {src_path} to {dst_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_delete_file(
    path: str
) -> Dict[str, Any]:
    """
    Delete a file (fake deletion - marks the file as deleted without actually removing it from disk). 
    The file can be restored later using fs_restore_deleted. Only works within allowed directories.
    
    Args:
        path: Path to the file to delete
    """
    try:
        file_path = validate_path(path)
        
        # ONLY fake deletion - no real deletion allowed
        if not file_path.exists():
            return {"error": f"Path {path} does not exist"}
        
        DELETED_FILES.add(str(file_path))
        DELETED_FILES_METADATA[str(file_path)] = {
            "deleted_at": datetime.now().isoformat(),
            "original_size": file_path.stat().st_size if file_path.is_file() else None,
            "type": "file" if file_path.is_file() else "directory"
        }
        message = f"Deleted {file_path} (file still exists on disk, can be restored)"
        
        return {
            "success": True,
            "path": str(file_path),
            "message": message,
            "can_restore": True
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_restore_deleted(path: str) -> Dict[str, Any]:
    """
    Restore a file that was marked as deleted (fake deletion). Only works for files that were soft-deleted.
    
    Args:
        path: Path of the file to restore
    """
    try:
        # Convert to Linux format first
        converted_path = convert_to_linux_path(path)
        file_path = Path(converted_path).expanduser().resolve()
        path_str = str(file_path)
        
        if path_str not in DELETED_FILES:
            return {"error": f"Path {path} is not in the deleted files list"}
        
        # Verify file still exists on disk
        if not file_path.exists():
            return {"error": f"Path {path} no longer exists on disk - cannot restore"}
        
        # Restore the file
        DELETED_FILES.remove(path_str)
        metadata = DELETED_FILES_METADATA.pop(path_str, {})
        
        return {
            "success": True,
            "path": path_str,
            "restored": True,
            "deleted_at": metadata.get("deleted_at", "unknown"),
            "message": f"Successfully restored {file_path}"
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_list_deleted() -> Dict[str, Any]:
    """
    List all files that have been marked as deleted (fake deletion).
    """
    deleted_list = []
    for path_str in DELETED_FILES:
        metadata = DELETED_FILES_METADATA.get(path_str, {})
        deleted_list.append({
            "path": path_str,
            "deleted_at": metadata.get("deleted_at", "unknown"),
            "type": metadata.get("type", "unknown"),
            "size": metadata.get("original_size")
        })
    
    return {
        "deleted_files": deleted_list,
        "total": len(deleted_list),
        "message": f"Found {len(deleted_list)} deleted files/directories"
    }

@mcp.tool()
async def fs_search_files(
    path: str,
    pattern: str,
    exclude_patterns: List[str] = None
) -> Dict[str, Any]:
    """
    Recursively search for files and directories matching a pattern. Searches through all subdirectories from the starting path. The search is case-insensitive and matches partial names. Returns full paths to all matching items. Great for finding files when you don't know their exact location. Only searches within allowed directories.
    
    Args:
        path: Starting directory for search
        pattern: Search pattern (case-insensitive partial match)
        exclude_patterns: Patterns to exclude from search
    """
    try:
        search_path = validate_path(path)
        if not search_path.is_dir():
            return {"error": f"Path {path} is not a directory"}
        
        pattern_lower = pattern.lower()
        matches = []
        exclude_patterns = exclude_patterns or []
        
        for item_path in search_path.rglob("*"):
            # Skip if marked as deleted
            if str(item_path) in DELETED_FILES:
                continue
            
            # Check exclude patterns
            skip = False
            for exclude_pattern in exclude_patterns:
                if item_path.match(exclude_pattern):
                    skip = True
                    break
            if skip:
                continue
            
            # Check if name matches pattern
            if pattern_lower in item_path.name.lower():
                matches.append({
                    "path": str(item_path),
                    "name": item_path.name,
                    "type": "directory" if item_path.is_dir() else "file",
                    "size": item_path.stat().st_size if item_path.is_file() else None
                })
        
        return {
            "pattern": pattern,
            "search_path": str(search_path),
            "matches": matches,
            "total": len(matches),
            "excluded_patterns": exclude_patterns
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_get_file_info(path: str) -> Dict[str, Any]:
    """
    Retrieve detailed metadata about a file or directory. Returns comprehensive information including size, creation time, last modified time, permissions, and type. This tool is perfect for understanding file characteristics without reading the actual content. Only works within allowed directories.
    
    Args:
        path: Path to the file or directory
    """
    try:
        file_path = validate_path(path)
        if not file_path.exists():
            return {"error": f"Path {path} does not exist"}
        
        stat = file_path.stat()
        
        info = {
            "path": str(file_path),
            "name": file_path.name,
            "type": "directory" if file_path.is_dir() else "file",
            "size": stat.st_size,
            "size_human": f"{stat.st_size:,} bytes",
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
            "is_symlink": file_path.is_symlink(),
            "is_hidden": file_path.name.startswith(".")
        }
        
        if file_path.is_dir():
            # Count contents for directories
            try:
                contents = list(file_path.iterdir())
                info["contents"] = {
                    "total": len(contents),
                    "files": sum(1 for p in contents if p.is_file() and str(p) not in DELETED_FILES),
                    "directories": sum(1 for p in contents if p.is_dir() and str(p) not in DELETED_FILES)
                }
            except PermissionError:
                info["contents"] = {"error": "Permission denied"}
        
        return info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def fs_list_allowed_directories() -> Dict[str, Any]:
    """
    Returns the list of directories that this server is allowed to access. Use this to understand which directories are available before trying to access files.
    """
    return {
        "allowed_directories": [str(d) for d in ALLOWED_DIRECTORIES],
        "total": len(ALLOWED_DIRECTORIES),
        "note": "Only operations within these directories are permitted"
    }

# ============================================================================
# PATH CONVERTER TOOLS
# ============================================================================

@mcp.tool()
async def convert_path(
    path: str,
    force_direction: str = None
) -> Dict[str, Any]:
    f"""
    Convert between Windows and Linux path formats ({path_converter.windows_root.rstrip(chr(92))} <--> {path_converter.linux_root})
    
    Args:
        path: Path to convert
        force_direction: Force conversion direction: 'to_linux' or 'to_windows' (auto-detect if not specified)
    """
    response = path_converter.convert_path(path, force_direction)
    return response.to_dict()

@mcp.tool()
async def convert_multiple_paths(
    paths: List[str],
    force_direction: str = None
) -> Dict[str, Any]:
    """
    Convert multiple paths at once
    
    Args:
        paths: List of paths to convert
        force_direction: Force conversion direction for all paths
    """
    response = path_converter.convert_multiple_paths(paths, force_direction)
    return response.to_dict()

@mcp.tool()
async def validate_path(
    path: str
) -> Dict[str, Any]:
    """
    Validate a path and show both Windows and Linux formats
    
    Args:
        path: Path to validate and show conversions for
    """
    response = path_converter.validate_path(path)
    return response.to_dict()

# ============================================================================
# CALCULATOR TOOLS
# ============================================================================

@mcp.tool()
async def calculate(
    a: float,
    b: float = None,
    operation: str = "add"
) -> Dict[str, Any]:
    """
    Perform mathematical calculations
    
    Args:
        a: First number or list of numbers
        b: Second number (optional for some operations)
        operation: Operation (add, subtract, multiply, divide, power, modulo, sqrt, factorial, percentage, average)
    """
    response = calculator.calculate(a, b, operation)
    return response.to_dict()

@mcp.tool()
async def calculate_advanced(
    expression: str,
    variables: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Evaluate mathematical expressions safely
    
    Args:
        expression: Mathematical expression (e.g., "2 * pi * r")
        variables: Optional dictionary of variables
    """
    response = calculator.calculate_advanced(expression, variables)
    return response.to_dict()

@mcp.tool()
async def calculate_statistics(
    data: List[float],
    operations: List[str]
) -> Dict[str, Any]:
    """
    Perform statistical calculations on data
    
    Args:
        data: List of numbers
        operations: Operations to perform (mean, median, mode, stdev, variance, sum, min, max, range)
    """
    response = calculator.calculate_statistics(data, operations)
    return response.to_dict()

@mcp.tool()
async def calculate_financial(
    calc_type: str,
    params: Dict[str, float]
) -> Dict[str, Any]:
    """
    Perform financial calculations
    
    Args:
        calc_type: Type of calculation (compound_interest, loan_payment, roi, present_value)
        params: Parameters specific to calculation type
    """
    response = calculator.calculate_financial(calc_type, params)
    return response.to_dict()

# ============================================================================
# TEXT ANALYZER TOOLS
# ============================================================================

@mcp.tool()
async def text_analyze(
    text: str,
    mode: str = "basic"
) -> Dict[str, Any]:
    """
    Analyze text with various metrics
    
    Args:
        text: Text to analyze
        mode: Analysis mode (basic, detailed, readability, sentiment, keywords)
    """
    response = text_analyzer.text_analyze(text, mode)
    return response.to_dict()

@mcp.tool()
async def text_compare(
    text1: str,
    text2: str
) -> Dict[str, Any]:
    """
    Compare two texts for similarity and differences
    
    Args:
        text1: First text
        text2: Second text
    """
    response = text_analyzer.text_compare(text1, text2)
    return response.to_dict()

@mcp.tool()
async def text_extract(
    text: str,
    extract_type: str
) -> Dict[str, Any]:
    """
    Extract specific information from text
    
    Args:
        text: Source text
        extract_type: Type of extraction (urls, emails, numbers, dates, hashtags, mentions)
    """
    response = text_analyzer.text_extract(text, extract_type)
    return response.to_dict()

@mcp.tool()
async def text_transform(
    text: str,
    transformation: str
) -> Dict[str, Any]:
    """
    Transform text in various ways
    
    Args:
        text: Text to transform
        transformation: Transformation type (uppercase, lowercase, title, reverse, remove_punctuation, remove_spaces, snake_case, camel_case)
    """
    response = text_analyzer.text_transform(text, transformation)
    return response.to_dict()

# ============================================================================
# TASK MANAGER TOOLS
# ============================================================================

@mcp.tool()
async def task_create(
    title: str,
    description: str = "",
    priority: str = "medium",
    category: str = None,
    tags: str = None,  # Accept as string, parse internally
    due_date: str = None,
    estimated_hours: str = None  # Accept as string, parse internally
) -> Dict[str, Any]:
    """
    Create a new task with advanced options
    
    Args:
        title: Task title
        description: Task description
        priority: Priority (low, medium, high, urgent, critical)
        category: Task category
        tags: List of tags
        due_date: Due date (ISO format)
        estimated_hours: Estimated hours to complete
    """
    # Parse tags from string (comma-separated)
    if tags is not None and isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    else:
        tags = None
    
    # Parse estimated_hours from string
    if estimated_hours is not None:
        try:
            estimated_hours = float(estimated_hours)
        except (ValueError, TypeError):
            estimated_hours = None
    
    response = task_manager.task_create(
        title, description, priority, category, 
        tags, due_date, estimated_hours
    )
    return response.to_dict()

@mcp.tool()
async def task_list(
    status: str = None,
    priority: str = None,
    category: str = None,
    overdue: bool = False
) -> Dict[str, Any]:
    """
    List tasks with filtering
    
    Args:
        status: Filter by status (pending, in_progress, blocked, review, completed, cancelled, archived)
        priority: Filter by priority
        category: Filter by category
        overdue: Show only overdue tasks
    """
    response = task_manager.task_list(status, priority, category, None, overdue)
    return response.to_dict()

@mcp.tool()
async def task_update(
    task_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Update a task
    
    Args:
        task_id: Task ID to update
        updates: Dictionary of fields to update
    """
    response = task_manager.task_update(task_id, updates)
    return response.to_dict()

@mcp.tool()
async def task_delete(
    task_id: str
) -> Dict[str, Any]:
    """
    Delete a task
    
    Args:
        task_id: Task ID to delete
    """
    response = task_manager.task_delete(task_id)
    return response.to_dict()

@mcp.tool()
async def task_complete(
    task_id: str,
    completion_notes: str = None,
    actual_hours: str = None  # Accept as string, parse internally
) -> Dict[str, Any]:
    """
    Mark a task as complete
    
    Args:
        task_id: Task ID to complete
        completion_notes: Optional completion notes
        actual_hours: Actual hours taken
    """
    # Handle parameter conversion for actual_hours
    if actual_hours is not None:
        try:
            actual_hours = float(actual_hours)
        except (ValueError, TypeError):
            actual_hours = None
    
    response = task_manager.task_complete(task_id, completion_notes, actual_hours)
    return response.to_dict()

@mcp.tool()
async def task_stats() -> Dict[str, Any]:
    """Get comprehensive task statistics"""
    response = task_manager.task_stats()
    return response.to_dict()

# ============================================================================
# TIME TOOLS
# ============================================================================

@mcp.tool()
async def time_now(
    format: str = "italian",
    timezone: int = 0
) -> Dict[str, Any]:
    """
    Get current date and time
    
    Args:
        format: Output format (italian, iso, us, timestamp, full_italian)
        timezone: Timezone offset in hours
    """
    response = time_engine.time_now(format, timezone)
    return response.to_dict()

@mcp.tool()
async def time_parse(
    shortcut: str,
    format: str = "italian"
) -> Dict[str, Any]:
    """
    Parse date shortcuts
    
    Examples:
        - 'now': Current datetime
        - 'yesterday': Yesterday at same time
        - 'tomorrow': Tomorrow at same time
        - 'EoD': End of Day (23:59:59)
        - 'EoM': End of Month
        - 'tomorrow EoD': Tomorrow at 23:59:59
        - 'next month EoM': Last day of next month
    
    Args:
        shortcut: Date shortcut to parse
        format: Output format
    """
    response = time_engine.time_parse(shortcut, format)
    return response.to_dict()

@mcp.tool()
async def time_calculate(
    date1: str,
    date2: str,
    unit: str = "days"
) -> Dict[str, Any]:
    """
    Calculate difference between two dates with detailed statistics
    
    Args:
        date1: First date (ISO format or shortcut)
        date2: Second date (ISO format or shortcut)
        unit: Result unit (seconds, minutes, hours, days, weeks, months, years)
    """
    response = time_engine.time_calculate(date1, date2, unit)
    return response.to_dict()

@mcp.tool()
async def time_add(
    base_date: str,
    amount: float,
    unit: str = "days",
    format: str = "italian"
) -> Dict[str, Any]:
    """
    Add or subtract time from a date
    
    Args:
        base_date: Base date (ISO format or shortcut)
        amount: Amount to add (negative to subtract)
        unit: Unit (seconds, minutes, hours, days, weeks, months, years)
        format: Output format
    """
    response = time_engine.time_add(base_date, amount, unit, format)
    return response.to_dict()

@mcp.tool()
async def time_format(
    date_input: str,
    input_format: str = "auto",
    output_format: str = "italian"
) -> Dict[str, Any]:
    """
    Convert between date formats
    
    Args:
        date_input: Date to format
        input_format: Input format (auto-detect if 'auto')
        output_format: Output format (italian, iso, us, timestamp, full_italian)
    """
    response = time_engine.time_format(date_input, input_format, output_format)
    return response.to_dict()

# ============================================================================
# ASGI APPLICATION WITH HEALTH CHECK
# ============================================================================

async def health_check(request):
    """Health check endpoint for CapRover"""
    return JSONResponse(
        {
            "status": "healthy",
            "service": "Atlas Toolset MCP",
            "version": "3.1.0",
            "features": ["calculator", "text_analyzer", "task_manager", "time", "path_converter", "filesystem"],
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )

# Create MCP app
try:
    if hasattr(mcp, 'http_app'):
        mcp_app = mcp.http_app()
        logger.info("Created MCP app with /mcp path")
    elif hasattr(mcp, 'streamable_http_app'):
        mcp_app = mcp.streamable_http_app()
        logger.warning("Using older streamable_http_app()")
    else:
        raise AttributeError("No HTTP app method found in FastMCP")
    
except Exception as e:
    logger.error(f"Failed to create MCP HTTP app: {e}")
    raise

# Create main Starlette app with health check
app = Starlette(
    lifespan=mcp_app.lifespan,
    routes=[
        Route("/health", health_check, methods=["GET"]),
        Route("/", health_check, methods=["GET"]),
        Route("/mcp", mcp_app, methods=["POST", "GET"]),
        Route("/mcp/", mcp_app, methods=["POST", "GET"]),
    ]
)

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # Get configuration from environment
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"Starting Atlas Toolset MCP Server v3.1.0")
    logger.info(f"Server will be available at {host}:{port}/mcp")
    logger.info(f"Health check at {host}:{port}/health")
    logger.info(f"Features loaded: calculator, text_analyzer, task_manager, time, path_converter, filesystem")
    logger.info(f"Filesystem allowed directories: {[str(d) for d in ALLOWED_DIRECTORIES]}")
    logger.info(f"Italian date format enabled with shortcuts")
    
    try:
        uvicorn.run(app, host=host, port=port)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
