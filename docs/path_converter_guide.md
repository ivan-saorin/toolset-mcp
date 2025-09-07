# Path Converter Tool Guide

The Path Converter tool helps convert between Windows and Linux path formats, with configurable drive letter mapping to `/mcp`.

## Configuration

By default, the tool maps `M:\` to `/mcp`, but you can configure this using the `MCP_WINDOWS_DRIVE` environment variable:

```bash
# Use D: drive instead of M:
export MCP_WINDOWS_DRIVE=D

# Use E: drive
export MCP_WINDOWS_DRIVE=E
```

## Overview

When working across Windows and Linux environments, path formats can be problematic:
- Windows uses backslashes and drive letters: `M:\projects\myproject`
- Linux uses forward slashes and root paths: `/mcp/projects/myproject`

This tool automatically handles the conversion between these formats.

## Available Tools

### 1. `convert_path`
Converts a single path between Windows and Linux formats.

**Parameters:**
- `path` (required): The path to convert
- `force_direction` (optional): Force conversion direction
  - `"to_linux"`: Always convert to Linux format
  - `"to_windows"`: Always convert to Windows format
  - If not specified, auto-detects the format and converts to the opposite

**Example:**
```json
{
  "path": "M:\\projects\\toolset-mcp\\README.md"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original": "M:\\projects\\toolset-mcp\\README.md",
    "converted": "/mcp/projects/toolset-mcp/README.md",
    "detected_type": "windows",
    "conversion": "windows_to_linux"
  }
}
```

### 2. `convert_multiple_paths`
Converts multiple paths at once.

**Parameters:**
- `paths` (required): List of paths to convert
- `force_direction` (optional): Force conversion direction for all paths

**Example:**
```json
{
  "paths": [
    "M:\\projects\\atlas-meta",
    "/mcp/data/test.txt",
    "M:\\workspace\\project1"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "original": "M:\\projects\\atlas-meta",
        "converted": "/mcp/projects/atlas-meta",
        "detected_type": "windows",
        "conversion": "windows_to_linux"
      },
      {
        "original": "/mcp/data/test.txt",
        "converted": "M:\\data\\test.txt",
        "detected_type": "linux",
        "conversion": "linux_to_windows"
      },
      {
        "original": "M:\\workspace\\project1",
        "converted": "/mcp/workspace/project1",
        "detected_type": "windows",
        "conversion": "windows_to_linux"
      }
    ],
    "summary": {
      "total": 3,
      "succeeded": 3,
      "failed": 0
    }
  }
}
```

### 3. `validate_path`
Validates a path and shows both Windows and Linux formats.

**Parameters:**
- `path` (required): Path to validate and show conversions for

**Example:**
```json
{
  "path": "M:\\projects\\toolset-mcp\\src"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "original": "M:\\projects\\toolset-mcp\\src",
    "normalized": "M:\\projects\\toolset-mcp\\src",
    "detected_type": "windows",
    "windows_format": "M:\\projects\\toolset-mcp\\src",
    "linux_format": "/mcp/projects/toolset-mcp/src",
    "warnings": null,
    "ready_to_copy": {
      "windows": "M:\\projects\\toolset-mcp\\src",
      "linux": "/mcp/projects/toolset-mcp/src"
    }
  }
}
```

## Usage Tips

1. **Auto-detection**: The tool automatically detects whether a path is Windows or Linux format based on:
   - Drive letters (e.g., `M:`)
   - Path separators (`\` vs `/`)
   - Root indicators (`/mcp`)

2. **VS Code Integration**: When you copy a path in VS Code on Windows:
   - Use `convert_path` with the copied path
   - The tool will return the Linux equivalent you can use

3. **Batch Conversion**: Use `convert_multiple_paths` when you have multiple paths to convert at once.

4. **Validation**: Use `validate_path` when you're unsure about a path or want to see both formats.

## Examples

### Converting a VS Code copied path:
```
Input: "M:\projects\toolset-mcp\src\remote_mcp\features\path_converter\engine.py"
Output: "/mcp/projects/toolset-mcp/src/remote_mcp/features/path_converter/engine.py"
```

### Converting back to Windows:
```
Input: "/mcp/projects/atlas-meta/akasha/knowledge"
Output: "M:\projects\atlas-meta\akasha\knowledge"
```

### Handling edge cases:
- Paths outside the M:\ mapping will be converted but with warnings
- Mixed slashes are normalized
- Trailing slashes are handled appropriately

## Error Handling

The tool provides clear error messages for:
- Empty paths
- Invalid path formats
- Paths that cannot be properly converted

All responses include a `success` field and either `data` (on success) or `error` (on failure).
