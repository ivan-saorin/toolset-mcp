#!/usr/bin/env python3
"""
Test script to verify filesystem tools work with both Windows and Linux paths
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from remote_mcp.server import (
    fs_read_file, fs_write_file, fs_list_directory, 
    fs_create_directory, fs_get_file_info, fs_move_file,
    fs_copy_file, fs_search_files, convert_to_linux_path
)

async def test_path_conversion():
    """Test automatic path conversion in filesystem tools"""
    
    print("=== Testing Filesystem Path Conversion ===\n")
    
    # Test the convert_to_linux_path function directly
    test_paths = [
        "M:\\projects\\toolset-mcp\\README.md",
        "/mcp/projects/toolset-mcp/README.md",
        "M:/projects/toolset-mcp/test.txt",
        "M:\\\\projects\\\\toolset-mcp\\\\docs",
    ]
    
    print("1. Testing path conversion function:")
    for path in test_paths:
        converted = convert_to_linux_path(path)
        print(f"   {path} -> {converted}")
    print()
    
    # Test filesystem operations with Windows paths
    print("2. Testing filesystem operations with Windows paths:")
    
    # Test fs_list_directory with Windows path
    print("\n   Testing fs_list_directory with Windows path:")
    windows_path = "M:\\projects\\toolset-mcp"
    result = await fs_list_directory(windows_path)
    if "error" not in result:
        print(f"   ✓ Listed directory using Windows path: {windows_path}")
        print(f"     Found {result['total']} items")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Test fs_get_file_info with Windows path
    print("\n   Testing fs_get_file_info with Windows path:")
    windows_file = "M:\\projects\\toolset-mcp\\README.md"
    result = await fs_get_file_info(windows_file)
    if "error" not in result:
        print(f"   ✓ Got file info using Windows path: {windows_file}")
        print(f"     File size: {result['size_human']}")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Test fs_read_file with Windows path
    print("\n   Testing fs_read_file with Windows path:")
    windows_file = "M:\\projects\\toolset-mcp\\pyproject.toml"
    result = await fs_read_file(windows_file)
    if "error" not in result:
        print(f"   ✓ Read file using Windows path: {windows_file}")
        print(f"     Content size: {result['size']} bytes")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Test fs_search_files with Windows path
    print("\n   Testing fs_search_files with Windows path:")
    search_path = "M:\\projects\\toolset-mcp"
    result = await fs_search_files(search_path, "*.py")
    if "error" not in result:
        print(f"   ✓ Searched files using Windows path: {search_path}")
        print(f"     Found {result['total']} matches")
    else:
        print(f"   ✗ Error: {result['error']}")
    
    # Test write and copy operations
    print("\n   Testing write/copy operations with Windows paths:")
    
    # Create a test file with Windows path
    test_file_windows = "M:\\projects\\toolset-mcp\\test_windows_path.txt"
    result = await fs_write_file(test_file_windows, "Test content from Windows path")
    if "error" not in result:
        print(f"   ✓ Created file using Windows path: {test_file_windows}")
    else:
        print(f"   ✗ Error creating file: {result['error']}")
    
    # Copy the file using Windows paths
    if "error" not in result:
        copy_dest_windows = "M:\\projects\\toolset-mcp\\test_windows_copy.txt"
        result = await fs_copy_file(test_file_windows, copy_dest_windows)
        if "error" not in result:
            print(f"   ✓ Copied file using Windows paths")
        else:
            print(f"   ✗ Error copying file: {result['error']}")
        
        # Clean up test files
        try:
            os.unlink("/mcp/projects/toolset-mcp/test_windows_path.txt")
            os.unlink("/mcp/projects/toolset-mcp/test_windows_copy.txt")
        except:
            pass
    
    print("\n=== Path Conversion Test Complete ===")

if __name__ == "__main__":
    # Set allowed directories for testing
    os.environ["ALLOWED_DIRECTORIES"] = "/mcp"
    
    asyncio.run(test_path_conversion())
