#!/bin/bash

# Atlas Toolset MCP - CapRover Setup Script
# This script helps set up the initial configuration for CapRover deployment

echo "Atlas Toolset MCP - CapRover Setup"
echo "=================================="
echo ""

# Check if CapRover CLI is installed
if ! command -v caprover &> /dev/null; then
    echo "Error: CapRover CLI is not installed."
    echo "Please install it with: npm install -g caprover"
    exit 1
fi

# Get app name
read -p "Enter CapRover app name (default: atlas-toolset-mcp): " APP_NAME
APP_NAME=${APP_NAME:-atlas-toolset-mcp}

# Create app if it doesn't exist
echo ""
echo "Creating CapRover app: $APP_NAME"
caprover apps:create --appName "$APP_NAME" 2>/dev/null || echo "App might already exist, continuing..."

# Configure environment variables
echo ""
echo "Configuring environment variables..."
echo ""
echo "Enter allowed directories (comma-separated)."
echo "Examples:"
echo "  - /data/shared,/data/projects"
echo "  - /data/users/ivan,/data/workspace"
echo ""
read -p "Allowed directories (default: /data/shared,/data/user,/data/projects,/data/workspace): " ALLOWED_DIRS
ALLOWED_DIRS=${ALLOWED_DIRS:-/data/shared,/data/user,/data/projects,/data/workspace}

# Create environment variable command
echo ""
echo "Setting environment variables..."
caprover apps:envVars --appName "$APP_NAME" --envVars "ALLOWED_DIRECTORIES=$ALLOWED_DIRS"

# Configure persistent volumes
echo ""
echo "Configure persistent volumes?"
echo "This will set up the following volumes:"
IFS=',' read -ra DIRS <<< "$ALLOWED_DIRS"
for dir in "${DIRS[@]}"; do
    echo "  - $dir"
done
echo ""
read -p "Configure volumes? (y/n): " CONFIGURE_VOLUMES

if [[ $CONFIGURE_VOLUMES == "y" ]]; then
    echo ""
    echo "Please configure the following persistent directories in CapRover web interface:"
    echo ""
    for i in "${!DIRS[@]}"; do
        dir="${DIRS[$i]}"
        label=$(basename "$dir")
        echo "$((i+1)). Container Path: $dir"
        echo "   Label: $label-data"
        echo ""
    done
    echo "Navigate to: https://captain.yourdomain.com/apps/appDetails/$APP_NAME"
    echo "Go to 'App Configs' tab and add these under 'Persistent Directories'"
    echo ""
    read -p "Press Enter when you've configured the volumes..."
fi

# Deploy
echo ""
echo "Ready to deploy!"
echo ""
echo "To deploy from this directory, run:"
echo "  caprover deploy"
echo ""
echo "Or set up git deployment:"
echo "  git remote add caprover $(caprover apps:gitUrl --appName "$APP_NAME" 2>/dev/null || echo "https://captain.yourdomain.com/git/$APP_NAME")"
echo "  git push caprover main"
echo ""
echo "Setup complete!"
