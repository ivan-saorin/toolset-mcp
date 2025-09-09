#!/bin/bash
# Fix script for toolset-mcp permission issues

echo "Fixing toolset-mcp permissions and rebuilding..."
echo "=============================================="

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/../.."

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "Warning: Running as root. This might cause permission issues."
fi

# Step 1: Stop existing containers
echo "Step 1: Stopping existing containers..."
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" down 2>/dev/null || true
docker stop $(docker ps -q --filter ancestor=toolset-mcp) 2>/dev/null || true

# Step 2: Fix local directory permissions
echo "Step 2: Fixing local directory permissions..."
if [ -d "/mnt/m/projects" ]; then
    echo "Setting ownership for /mnt/m/projects to current user..."
    sudo chown -R $(id -u):$(id -g) /mnt/m/projects 2>/dev/null || \
        echo "Could not change ownership. You may need to run: sudo chown -R auto:auto /mnt/m/projects"
fi

# Step 3: Clean Docker artifacts
echo "Step 3: Cleaning Docker artifacts..."
docker system prune -f

# Step 4: Replace the original Dockerfile
echo "Step 4: Updating Dockerfile..."
if [ -f "$PROJECT_ROOT/deploy/caprover/Dockerfile.fixed" ]; then
    cp "$PROJECT_ROOT/deploy/caprover/Dockerfile" "$PROJECT_ROOT/deploy/caprover/Dockerfile.backup"
    cp "$PROJECT_ROOT/deploy/caprover/Dockerfile.fixed" "$PROJECT_ROOT/deploy/caprover/Dockerfile"
    echo "Dockerfile updated (backup saved as Dockerfile.backup)"
fi

# Step 5: Build new image
echo "Step 5: Building new Docker image..."
cd "$PROJECT_ROOT"
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" build --no-cache

# Step 6: Start the service
echo "Step 6: Starting the service..."
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" up -d

# Step 7: Check logs
echo "Step 7: Checking service status..."
sleep 3
docker-compose -f "$SCRIPT_DIR/docker-compose.yml" logs --tail=20

# Step 8: Test the service
echo "Step 8: Testing the service..."
sleep 2
curl -f http://localhost:8000/health 2>/dev/null && \
    echo "✓ Service is healthy!" || \
    echo "✗ Service health check failed. Check logs with: docker-compose -f $SCRIPT_DIR/docker-compose.yml logs"

echo ""
echo "Fix complete!"
echo ""
echo "If you still have issues:"
echo "1. Check that your user ID is 1000: id -u"
echo "2. If not, update the Dockerfile.fixed with your UID/GID"
echo "3. Make sure /mnt/m/projects is accessible: ls -la /mnt/m/projects"
echo "4. Check Docker logs: docker-compose -f $SCRIPT_DIR/docker-compose.yml logs -f"
