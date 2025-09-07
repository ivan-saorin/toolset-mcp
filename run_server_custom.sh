#!/bin/bash
# Example script to run the server with a custom drive mapping

# Set the Windows drive that maps to /mcp
# Change this to your preferred drive letter
export MCP_WINDOWS_DRIVE=D

# You can also set other environment variables here
export PORT=8000
export HOST=0.0.0.0

echo "Starting Atlas Toolset MCP Server..."
echo "Path mapping: ${MCP_WINDOWS_DRIVE}:\\ <--> /mcp"
echo

# Run the server
python -m src.remote_mcp.server
