#!/usr/bin/env python3
"""
Quick test script for Atlas Toolset MCP features
"""

import asyncio
from datetime import datetime

# Test imports
from src.remote_mcp.features import (
    CalculatorEngine,
    TextAnalyzerEngine,
    TaskManagerEngine,
    TimeEngine
)

async def test_calculator():
    """Test calculator features"""
    print("\n=== Testing Calculator ===")
    calc = CalculatorEngine()
    
    # Basic calculation
    result = calc.calculate(10, 5, "multiply")
    print(f"10 × 5 = {result.data['result']}")
    
    # Advanced expression
    result = calc.calculate_advanced("2 * pi * r", {"r": 5})
    print(f"2πr (r=5) = {result.data['result']:.2f}")
    
    # Statistics
    result = calc.calculate_statistics([1, 2, 3, 4, 5], ["mean", "stdev"])
    print(f"Statistics: {result.data['results']}")
    
    print("✓ Calculator tests passed")

async def test_text_analyzer():
    """Test text analyzer features"""
    print("\n=== Testing Text Analyzer ===")
    analyzer = TextAnalyzerEngine()
    
    # Basic analysis
    text = "This is a test sentence. It has multiple words and punctuation!"
    result = analyzer.text_analyze(text, "basic")
    print(f"Text stats: {result.data['statistics']}")
    
    # Sentiment analysis
    positive_text = "This is amazing! I love it. Great work!"
    result = analyzer.text_analyze(positive_text, "sentiment")
    print(f"Sentiment: {result.data['sentiment']['overall']}")
    
    # Extract emails
    text_with_email = "Contact us at support@example.com for help"
    result = analyzer.text_extract(text_with_email, "emails")
    print(f"Extracted emails: {result.data['results']}")
    
    print("✓ Text Analyzer tests passed")

async def test_task_manager():
    """Test task manager features"""
    print("\n=== Testing Task Manager ===")
    manager = TaskManagerEngine()
    
    # Create task
    result = manager.task_create(
        title="Test Task",
        description="This is a test",
        priority="high",
        category="testing",
        tags=["test", "demo"]
    )
    task_id = result.data['task']['id']
    print(f"Created task: {task_id}")
    
    # List tasks
    result = manager.task_list()
    print(f"Total tasks: {result.data['count']}")
    
    # Complete task
    result = manager.task_complete(task_id, "Test completed")
    print(f"Task completed: {result.data['message']}")
    
    # Get stats
    result = manager.task_stats()
    print(f"Task stats: Completed {result.data['status_breakdown'].get('completed', 0)} tasks")
    
    print("✓ Task Manager tests passed")

async def test_time_engine():
    """Test time engine features"""
    print("\n=== Testing Time Engine ===")
    time = TimeEngine()
    
    # Get current time in Italian format
    result = time.time_now("italian")
    print(f"Current time (Italian): {result.data['datetime']}")
    
    # Parse shortcuts
    shortcuts = ["now", "tomorrow", "tomorrow EoD", "next month EoM"]
    for shortcut in shortcuts:
        result = time.time_parse(shortcut)
        print(f"{shortcut:15} -> {result.data['datetime']}")
    
    # Calculate date difference
    result = time.time_calculate("now", "next month", "days")
    print(f"Days until next month: {result.data['difference']['value']:.0f}")
    
    # Add time
    result = time.time_add("now", 7, "days", "italian")
    print(f"7 days from now: {result.data['result_date']}")
    
    print("✓ Time Engine tests passed")

async def main():
    """Run all tests"""
    print("Atlas Toolset MCP - Feature Tests")
    print("=" * 50)
    
    try:
        await test_calculator()
        await test_text_analyzer()
        await test_task_manager()
        await test_time_engine()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
