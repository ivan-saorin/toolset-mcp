#!/usr/bin/env python3
"""
Test script for the path converter feature
"""

import os
from src.remote_mcp.features.path_converter import PathConverterEngine

def test_path_converter():
    """Test the path converter functionality"""
    print("Testing Path Converter Engine")
    print("=" * 50)
    
    # Show current configuration
    current_drive = os.environ.get("MCP_WINDOWS_DRIVE", "M")
    print(f"\nCurrent configuration:")
    print(f"MCP_WINDOWS_DRIVE = {current_drive}")
    print(f"Mapping: {current_drive}:\\ <--> /mcp")
    
    # Initialize the engine
    converter = PathConverterEngine()
    
    # Test cases
    test_paths = [
        # Windows paths
        "M:\\projects\\atlas-meta\\akasha",
        "M:\\projects\\toolset-mcp\\src\\remote_mcp",
        "M:\\data\\test.txt",
        "M:\\",
        
        # Linux paths
        "/mcp/projects/atlas-meta/akasha",
        "/mcp/projects/toolset-mcp/src/remote_mcp",
        "/mcp/data/test.txt",
        "/mcp",
        
        # Mixed/edge cases
        "M:/projects/test",  # Forward slash in Windows path
        "/mcp\\projects\\test",  # Backslash in Linux path
        "C:\\Windows\\System32",  # Different drive (should not convert)
        "/home/user/documents",  # Outside /mcp (should not convert)
    ]
    
    print("\n1. Testing single path conversions:")
    for path in test_paths:
        result = converter.convert_path(path)
        if result.success:
            data = result.data
            print(f"\nOriginal: {data['original']}")
            print(f"Detected: {data['detected_type']}")
            print(f"Converted: {data['converted']}")
            print(f"Conversion: {data['conversion']}")
        else:
            print(f"\nError converting {path}: {result.error}")
    
    print("\n" + "=" * 50)
    print("\n2. Testing forced conversions:")
    
    # Force to Linux
    test_path = "M:\\projects\\test.txt"
    result = converter.convert_path(test_path, force_direction="to_linux")
    if result.success:
        print(f"\nForce to Linux:")
        print(f"Original: {result.data['original']}")
        print(f"Converted: {result.data['converted']}")
    
    # Force to Windows
    test_path = "/mcp/projects/test.txt"
    result = converter.convert_path(test_path, force_direction="to_windows")
    if result.success:
        print(f"\nForce to Windows:")
        print(f"Original: {result.data['original']}")
        print(f"Converted: {result.data['converted']}")
    
    print("\n" + "=" * 50)
    print("\n3. Testing multiple paths conversion:")
    
    paths = [
        "M:\\projects\\atlas-meta",
        "/mcp/data/test.txt",
        "M:\\workspace\\project1",
        "/mcp/tools/script.py"
    ]
    
    result = converter.convert_multiple_paths(paths)
    if result.success:
        data = result.data
        print(f"\nConverted {data['summary']['succeeded']} paths successfully")
        print(f"Failed: {data['summary']['failed']}")
        for r in data['results']:
            if 'converted' in r:
                print(f"\n  {r['original']} -> {r['converted']}")
            else:
                print(f"\n  {r['original']} -> ERROR: {r['error']}")
    
    print("\n" + "=" * 50)
    print("\n4. Testing path validation:")
    
    validate_paths = [
        "M:\\projects\\toolset-mcp\\README.md",
        "/mcp/projects/toolset-mcp/README.md",
        "C:\\Users\\Documents\\file.txt",
        "/home/user/file.txt"
    ]
    
    for path in validate_paths:
        result = converter.validate_path(path)
        if result.success:
            data = result.data
            print(f"\nValidating: {data['original']}")
            print(f"  Windows format: {data['windows_format']}")
            print(f"  Linux format: {data['linux_format']}")
            if data.get('warnings'):
                print(f"  Warnings: {', '.join(data['warnings'])}")
        else:
            print(f"\nError validating {path}: {result.error}")
    
    print("\n" + "=" * 50)
    print("\nPath Converter tests completed!")

if __name__ == "__main__":
    test_path_converter()
