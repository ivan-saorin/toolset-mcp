# Atlas Toolset MCP - CapRover Deployment

This directory contains all the files needed to deploy the Atlas Toolset MCP server on CapRover with proper filesystem access configuration.

## Files

- **Dockerfile**: Production-ready Docker image with volume support
- **docker-compose.yml**: CapRover-compatible compose file with volume definitions
- **captain-definition**: Points CapRover to use this Dockerfile
- **DEPLOYMENT_GUIDE.md**: Comprehensive deployment instructions
- **setup.sh**: Automated setup script for quick deployment
- **config/.env.template**: Environment variable template

## Quick Start

1. Make the setup script executable:
   ```bash
   chmod +x setup.sh
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Follow the prompts to configure your deployment

## Manual Deployment

If you prefer manual setup, see `DEPLOYMENT_GUIDE.md` for detailed instructions.

## Key Configuration

The most important configuration is the `ALLOWED_DIRECTORIES` environment variable, which controls which directories the MCP filesystem tools can access.

Example configurations:

```bash
# Development
ALLOWED_DIRECTORIES=/data/dev,/data/test

# Production
ALLOWED_DIRECTORIES=/data/secure,/data/public,/data/workspace

# Personal use
ALLOWED_DIRECTORIES=/data/documents,/data/projects,/data/downloads
```

## Volume Persistence

Ensure you configure persistent volumes in CapRover for any directories you want to preserve across container restarts.

## Support

For deployment issues, check:
1. CapRover logs: `caprover logs --appName your-app-name`
2. Health check: `https://your-app.domain.com/health`
3. The comprehensive DEPLOYMENT_GUIDE.md

## Security Notes

1. **Directory Access**: The filesystem tools respect the `ALLOWED_DIRECTORIES` configuration. Never expose sensitive system directories unless absolutely necessary.

2. **Deletion Safety**: The server implements FAKE DELETION ONLY. Files are never actually removed from disk - they are only marked as deleted and can be restored at any time. This is a safety feature to prevent accidental data loss. See `DELETION_SAFETY.md` for details.
