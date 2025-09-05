"""
Example: Database integration for Atlas Toolset MCP

This example shows how to create a database feature following the architecture pattern.
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager
from src.remote_mcp.shared.base import BaseFeature, ToolResponse


class DatabaseEngine(BaseFeature):
    """Example database feature with SQLite"""
    
    def __init__(self, db_path: str = "atlas_toolset.db"):
        super().__init__("database", "1.0.0")
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with example tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    category TEXT,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster searches
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_category 
                ON notes(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_notes_created 
                ON notes(created_at)
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(
            self.db_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of database tools"""
        return [
            {
                "name": "db_create_note",
                "description": "Create a new note in database",
                "parameters": {
                    "title": "Note title",
                    "content": "Note content",
                    "category": "Note category",
                    "tags": "List of tags"
                }
            },
            {
                "name": "db_search_notes",
                "description": "Search notes in database",
                "parameters": {
                    "query": "Search query",
                    "category": "Filter by category",
                    "limit": "Maximum results"
                }
            },
            {
                "name": "db_update_note",
                "description": "Update an existing note",
                "parameters": {
                    "note_id": "Note ID",
                    "updates": "Dictionary of fields to update"
                }
            },
            {
                "name": "db_delete_note",
                "description": "Delete a note",
                "parameters": {
                    "note_id": "Note ID"
                }
            },
            {
                "name": "db_execute_query",
                "description": "Execute custom SQL query (read-only)",
                "parameters": {
                    "query": "SQL query",
                    "params": "Query parameters"
                }
            }
        ]
    
    def db_create_note(self, 
                      title: str,
                      content: str = "",
                      category: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> ToolResponse:
        """
        Create a new note in the database
        
        Args:
            title: Note title
            content: Note content
            category: Note category
            tags: List of tags
        """
        try:
            # Validate required fields
            error = self.validate_input({"title": title}, ["title"])
            if error:
                return ToolResponse(success=False, error=error)
            
            # Convert tags to JSON string
            tags_json = json.dumps(tags) if tags else None
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO notes (title, content, category, tags)
                    VALUES (?, ?, ?, ?)
                """, (title, content, category, tags_json))
                
                note_id = cursor.lastrowid
                conn.commit()
                
                # Fetch the created note
                cursor.execute("""
                    SELECT * FROM notes WHERE id = ?
                """, (note_id,))
                
                note = self._row_to_dict(cursor.fetchone())
                
                return ToolResponse(
                    success=True,
                    data={
                        "note": note,
                        "message": f"Note {note_id} created successfully"
                    }
                )
                
        except Exception as e:
            return self.handle_error("db_create_note", e)
    
    def db_search_notes(self,
                       query: Optional[str] = None,
                       category: Optional[str] = None,
                       limit: int = 50) -> ToolResponse:
        """
        Search notes in the database
        
        Args:
            query: Search query (searches title and content)
            category: Filter by category
            limit: Maximum number of results
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Build query dynamically
                sql = "SELECT * FROM notes WHERE 1=1"
                params = []
                
                if query:
                    sql += " AND (title LIKE ? OR content LIKE ?)"
                    search_pattern = f"%{query}%"
                    params.extend([search_pattern, search_pattern])
                
                if category:
                    sql += " AND category = ?"
                    params.append(category)
                
                sql += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                notes = [self._row_to_dict(row) for row in rows]
                
                return ToolResponse(
                    success=True,
                    data={
                        "notes": notes,
                        "count": len(notes),
                        "query": query,
                        "category": category
                    }
                )
                
        except Exception as e:
            return self.handle_error("db_search_notes", e)
    
    def db_update_note(self, 
                      note_id: int,
                      updates: Dict[str, Any]) -> ToolResponse:
        """
        Update an existing note
        
        Args:
            note_id: Note ID to update
            updates: Dictionary of fields to update
        """
        try:
            if not updates:
                return ToolResponse(
                    success=False,
                    error="No updates provided"
                )
            
            # Allowed fields for update
            allowed_fields = ["title", "content", "category", "tags"]
            
            # Filter updates to allowed fields
            filtered_updates = {
                k: v for k, v in updates.items() 
                if k in allowed_fields
            }
            
            if not filtered_updates:
                return ToolResponse(
                    success=False,
                    error="No valid fields to update"
                )
            
            # Handle tags serialization
            if "tags" in filtered_updates:
                filtered_updates["tags"] = json.dumps(filtered_updates["tags"])
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if note exists
                cursor.execute("SELECT id FROM notes WHERE id = ?", (note_id,))
                if not cursor.fetchone():
                    return ToolResponse(
                        success=False,
                        error=f"Note {note_id} not found"
                    )
                
                # Build update query
                set_clause = ", ".join([f"{k} = ?" for k in filtered_updates.keys()])
                sql = f"""
                    UPDATE notes 
                    SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """
                
                params = list(filtered_updates.values()) + [note_id]
                cursor.execute(sql, params)
                conn.commit()
                
                # Fetch updated note
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                note = self._row_to_dict(cursor.fetchone())
                
                return ToolResponse(
                    success=True,
                    data={
                        "note": note,
                        "updated_fields": list(filtered_updates.keys()),
                        "message": f"Note {note_id} updated successfully"
                    }
                )
                
        except Exception as e:
            return self.handle_error("db_update_note", e)
    
    def db_delete_note(self, note_id: int) -> ToolResponse:
        """
        Delete a note from the database
        
        Args:
            note_id: Note ID to delete
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if note exists
                cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
                note = cursor.fetchone()
                
                if not note:
                    return ToolResponse(
                        success=False,
                        error=f"Note {note_id} not found"
                    )
                
                # Delete the note
                cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()
                
                return ToolResponse(
                    success=True,
                    data={
                        "deleted_note": self._row_to_dict(note),
                        "message": f"Note {note_id} deleted successfully"
                    }
                )
                
        except Exception as e:
            return self.handle_error("db_delete_note", e)
    
    def db_execute_query(self, 
                        query: str,
                        params: Optional[Tuple] = None) -> ToolResponse:
        """
        Execute a custom SQL query (read-only for safety)
        
        Args:
            query: SQL query to execute
            params: Query parameters
        """
        try:
            # Safety check - only allow SELECT queries
            if not query.strip().upper().startswith("SELECT"):
                return ToolResponse(
                    success=False,
                    error="Only SELECT queries are allowed"
                )
            
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Get column names
                columns = [description[0] for description in cursor.description]
                
                # Fetch all results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = [
                    dict(zip(columns, row))
                    for row in rows
                ]
                
                return ToolResponse(
                    success=True,
                    data={
                        "results": results,
                        "count": len(results),
                        "columns": columns
                    }
                )
                
        except Exception as e:
            return self.handle_error("db_execute_query", e)
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert SQLite row to dictionary"""
        if not row:
            return {}
        
        result = dict(row)
        
        # Deserialize JSON fields
        if "tags" in result and result["tags"]:
            try:
                result["tags"] = json.loads(result["tags"])
            except json.JSONDecodeError:
                result["tags"] = []
        
        # Convert timestamps to ISO format
        for field in ["created_at", "updated_at"]:
            if field in result and result[field]:
                if isinstance(result[field], str):
                    result[field] = result[field]
                else:
                    result[field] = result[field].isoformat()
        
        return result


# Database Best Practices:
#
# 1. **Connection Management**: Use context managers for automatic cleanup
# 2. **SQL Injection Prevention**: Always use parameterized queries
# 3. **Indexing**: Create indexes for frequently queried columns
# 4. **Transaction Management**: Use transactions for multiple operations
# 5. **Error Handling**: Gracefully handle database errors
# 6. **Data Validation**: Validate input before database operations
# 7. **Migrations**: Version your database schema
# 8. **Backups**: Implement regular backup strategies
# 9. **Connection Pooling**: For production, use connection pools
# 10. **Read/Write Separation**: Consider read replicas for scaling
#
# For production, consider using:
# - PostgreSQL or MySQL for relational data
# - MongoDB for document storage
# - Redis for caching and sessions
# - SQLAlchemy as an ORM for complex applications
