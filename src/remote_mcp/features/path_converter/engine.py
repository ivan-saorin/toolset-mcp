"""
Path Converter Engine - Convert between Windows and Linux paths
Configurable drive mapping with MCP_WINDOWS_DRIVE environment variable
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple
from ...shared.base import BaseFeature, ToolResponse


class PathConverterEngine(BaseFeature):
    """Engine for converting between Windows and Linux path formats"""
    
    def __init__(self):
        super().__init__(name="path_converter", version="1.1.0")
        # Get Windows drive from environment variable, default to M:
        self.windows_drive = os.environ.get("MCP_WINDOWS_DRIVE", "M")
        self.windows_root = f"{self.windows_drive}:\\"
        self.linux_root = "/mcp"
        
        # Log the configuration
        self.logger.info(f"Path converter initialized with mapping: {self.windows_root} <--> {self.linux_root}")
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of path conversion tools"""
        return [
            {
                "name": "convert_path",
                "description": f"Convert between Windows and Linux path formats ({self.windows_root.rstrip(chr(92))} <--> {self.linux_root})",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to convert"
                        },
                        "force_direction": {
                            "type": "string",
                            "description": "Force conversion direction: 'to_linux' or 'to_windows' (auto-detect if not specified)",
                            "enum": ["to_linux", "to_windows"]
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "convert_multiple_paths",
                "description": "Convert multiple paths at once",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of paths to convert"
                        },
                        "force_direction": {
                            "type": "string",
                            "description": "Force conversion direction for all paths",
                            "enum": ["to_linux", "to_windows"]
                        }
                    },
                    "required": ["paths"]
                }
            },
            {
                "name": "validate_path",
                "description": "Validate a path and show both Windows and Linux formats",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to validate and show conversions for"
                        }
                    },
                    "required": ["path"]
                }
            }
        ]
    
    def _detect_path_type(self, path: str) -> str:
        """Detect whether a path is Windows or Linux format"""
        # Check for Windows path patterns
        if re.match(r'^[A-Za-z]:[\\\/]', path):
            return "windows"
        # Check for Windows UNC paths
        elif path.startswith('\\\\'):
            return "windows"
        # Check for forward slashes indicating Linux
        elif '/' in path and '\\' not in path:
            return "linux"
        # Check for backslashes indicating Windows
        elif '\\' in path and '/' not in path:
            return "windows"
        # Mixed slashes - try to determine by root
        elif path.upper().startswith(f'{self.windows_drive.upper()}:'):
            return "windows"
        elif path.startswith('/mcp'):
            return "linux"
        # Default to Linux if unclear
        return "linux"
    
    def _normalize_path(self, path: str) -> str:
        """Normalize a path by handling various input formats"""
        # Strip quotes if present
        path = path.strip().strip('"').strip("'")
        
        # Replace multiple slashes with single ones
        path = re.sub(r'[\\\/]+', lambda m: m.group(0)[0], path)
        
        return path
    
    def _windows_to_linux(self, path: str) -> str:
        """Convert Windows path to Linux format"""
        path = self._normalize_path(path)
        
        # Handle the configured drive to /mcp conversion
        windows_prefix_backslash = f"{self.windows_drive.upper()}:\\"
        windows_prefix_forward = f"{self.windows_drive.upper()}:/"
        
        if path.upper().startswith(windows_prefix_backslash) or path.upper().startswith(windows_prefix_forward):
            # Remove drive letter and colon (e.g., 'M:\' or 'M:/')
            path = path[3:]  # Remove 'X:\' or 'X:/'
            path = self.linux_root + '/' + path
        
        # Convert all backslashes to forward slashes
        path = path.replace('\\', '/')
        
        # Clean up double slashes
        path = re.sub(r'/{2,}', '/', path)
        
        # Remove trailing slash unless it's the root
        if path != '/' and path.endswith('/'):
            path = path.rstrip('/')
        
        return path
    
    def _linux_to_windows(self, path: str) -> str:
        """Convert Linux path to Windows format"""
        path = self._normalize_path(path)
        
        # Handle the /mcp to configured drive conversion
        if path.startswith(self.linux_root):
            # Remove /mcp and prepend configured drive
            path = path[len(self.linux_root):]
            if path and not path.startswith('/'):
                path = '/' + path
            path = self.windows_root + path[1:] if path and len(path) > 1 else self.windows_root
        
        # Convert all forward slashes to backslashes
        path = path.replace('/', '\\')
        
        # Clean up double backslashes (except at the start for UNC paths)
        if not path.startswith('\\\\'):
            path = re.sub(r'\\{2,}', r'\\', path)
        
        # Remove trailing backslash unless it's the root
        if len(path) > 3 and path.endswith('\\') and not path.endswith(':\\'):
            path = path.rstrip(chr(92))
        
        return path
    
    def convert_path(self, path: str, force_direction: Optional[str] = None) -> ToolResponse:
        """
        Convert a single path between Windows and Linux formats
        
        Args:
            path: The path to convert
            force_direction: Force conversion direction ('to_linux' or 'to_windows')
            
        Returns:
            ToolResponse with converted path
        """
        try:
            # Validate input
            if not path:
                return ToolResponse(
                    success=False,
                    error="Path cannot be empty"
                )
            
            original_path = path
            detected_type = self._detect_path_type(path)
            
            # Determine conversion direction
            if force_direction == "to_linux":
                converted = self._windows_to_linux(path)
                conversion = "windows_to_linux"
            elif force_direction == "to_windows":
                converted = self._linux_to_windows(path)
                conversion = "linux_to_windows"
            else:
                # Auto-detect and convert
                if detected_type == "windows":
                    converted = self._windows_to_linux(path)
                    conversion = "windows_to_linux"
                else:
                    converted = self._linux_to_windows(path)
                    conversion = "linux_to_windows"
            
            return ToolResponse(
                success=True,
                data={
                    "original": original_path,
                    "converted": converted,
                    "detected_type": detected_type,
                    "conversion": conversion
                }
            )
            
        except Exception as e:
            return self.handle_error("convert_path", e)
    
    def convert_multiple_paths(self, paths: List[str], force_direction: Optional[str] = None) -> ToolResponse:
        """
        Convert multiple paths at once
        
        Args:
            paths: List of paths to convert
            force_direction: Force conversion direction for all paths
            
        Returns:
            ToolResponse with list of converted paths
        """
        try:
            if not paths:
                return ToolResponse(
                    success=False,
                    error="No paths provided"
                )
            
            results = []
            for path in paths:
                result = self.convert_path(path, force_direction)
                if result.success:
                    results.append(result.data)
                else:
                    results.append({
                        "original": path,
                        "error": result.error
                    })
            
            # Count successes and failures
            successes = sum(1 for r in results if "converted" in r)
            failures = sum(1 for r in results if "error" in r)
            
            return ToolResponse(
                success=True,
                data={
                    "results": results,
                    "summary": {
                        "total": len(paths),
                        "succeeded": successes,
                        "failed": failures
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("convert_multiple_paths", e)
    
    def validate_fs_path(self, path: str) -> ToolResponse:
        """
        Validate a path and show both Windows and Linux conversions
        
        Args:
            path: Path to validate and convert
            
        Returns:
            ToolResponse with validation info and both conversions
        """
        try:
            if not path:
                return ToolResponse(
                    success=False,
                    error="Path cannot be empty"
                )
            
            original_path = path
            detected_type = self._detect_path_type(path)
            normalized = self._normalize_path(path)
            
            # Get both conversions
            windows_path = self._linux_to_windows(normalized) if detected_type == "linux" else normalized
            linux_path = self._windows_to_linux(normalized) if detected_type == "windows" else normalized
            
            # If the path doesn't start with the expected roots, provide a warning
            warnings = []
            expected_windows_root = f"{self.windows_drive.upper()}:\\"
            if detected_type == "windows" and not windows_path.upper().startswith(expected_windows_root):
                warnings.append(f"Windows path does not start with {expected_windows_root} - conversion may be incomplete")
            elif detected_type == "linux" and not linux_path.startswith('/mcp'):
                warnings.append("Linux path does not start with /mcp - conversion may be incomplete")
            
            # Check if the paths are actually different
            if windows_path == linux_path:
                warnings.append("Path does not appear to be within the M:\\ <--> /mcp mapping")
            
            return ToolResponse(
                success=True,
                data={
                    "original": original_path,
                    "normalized": normalized,
                    "detected_type": detected_type,
                    "windows_format": windows_path,
                    "linux_format": linux_path,
                    "warnings": warnings if warnings else None,
                    "ready_to_copy": {
                        "windows": windows_path,
                        "linux": linux_path
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("validate_path", e)
