# Using Atlas Toolset MCP Filesystem Features

Once deployed on CapRover, here's how to use the filesystem features:

## 1. Check Allowed Directories

First, verify which directories are accessible:

```javascript
// Using MCP Inspector or your client
const result = await fs_list_allowed_directories();
console.log(result);
// Output: {
//   "allowed_directories": ["/data/shared", "/data/user", "/data/projects", "/data/workspace"],
//   "total": 4
// }
```

## 2. Basic File Operations

### Write a file
```javascript
await fs_write_file({
  path: "/data/shared/hello.txt",
  content: "Hello from CapRover!"
});
```

### Read a file
```javascript
const file = await fs_read_file({
  path: "/data/shared/hello.txt"
});
console.log(file.content);
```

### List directory
```javascript
const listing = await fs_list_directory({
  path: "/data/shared"
});
console.log(listing.items);
```

## 3. Advanced Operations

### Search for files
```javascript
const results = await fs_search_files({
  path: "/data/projects",
  pattern: "*.py",
  exclude_patterns: ["__pycache__", "*.pyc"]
});
```

### Copy entire directory
```javascript
await fs_copy_directory({
  source: "/data/projects/template",
  destination: "/data/workspace/new-project",
  exclude_patterns: [".git", "node_modules"]
});
```

### Get file information
```javascript
const info = await fs_get_file_info({
  path: "/data/shared/document.pdf"
});
console.log(`Size: ${info.size_human}, Modified: ${info.modified}`);
```

## 4. Safe Deletion Feature

For safety, the MCP only supports "fake deletion" where files are marked as deleted but NEVER actually removed from disk:

```javascript
// Delete a file (fake deletion only)
await fs_delete_file({
  path: "/data/workspace/draft.txt"
});
// Result: File is marked as deleted but still exists on disk

// List deleted files
const deleted = await fs_list_deleted();
console.log(deleted.deleted_files);

// Restore a deleted file
await fs_restore_deleted({
  path: "/data/workspace/draft.txt"
});
// Result: File is unmarked and accessible again
```

**Important**: Real/permanent deletion is NOT supported. All deletions are reversible to prevent data loss.

## 5. Working with Multiple Files

```javascript
// Read multiple files at once
const files = await fs_read_multiple_files({
  paths: [
    "/data/projects/config.json",
    "/data/projects/README.md",
    "/data/projects/main.py"
  ]
});

// Process results
for (const [path, data] of Object.entries(files.files)) {
  console.log(`File: ${path}, Size: ${data.size} bytes`);
}
```

## 6. Directory Trees

```javascript
// Get full directory structure
const tree = await fs_directory_tree({
  path: "/data/projects"
});
console.log(JSON.stringify(tree.tree, null, 2));
```

## 7. File Editing

```javascript
// Make specific edits to a file
await fs_edit_file({
  path: "/data/projects/config.json",
  edits: [
    {
      old_text: '"version": "1.0.0"',
      new_text: '"version": "1.1.0"'
    },
    {
      old_text: '"debug": true',
      new_text: '"debug": false'
    }
  ],
  dry_run: false  // Set to true to preview changes
});
```

## Common Use Cases

### Project Template System
```javascript
// Create project from template
await fs_copy_directory({
  source: "/data/shared/templates/python-project",
  destination: "/data/workspace/my-new-project"
});

// Customize the template
await fs_edit_file({
  path: "/data/workspace/my-new-project/setup.py",
  edits: [{
    old_text: "project_name",
    new_text: "my-new-project"
  }]
});
```

### Backup and Archive
```javascript
// Create timestamped backup
const timestamp = new Date().toISOString().split('T')[0];
await fs_copy_directory({
  source: "/data/projects/active-project",
  destination: `/data/shared/backups/project-${timestamp}`
});
```

### Shared Team Resources
```javascript
// Save shared configuration
await fs_write_file({
  path: "/data/shared/team/config.json",
  content: JSON.stringify({
    team: "engineering",
    settings: { theme: "dark", notifications: true }
  }, null, 2)
});

// Team members can read
const config = await fs_read_file({
  path: "/data/shared/team/config.json"
});
```

## Error Handling

Always handle potential errors:

```javascript
try {
  const result = await fs_write_file({
    path: "/data/restricted/file.txt",
    content: "test"
  });
} catch (error) {
  if (error.message.includes("Access denied")) {
    console.log("This directory is not in ALLOWED_DIRECTORIES");
  }
}
```

## Tips

1. **Use appropriate directories**: 
   - `/data/shared` for team resources
   - `/data/user` for personal files
   - `/data/projects` for project files
   - `/data/workspace` for temporary work

2. **Check permissions**: Always verify allowed directories first

3. **Handle paths carefully**: Use forward slashes, even on Windows

4. **Large files**: Be mindful of file sizes when reading/copying

5. **Backups**: Regularly backup important data using the copy tools

## Troubleshooting

If you get "Access denied" errors:
1. Check `fs_list_allowed_directories()` output
2. Verify the path is within an allowed directory
3. Check CapRover environment variables
4. Ensure volumes are properly mounted

For more help, check the server logs in CapRover.
