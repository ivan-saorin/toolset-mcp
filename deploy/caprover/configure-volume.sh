#!/bin/bash
# Script to update CapRover deployment with volume mount

echo "=== CapRover Volume Mount Configuration ==="
echo
echo "This script will help you configure volume mounting for atlas-toolset-mcp"
echo

# Check if user wants to proceed
read -p "Do you want to configure /home/auto/mcp access? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo
echo "To mount /home/auto/mcp in your CapRover app, you need to:"
echo
echo "1. SSH into your CapRover server:"
echo "   ssh root@your-caprover-server"
echo
echo "2. Create a custom configuration file:"
echo "   sudo mkdir -p /captain/data"
echo "   sudo nano /captain/data/config-override-atlas-toolset-mcp.json"
echo
echo "3. Add this content:"
cat << 'EOF'
{
  "appName": "atlas-toolset-mcp",
  "volumes": [
    {
      "hostPath": "/home/auto/mcp",
      "containerPath": "/data/mcp"
    }
  ]
}
EOF
echo
echo "4. In CapRover web interface:"
echo "   - Go to your app settings"
echo "   - Update the environment variable:"
echo "     ALLOWED_DIRECTORIES=/data/mcp"
echo "   - Click 'Save & Restart'"
echo
echo "5. Test the configuration:"
echo "   curl https://atlas-toolset-mcp.your-domain.com/health"
echo

# Alternative method using Docker
echo "=== Alternative: Direct Docker Volume Mount ==="
echo
echo "If the above doesn't work, you can modify the container directly:"
echo
echo "1. Find your app container:"
echo "   docker ps | grep atlas-toolset-mcp"
echo
echo "2. Stop the container and recreate with volume:"
echo "   docker stop srv-captain--atlas-toolset-mcp"
echo "   docker run -d --name srv-captain--atlas-toolset-mcp \\"
echo "     -v /home/auto/mcp:/data/mcp \\"
echo "     -e ALLOWED_DIRECTORIES=/data/mcp \\"
echo "     -p 80:80 \\"
echo "     img-captain--atlas-toolset-mcp"
echo

echo "=== Testing Access ==="
echo
echo "Once configured, test with these commands:"
echo "1. List allowed directories:"
echo "   curl -X POST https://your-app-url/mcp -d '{\"method\":\"fs_list_allowed_directories\"}'"
echo
echo "2. List contents of /data/mcp:"
echo "   curl -X POST https://your-app-url/mcp -d '{\"method\":\"fs_list_directory\",\"params\":{\"path\":\"/data/mcp\"}}'"
