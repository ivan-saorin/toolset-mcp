"""
Comprehensive test suite for Remote MCP Server
"""

import pytest
import asyncio
import httpx
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.remote_mcp.server import (
    system_info,
    calculate,
    text_analyze,
    task_create,
    task_list,
    task_update,
    task_delete,
    tasks_db,
    task_counter
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def setup_tasks():
    """Reset task database before each test"""
    global tasks_db, task_counter
    tasks_db.clear()
    task_counter = 0
    yield
    tasks_db.clear()
    task_counter = 0

@pytest.fixture
async def test_client():
    """Create a test client for the server"""
    # This would be used for integration tests
    # You'd start the server and return an httpx client
    pass

# ============================================================================
# SYSTEM TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_system_info():
    """Test system info tool"""
    result = await system_info()
    
    assert "server_name" in result
    assert "version" in result
    assert "timestamp" in result
    assert "transport" in result
    assert "features" in result
    assert result["transport"] == "streamable-http"

# ============================================================================
# CALCULATOR TESTS
# ============================================================================

@pytest.mark.asyncio
class TestCalculator:
    """Test calculator functionality"""
    
    async def test_addition(self):
        result = await calculate(5, 3, "add")
        assert result["result"] == 8
        assert result["operation"] == "add"
    
    async def test_subtraction(self):
        result = await calculate(10, 4, "subtract")
        assert result["result"] == 6
    
    async def test_multiplication(self):
        result = await calculate(7, 6, "multiply")
        assert result["result"] == 42
    
    async def test_division(self):
        result = await calculate(15, 3, "divide")
        assert result["result"] == 5
    
    async def test_division_by_zero(self):
        result = await calculate(10, 0, "divide")
        assert result["result"] == float('inf')
    
    async def test_power(self):
        result = await calculate(2, 8, "power")
        assert result["result"] == 256
    
    async def test_modulo(self):
        result = await calculate(10, 3, "modulo")
        assert result["result"] == 1
    
    async def test_modulo_by_zero(self):
        result = await calculate(10, 0, "modulo")
        assert result["result"] is None
    
    async def test_invalid_operation(self):
        result = await calculate(5, 3, "invalid")
        assert "error" in result
        assert "valid_operations" in result

# ============================================================================
# TEXT ANALYSIS TESTS
# ============================================================================

@pytest.mark.asyncio
class TestTextAnalysis:
    """Test text analysis functionality"""
    
    async def test_basic_analysis(self):
        text = "Hello world. This is a test."
        result = await text_analyze(text)
        
        assert result["character_count"] == len(text)
        assert result["word_count"] == 6
        assert result["sentence_count"] == 2
        assert result["unique_words"] == 6
    
    async def test_empty_text(self):
        result = await text_analyze("")
        
        assert result["character_count"] == 0
        assert result["word_count"] == 0
        assert result["sentence_count"] == 0
        assert result["average_word_length"] == 0
    
    async def test_long_text_preview(self):
        text = "a" * 150
        result = await text_analyze(text)
        
        assert "preview" in result
        assert result["preview"].endswith("...")
        assert len(result["preview"]) == 103  # 100 chars + "..."
    
    async def test_repeated_words(self):
        text = "test test test hello hello world"
        result = await text_analyze(text)
        
        assert result["word_count"] == 6
        assert result["unique_words"] == 3

# ============================================================================
# TASK MANAGEMENT TESTS
# ============================================================================

@pytest.mark.asyncio
class TestTaskManagement:
    """Test task management functionality"""
    
    async def test_create_task(self, setup_tasks):
        result = await task_create(
            title="Test Task",
            description="Test Description",
            priority="high"
        )
        
        assert result["id"] == "task_1"
        assert result["title"] == "Test Task"
        assert result["description"] == "Test Description"
        assert result["priority"] == "high"
        assert result["status"] == "pending"
        assert "created_at" in result
    
    async def test_create_minimal_task(self, setup_tasks):
        result = await task_create(title="Minimal Task")
        
        assert result["title"] == "Minimal Task"
        assert result["description"] == ""
        assert result["priority"] == "medium"
    
    async def test_list_all_tasks(self, setup_tasks):
        # Create multiple tasks
        await task_create("Task 1")
        await task_create("Task 2")
        await task_create("Task 3")
        
        result = await task_list()
        
        assert len(result) == 3
        assert all(isinstance(task, dict) for task in result)
    
    async def test_list_filtered_tasks(self, setup_tasks):
        # Create tasks with different statuses
        task1 = await task_create("Pending Task")
        task2 = await task_create("In Progress Task")
        
        # Update one task status
        await task_update(task2["id"], status="in_progress")
        
        # List only pending tasks
        result = await task_list(status="pending")
        
        assert len(result) == 1
        assert result[0]["title"] == "Pending Task"
    
    async def test_update_task(self, setup_tasks):
        # Create a task
        task = await task_create("Original Task", "Original Description")
        
        # Update the task
        result = await task_update(
            task_id=task["id"],
            title="Updated Task",
            status="completed"
        )
        
        assert result["title"] == "Updated Task"
        assert result["status"] == "completed"
        assert result["description"] == "Original Description"  # Unchanged
        assert result["updated_at"] != task["created_at"]
    
    async def test_update_nonexistent_task(self, setup_tasks):
        result = await task_update("task_999", title="New Title")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    async def test_delete_task(self, setup_tasks):
        # Create a task
        task = await task_create("Task to Delete")
        
        # Delete the task
        result = await task_delete(task["id"])
        
        assert result["success"] is True
        assert task["id"] in result["message"]
        
        # Verify it's deleted
        tasks = await task_list()
        assert len(tasks) == 0
    
    async def test_delete_nonexistent_task(self, setup_tasks):
        result = await task_delete("task_999")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    async def test_task_persistence(self, setup_tasks):
        """Test that tasks persist across operations"""
        # Create multiple tasks
        task1 = await task_create("Task 1")
        task2 = await task_create("Task 2")
        task3 = await task_create("Task 3")
        
        # Update one
        await task_update(task2["id"], status="completed")
        
        # Delete one
        await task_delete(task1["id"])
        
        # List remaining tasks
        result = await task_list()
        
        assert len(result) == 2
        task_ids = [t["id"] for t in result]
        assert task1["id"] not in task_ids
        assert task2["id"] in task_ids
        assert task3["id"] in task_ids

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.asyncio
class TestIntegration:
    """Integration tests for the complete server"""
    
    @pytest.mark.skipif(
        not Path("run_server.py").exists(),
        reason="Server script not found"
    )
    async def test_server_startup(self):
        """Test that the server can start without errors"""
        # This would typically use subprocess to start the server
        # and verify it's responding
        pass
    
    async def test_concurrent_operations(self, setup_tasks):
        """Test concurrent tool operations"""
        tasks = [
            calculate(i, i+1, "add") for i in range(10)
        ]
        tasks.extend([
            task_create(f"Task {i}") for i in range(10)
        ])
        tasks.extend([
            text_analyze(f"Text {i}" * 10) for i in range(10)
        ])
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 30
        assert all(isinstance(r, dict) for r in results)

# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

@pytest.mark.asyncio
class TestPerformance:
    """Performance and stress tests"""
    
    @pytest.mark.slow
    async def test_many_tasks(self, setup_tasks):
        """Test creating many tasks"""
        tasks = []
        for i in range(100):
            task = await task_create(f"Task {i}")
            tasks.append(task)
        
        result = await task_list()
        assert len(result) == 100
    
    @pytest.mark.slow
    async def test_large_text_analysis(self):
        """Test analyzing large text"""
        # Create a large text (1MB)
        text = "Lorem ipsum dolor sit amet. " * 50000
        
        result = await text_analyze(text)
        
        assert result["character_count"] == len(text)
        assert result["word_count"] > 0

# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    async def test_invalid_types(self):
        """Test handling of invalid parameter types"""
        # These should be handled gracefully by FastMCP
        # In practice, FastMCP would validate types before calling
        pass
    
    async def test_unicode_handling(self):
        """Test Unicode text handling"""
        text = "Hello 世界 🌍 مرحبا мир"
        result = await text_analyze(text)
        
        assert result["word_count"] == 5
        assert result["character_count"] == len(text)
    
    async def test_special_characters(self):
        """Test special characters in task titles"""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        task = await task_create(title=special_chars)
        assert task["title"] == special_chars
        
        # Can still retrieve it
        tasks = await task_list()
        assert len(tasks) == 1
        assert tasks[0]["title"] == special_chars

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
