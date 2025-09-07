# Path Converter Feature

Convert between Windows and Linux path formats with configurable drive mapping.

## Features

- **Auto-detection** of path format (Windows vs Linux)
- **Configurable drive mapping** via `MCP_WINDOWS_DRIVE` environment variable
- **Batch conversion** for multiple paths
- **Path validation** with warnings for edge cases

## Configuration

The Windows drive letter that maps to `/mcp` can be configured:

```bash
# Default mapping (if not set)
M:\ <--> /mcp

# Custom mapping examples
export MCP_WINDOWS_DRIVE=D  # D:\ <--> /mcp
export MCP_WINDOWS_DRIVE=E  # E:\ <--> /mcp
```

## Tools

### convert_path
Converts a single path between Windows and Linux formats.

### convert_multiple_paths
Converts multiple paths in one operation.

### validate_path
Validates a path and shows both Windows and Linux formats.

## Example Usage

```python
# Default configuration (M:)
converter = PathConverterEngine()

# Convert Windows to Linux
result = converter.convert_path("M:\\projects\\myapp\\src\\main.py")
# Output: "/mcp/projects/myapp/src/main.py"

# With custom drive configuration
os.environ["MCP_WINDOWS_DRIVE"] = "D"
converter = PathConverterEngine()  # Now uses D:\

result = converter.convert_path("D:\\projects\\myapp\\src\\main.py")
# Output: "/mcp/projects/myapp/src/main.py"
```

## Version History

- v1.1.0: Added configurable drive mapping via environment variable
- v1.0.0: Initial implementation with hardcoded M:\ mapping
