#!/usr/bin/env python3
"""
Quick test to verify environment variable configuration works
"""

import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.remote_mcp.features.path_converter import PathConverterEngine

# Test 1: Default configuration
print("Test 1: Default configuration (no env var set)")
if "MCP_WINDOWS_DRIVE" in os.environ:
    del os.environ["MCP_WINDOWS_DRIVE"]
converter1 = PathConverterEngine()
result = converter1.convert_path("M:\\test\\file.txt")
print(f"Result: {result.data['converted'] if result.success else 'ERROR'}")
print(f"Expected: /mcp/test/file.txt")
print()

# Test 2: Custom drive D
print("Test 2: Custom configuration (D drive)")
os.environ["MCP_WINDOWS_DRIVE"] = "D"
converter2 = PathConverterEngine()
result = converter2.convert_path("D:\\test\\file.txt")
print(f"Result: {result.data['converted'] if result.success else 'ERROR'}")
print(f"Expected: /mcp/test/file.txt")
print()

# Test 3: Custom drive E
print("Test 3: Custom configuration (E drive)")
os.environ["MCP_WINDOWS_DRIVE"] = "E"
converter3 = PathConverterEngine()
result = converter3.convert_path("E:\\test\\file.txt")
print(f"Result: {result.data['converted'] if result.success else 'ERROR'}")
print(f"Expected: /mcp/test/file.txt")
print()

# Test 4: Reverse conversion
print("Test 4: Linux to Windows with E drive")
result = converter3.convert_path("/mcp/test/file.txt")
print(f"Result: {result.data['converted'] if result.success else 'ERROR'}")
print(f"Expected: E:\\test\\file.txt")
print()

print("All tests completed!")
