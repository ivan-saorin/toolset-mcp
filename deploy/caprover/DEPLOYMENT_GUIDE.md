# CapRover Deployment Guide for Atlas Toolset MCP

## Overview

This guide explains how to deploy the Atlas Toolset MCP server on CapRover with proper filesystem access configuration.

## Prerequisites

- CapRover instance running
- Captain CLI installed and logged in
- Basic understanding of Docker volumes

## Deployment Steps

### 1. Create the App in CapRover

```bash
caprover apps:create --appName atlas-toolset-mcp
```

### 2. Configure Environment Variables

In CapRover web interface, navigate to your app and add these environment variables:

```bash
# Core settings (already in Dockerfile, but can override)
PORT=80
HOST=0.0.0.0

# Filesystem configuration - IMPORTANT!
# Specify allowed directories as comma-separated list
ALLOWED_DIRECTORIES=/data/shared,/data/user,/data/projects,/data/workspace
```

### 3. Configure Persistent Volumes

In CapRover app settings, add these persistent directories:

1. **Shared Data Volume**
   - Container Path: `/data/shared`
   - Label: `shared-data`
   
2. **User Data Volume**
   - Container Path: `/data/user`
   - Label: `user-data`
   
3. **Projects Volume**
   - Container Path: `/data/projects`
   - Label: `projects`
   
4. **Workspace Volume**
   - Container Path: `/data/workspace`
   - Label: `workspace`

### 4. Deploy the Application

From the repository root:

```bash
caprover deploy
```

Or using git push:

```bash
git remote add caprover https://captain.yourdomain.com/git/atlas-toolset-mcp
git push caprover main
```

## Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_DIRECTORIES` | Comma-separated list of allowed directories | `/data/shared,/data/user,/data/projects,/data/workspace` |
| `PORT` | Server port | `80` |
| `HOST` | Server host | `0.0.0.0` |

### Volume Mapping Strategies

#### Option 1: Standard CapRover Volumes (Recommended)

Use CapRover's built-in volume management:

```javascript
// In your app configuration
{
  "persistentDirectories": [
    {
      "path": "/data/shared",
      "label": "shared-data"
    },
    {
      "path": "/data/user",
      "label": "user-data"
    }
  ]
}
```

#### Option 2: Bind Mounts to Host Directories

For direct access to host filesystem (requires SSH access to server):

1. SSH into your CapRover server
2. Create host directories:
   ```bash
   mkdir -p /srv/atlas-mcp/shared
   mkdir -p /srv/atlas-mcp/user
   mkdir -p /srv/atlas-mcp/projects
   ```

3. In CapRover app configuration, use bind mounts:
   ```
   /srv/atlas-mcp/shared:/data/shared
   /srv/atlas-mcp/user:/data/user
   /srv/atlas-mcp/projects:/data/projects
   ```

#### Option 3: Network Storage

For shared access across multiple instances:

1. Set up NFS or similar network storage
2. Mount on CapRover host:
   ```bash
   mount -t nfs storage-server:/export/atlas /mnt/atlas-storage
   ```

3. Bind mount in CapRover:
   ```
   /mnt/atlas-storage:/data/shared
   ```

## Security Considerations

1. **Restrict Directory Access**: Only allow access to specific directories needed for your use case
2. **Use Read-Only Mounts**: For directories that don't need write access
3. **Regular Backups**: Set up automated backups for persistent volumes
4. **Access Control**: Consider implementing additional authentication if exposing publicly
5. **Safe Deletion**: The server only supports fake deletion - files are marked as deleted but never actually removed from disk. This prevents accidental data loss.

## Testing the Deployment

1. Check health endpoint:
   ```bash
   curl https://atlas-toolset-mcp.yourdomain.com/health
   ```

2. Test filesystem access:
   ```bash
   # Using the MCP inspector
   npx @modelcontextprotocol/inspector --url https://atlas-toolset-mcp.yourdomain.com/mcp
   
   # Call fs_list_allowed_directories to verify configuration
   ```

3. Create a test file:
   ```javascript
   // In MCP inspector
   await fs_write_file({
     path: "/data/shared/test.txt",
     content: "Hello from CapRover!"
   });
   ```

## Troubleshooting

### Issue: "Access denied: path is outside allowed directories"

**Solution**: Check that:
1. `ALLOWED_DIRECTORIES` environment variable is set correctly
2. The directories exist in the container
3. Volumes are properly mounted

### Issue: Files disappear after restart

**Solution**: Ensure persistent volumes are configured in CapRover app settings

### Issue: Permission denied errors

**Solution**: The container runs as root by default. If you need different permissions:
1. Modify the Dockerfile to create a specific user
2. Set proper ownership on mounted volumes

## Advanced Configuration

### Custom Allowed Directories

You can customize allowed directories per deployment:

```bash
# For development environment
ALLOWED_DIRECTORIES=/data/dev,/data/test

# For production
ALLOWED_DIRECTORIES=/data/prod/secure,/data/prod/public

# For specific use cases
ALLOWED_DIRECTORIES=/data/ml-models,/data/datasets,/data/results
```

### Monitoring and Logs

View logs in CapRover:
```bash
caprover logs --appName atlas-toolset-mcp
```

Or through the web interface in the app's "Logs" section.

## Example Use Cases

### 1. Shared Team Workspace
```bash
ALLOWED_DIRECTORIES=/data/team/shared,/data/team/projects,/data/team/resources
```

### 2. Personal Cloud Storage
```bash
ALLOWED_DIRECTORIES=/data/users/ivan,/data/users/ivan/projects
```

### 3. Data Processing Pipeline
```bash
ALLOWED_DIRECTORIES=/data/input,/data/processing,/data/output,/data/logs
```

## Next Steps

1. Set up automated backups for your volumes
2. Configure monitoring/alerts
3. Implement access control if needed
4. Consider using S3-compatible storage for large files

## Support

For issues specific to the MCP server, check the logs and ensure all environment variables are set correctly. For CapRover-specific issues, consult the CapRover documentation.
