# IMPORTANT: File Deletion Safety

## Atlas Toolset MCP - Deletion Behavior

This server implements **SAFE DELETION ONLY**. 

### What this means:

1. **No Real Deletion**: The `fs_delete_file` operation NEVER actually removes files from disk
2. **Fake Deletion**: Files are only marked as deleted in memory
3. **Always Reversible**: Any "deleted" file can be restored using `fs_restore_deleted`
4. **Data Safety**: Your data is always safe - accidental deletion cannot cause permanent data loss

### How it works:

```javascript
// When you delete a file:
await fs_delete_file({ path: "/data/important-file.txt" });

// What happens:
// 1. File is added to DELETED_FILES set
// 2. Metadata is saved (deletion time, size, type)
// 3. File remains on disk untouched
// 4. File becomes invisible to listing/reading operations

// To restore:
await fs_restore_deleted({ path: "/data/important-file.txt" });
// File is immediately accessible again
```

### Why this design:

- **Prevents accidents**: No risk of permanently losing important data
- **Audit trail**: Track what was deleted and when
- **Easy recovery**: Instant restoration of any deleted file
- **Safety first**: Follows the principle of least destruction

### If you need actual deletion:

If you have a specific use case that requires actual file deletion (e.g., GDPR compliance, disk space management), you would need to:

1. SSH into the server
2. Manually delete files using system commands
3. Or implement a separate cleanup process outside the MCP

This is intentionally not supported through the MCP API to maintain data safety.

## Configuration

The deletion behavior is hardcoded and cannot be changed via configuration. This is a deliberate safety feature.
