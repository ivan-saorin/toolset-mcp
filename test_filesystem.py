#!/usr/bin/env python3
"""
Test script for filesystem tools in Atlas Toolset MCP Server
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from remote_mcp.server import (
    fs_list_allowed_directories,
    fs_read_file,
    fs_write_file,
    fs_list_directory,
    fs_copy_file,
    fs_delete_file,
    fs_list_deleted,
    fs_restore_deleted,
    fs_search_files,
    fs_get_file_info
)

async def test_filesystem_tools():
    """Test filesystem tools"""
    print("Testing Filesystem Tools")
    print("=" * 60)
    
    # Test 1: List allowed directories
    print("\n1. Testing fs_list_allowed_directories:")
    result = await fs_list_allowed_directories()
    print(f"   Allowed directories: {result.get('allowed_directories', [])}")
    
    # Test 2: Write a test file
    test_file = "/tmp/test_fs_tools.txt"
    print(f"\n2. Testing fs_write_file to {test_file}:")
    result = await fs_write_file(test_file, "Hello from filesystem tools!")
    print(f"   Result: {result.get('message', result.get('error'))}")
    
    # Test 3: Read the file
    print(f"\n3. Testing fs_read_file from {test_file}:")
    result = await fs_read_file(test_file)
    print(f"   Content: {result.get('content', result.get('error'))[:50]}...")
    
    # Test 4: Get file info
    print(f"\n4. Testing fs_get_file_info for {test_file}:")
    result = await fs_get_file_info(test_file)
    print(f"   Type: {result.get('type')}, Size: {result.get('size')} bytes")
    
    # Test 5: Copy file
    copy_file = "/tmp/test_fs_tools_copy.txt"
    print(f"\n5. Testing fs_copy_file to {copy_file}:")
    result = await fs_copy_file(test_file, copy_file)
    print(f"   Result: {result.get('message', result.get('error'))}")
    
    # Test 6: List directory
    print("\n6. Testing fs_list_directory for /tmp:")
    result = await fs_list_directory("/tmp")
    items = result.get('items', [])
    test_files = [item for item in items if 'test_fs_tools' in item]
    print(f"   Found test files: {test_files}")
    
    # Test 7: Search files
    print("\n7. Testing fs_search_files for 'test_fs' in /tmp:")
    result = await fs_search_files("/tmp", "test_fs")
    matches = result.get('matches', [])
    print(f"   Found {len(matches)} matches")
    
    # Test 8: Delete file (fake delete)
    print(f"\n8. Testing fs_delete_file (fake) for {test_file}:")
    result = await fs_delete_file(test_file, permanent=False)
    print(f"   Result: {result.get('message', result.get('error'))}")
    
    # Test 9: List deleted files
    print("\n9. Testing fs_list_deleted:")
    result = await fs_list_deleted()
    deleted = result.get('deleted_files', [])
    print(f"   Deleted files: {len(deleted)}")
    for file in deleted:
        print(f"     - {file['path']} ({file['type']})")
    
    # Test 10: Restore deleted file
    print(f"\n10. Testing fs_restore_deleted for {test_file}:")
    result = await fs_restore_deleted(test_file)
    print(f"    Result: {result.get('message', result.get('error'))}")
    
    # Test 11: Permanently delete files
    print(f"\n11. Testing permanent deletion:")
    result = await fs_delete_file(test_file, permanent=True)
    print(f"    Delete {test_file}: {result.get('message', result.get('error'))}")
    result = await fs_delete_file(copy_file, permanent=True)
    print(f"    Delete {copy_file}: {result.get('message', result.get('error'))}")
    
    print("\n" + "=" * 60)
    print("Filesystem tools test completed!")

if __name__ == "__main__":
    asyncio.run(test_filesystem_tools())
