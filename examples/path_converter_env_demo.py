#!/usr/bin/env python3
"""
Example: Using Path Converter with Different Drive Configurations
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.remote_mcp.features.path_converter import PathConverterEngine

def demonstrate_with_drive(drive_letter):
    """Demonstrate path conversion with a specific drive letter"""
    # Set the environment variable
    os.environ["MCP_WINDOWS_DRIVE"] = drive_letter
    
    print(f"\n{'=' * 60}")
    print(f"Configuration: {drive_letter}:\\ <--> /mcp")
    print(f"{'=' * 60}\n")
    
    # Initialize converter with new configuration
    converter = PathConverterEngine()
    
    # Test paths
    test_cases = [
        f"{drive_letter}:\\projects\\myapp\\src\\main.py",
        f"{drive_letter}:\\data\\config.json",
        "/mcp/projects/myapp/src/main.py",
        "/mcp/data/config.json"
    ]
    
    for path in test_cases:
        result = converter.convert_path(path)
        if result.success:
            data = result.data
            print(f"Original: {data['original']}")
            print(f"Converted: {data['converted']}")
            print(f"Type: {data['detected_type']} → {data['conversion']}")
            print()

def main():
    """Main demonstration"""
    print("Path Converter - Environment Variable Configuration Demo")
    print("=" * 60)
    
    # Show default configuration
    default_drive = os.environ.get("MCP_WINDOWS_DRIVE", "M")
    print(f"\nDefault configuration (MCP_WINDOWS_DRIVE not set): {default_drive}")
    
    # Demonstrate with different drives
    for drive in ["M", "D", "E", "Z"]:
        demonstrate_with_drive(drive)
    
    # Restore original environment
    if "MCP_WINDOWS_DRIVE" in os.environ:
        del os.environ["MCP_WINDOWS_DRIVE"]
    
    print("\n" + "=" * 60)
    print("Demo complete! You can set MCP_WINDOWS_DRIVE to any drive letter.")
    print("Examples:")
    print("  export MCP_WINDOWS_DRIVE=D")
    print("  set MCP_WINDOWS_DRIVE=E  (Windows)")
    print("  MCP_WINDOWS_DRIVE=Z python run_server.py")

if __name__ == "__main__":
    main()
