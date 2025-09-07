@echo off
REM Example batch file to run the server with a custom drive mapping

REM Set the Windows drive that maps to /mcp
REM Change this to your preferred drive letter
set MCP_WINDOWS_DRIVE=D

REM You can also set other environment variables here
set PORT=8000
set HOST=0.0.0.0

echo Starting Atlas Toolset MCP Server...
echo Path mapping: %MCP_WINDOWS_DRIVE%:\ ^<--^> /mcp
echo.

REM Run the server
python -m src.remote_mcp.server

pause
