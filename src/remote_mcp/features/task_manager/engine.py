"""
Enhanced Task Manager Engine with advanced task tracking capabilities
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ...shared.base import BaseFeature, ToolResponse
from ...shared.types import Priority, TaskStatus


class TaskManagerEngine(BaseFeature):
    """Advanced task manager with categories, dependencies, and time tracking"""
    
    def __init__(self):
        super().__init__("task_manager", "2.0.0")
        self.tasks = {}
        self.task_counter = 0
        self.categories = set()
        self.tags = set()
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of task manager tools"""
        return [
            {
                "name": "task_create",
                "description": "Create a new task with advanced options",
                "parameters": {
                    "title": "Task title",
                    "description": "Task description",
                    "priority": f"Priority: {', '.join(Priority.values())}",
                    "category": "Task category",
                    "tags": "List of tags",
                    "due_date": "Due date (ISO format)",
                    "estimated_hours": "Estimated hours to complete"
                }
            },
            {
                "name": "task_list",
                "description": "List tasks with filtering",
                "parameters": {
                    "status": f"Filter by status: {', '.join(TaskStatus.values())}",
                    "priority": "Filter by priority",
                    "category": "Filter by category",
                    "overdue": "Show only overdue tasks"
                }
            },
            {
                "name": "task_update",
                "description": "Update a task",
                "parameters": {
                    "task_id": "Task ID",
                    "updates": "Dictionary of fields to update"
                }
            },
            {
                "name": "task_delete",
                "description": "Delete a task",
                "parameters": {
                    "task_id": "Task ID"
                }
            },
            {
                "name": "task_complete",
                "description": "Mark task as complete",
                "parameters": {
                    "task_id": "Task ID",
                    "completion_notes": "Optional completion notes"
                }
            },
            {
                "name": "task_stats",
                "description": "Get task statistics",
                "parameters": {}
            }
        ]
    
    def task_create(self, 
                   title: str,
                   description: str = "",
                   priority: str = "medium",
                   category: Optional[str] = None,
                   tags: Optional[List[str]] = None,
                   due_date: Optional[str] = None,
                   estimated_hours: Optional[float] = None,
                   dependencies: Optional[List[str]] = None) -> ToolResponse:
        """
        Create a new task with advanced options
        
        Args:
            title: Task title
            description: Task description
            priority: Task priority
            category: Task category
            tags: List of tags
            due_date: Due date in ISO format
            estimated_hours: Estimated hours to complete
            dependencies: List of task IDs this depends on
        """
        try:
            # Validate priority
            try:
                priority_enum = Priority(priority.lower())
            except ValueError:
                return ToolResponse(
                    success=False,
                    error=f"Invalid priority. Must be one of: {', '.join(Priority.values())}"
                )
            
            # Generate task ID
            self.task_counter += 1
            task_id = f"task_{self.task_counter:04d}"
            
            # Create task
            task = {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority_enum.value,
                "status": TaskStatus.PENDING.value,
                "category": category,
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "due_date": due_date,
                "estimated_hours": estimated_hours,
                "actual_hours": None,
                "completed_at": None,
                "completion_notes": None,
                "dependencies": dependencies or [],
                "blocked_by": [],
                "subtasks": []
            }
            
            # Check dependencies
            if dependencies:
                for dep_id in dependencies:
                    if dep_id not in self.tasks:
                        return ToolResponse(
                            success=False,
                            error=f"Dependency {dep_id} does not exist"
                        )
                    # Check if dependency is complete
                    if self.tasks[dep_id]["status"] != TaskStatus.COMPLETED.value:
                        task["blocked_by"].append(dep_id)
                        task["status"] = TaskStatus.BLOCKED.value
            
            # Update categories and tags
            if category:
                self.categories.add(category)
            if tags:
                self.tags.update(tags)
            
            # Store task
            self.tasks[task_id] = task
            
            return ToolResponse(
                success=True,
                data={
                    "task": task,
                    "message": f"Task {task_id} created successfully"
                }
            )
            
        except Exception as e:
            return self.handle_error("task_create", e)
    
    def task_list(self,
                  status: Optional[str] = None,
                  priority: Optional[str] = None,
                  category: Optional[str] = None,
                  tags: Optional[List[str]] = None,
                  overdue: bool = False,
                  limit: int = 50) -> ToolResponse:
        """
        List tasks with advanced filtering
        
        Args:
            status: Filter by status
            priority: Filter by priority
            category: Filter by category
            tags: Filter by tags (any match)
            overdue: Show only overdue tasks
            limit: Maximum number of tasks to return
        """
        try:
            filtered_tasks = []
            now = datetime.now()
            
            for task in self.tasks.values():
                # Status filter
                if status and task["status"] != status:
                    continue
                
                # Priority filter
                if priority and task["priority"] != priority:
                    continue
                
                # Category filter
                if category and task["category"] != category:
                    continue
                
                # Tags filter (any match)
                if tags and not any(tag in task["tags"] for tag in tags):
                    continue
                
                # Overdue filter
                if overdue:
                    if not task["due_date"]:
                        continue
                    due = datetime.fromisoformat(task["due_date"])
                    if due >= now or task["status"] == TaskStatus.COMPLETED.value:
                        continue
                
                filtered_tasks.append(task)
            
            # Sort by priority and due date
            priority_order = {p.value: i for i, p in enumerate(Priority)}
            
            def sort_key(task):
                priority_score = priority_order.get(task["priority"], 999)
                due_score = 0
                if task["due_date"]:
                    due = datetime.fromisoformat(task["due_date"])
                    due_score = (due - now).total_seconds()
                return (priority_score, due_score)
            
            filtered_tasks.sort(key=sort_key)
            
            # Apply limit
            filtered_tasks = filtered_tasks[:limit]
            
            # Calculate summary statistics
            stats = {
                "total_matched": len(filtered_tasks),
                "by_status": {},
                "by_priority": {}
            }
            
            for task in filtered_tasks:
                status_key = task["status"]
                priority_key = task["priority"]
                
                stats["by_status"][status_key] = stats["by_status"].get(status_key, 0) + 1
                stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1
            
            return ToolResponse(
                success=True,
                data={
                    "tasks": filtered_tasks,
                    "count": len(filtered_tasks),
                    "stats": stats,
                    "filters_applied": {
                        "status": status,
                        "priority": priority,
                        "category": category,
                        "tags": tags,
                        "overdue": overdue
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("task_list", e)
    
    def task_update(self, task_id: str, updates: Dict[str, Any]) -> ToolResponse:
        """
        Update a task with validation
        
        Args:
            task_id: Task ID to update
            updates: Dictionary of fields to update
        """
        try:
            if task_id not in self.tasks:
                return ToolResponse(success=False, error=f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            
            # Validate priority if updating
            if "priority" in updates:
                try:
                    Priority(updates["priority"])
                except ValueError:
                    return ToolResponse(
                        success=False,
                        error=f"Invalid priority. Must be one of: {', '.join(Priority.values())}"
                    )
            
            # Validate status if updating
            if "status" in updates:
                try:
                    new_status = TaskStatus(updates["status"])
                    
                    # Check status transitions
                    current_status = TaskStatus(task["status"])
                    if not self._is_valid_transition(current_status, new_status):
                        return ToolResponse(
                            success=False,
                            error=f"Invalid status transition from {current_status.value} to {new_status.value}"
                        )
                    
                    updates["status"] = new_status.value
                except ValueError:
                    return ToolResponse(
                        success=False,
                        error=f"Invalid status. Must be one of: {', '.join(TaskStatus.values())}"
                    )
            
            # Update fields
            for key, value in updates.items():
                if key in task:
                    task[key] = value
            
            # Update metadata
            task["updated_at"] = datetime.now().isoformat()
            
            # Update categories and tags if changed
            if "category" in updates and updates["category"]:
                self.categories.add(updates["category"])
            if "tags" in updates:
                self.tags.update(updates["tags"])
            
            return ToolResponse(
                success=True,
                data={
                    "task": task,
                    "message": f"Task {task_id} updated successfully",
                    "updated_fields": list(updates.keys())
                }
            )
            
        except Exception as e:
            return self.handle_error("task_update", e)
    
    def task_delete(self, task_id: str) -> ToolResponse:
        """
        Delete a task
        
        Args:
            task_id: Task ID to delete
        """
        try:
            if task_id not in self.tasks:
                return ToolResponse(success=False, error=f"Task {task_id} not found")
            
            # Check if other tasks depend on this one
            dependent_tasks = []
            for other_task in self.tasks.values():
                if task_id in other_task.get("dependencies", []):
                    dependent_tasks.append(other_task["id"])
            
            if dependent_tasks:
                return ToolResponse(
                    success=False,
                    error=f"Cannot delete task {task_id}. Other tasks depend on it: {', '.join(dependent_tasks)}"
                )
            
            # Delete the task
            deleted_task = self.tasks.pop(task_id)
            
            return ToolResponse(
                success=True,
                data={
                    "deleted_task": deleted_task,
                    "message": f"Task {task_id} deleted successfully"
                }
            )
            
        except Exception as e:
            return self.handle_error("task_delete", e)
    
    def task_complete(self, task_id: str, completion_notes: Optional[str] = None,
                     actual_hours: Optional[float] = None) -> ToolResponse:
        """
        Mark a task as complete
        
        Args:
            task_id: Task ID to complete
            completion_notes: Optional notes about completion
            actual_hours: Actual hours taken to complete
        """
        try:
            if task_id not in self.tasks:
                return ToolResponse(success=False, error=f"Task {task_id} not found")
            
            task = self.tasks[task_id]
            
            # Check if task can be completed
            if task["blocked_by"]:
                return ToolResponse(
                    success=False,
                    error=f"Task {task_id} is blocked by: {', '.join(task['blocked_by'])}"
                )
            
            # Mark as complete
            task["status"] = TaskStatus.COMPLETED.value
            task["completed_at"] = datetime.now().isoformat()
            task["completion_notes"] = completion_notes
            task["actual_hours"] = actual_hours
            task["updated_at"] = datetime.now().isoformat()
            
            # Unblock dependent tasks
            unblocked_tasks = []
            for other_task in self.tasks.values():
                if task_id in other_task.get("blocked_by", []):
                    other_task["blocked_by"].remove(task_id)
                    if not other_task["blocked_by"] and other_task["status"] == TaskStatus.BLOCKED.value:
                        other_task["status"] = TaskStatus.PENDING.value
                        unblocked_tasks.append(other_task["id"])
            
            response_data = {
                "task": task,
                "message": f"Task {task_id} completed successfully"
            }
            
            if unblocked_tasks:
                response_data["unblocked_tasks"] = unblocked_tasks
            
            # Calculate efficiency if estimated hours were provided
            if task["estimated_hours"] and actual_hours:
                efficiency = (task["estimated_hours"] / actual_hours) * 100
                response_data["efficiency_percentage"] = round(efficiency, 1)
            
            return ToolResponse(success=True, data=response_data)
            
        except Exception as e:
            return self.handle_error("task_complete", e)
    
    def task_stats(self) -> ToolResponse:
        """Get comprehensive task statistics"""
        try:
            total_tasks = len(self.tasks)
            
            if total_tasks == 0:
                return ToolResponse(
                    success=True,
                    data={"message": "No tasks in the system"}
                )
            
            # Count by status
            status_counts = {status.value: 0 for status in TaskStatus}
            for task in self.tasks.values():
                status_counts[task["status"]] += 1
            
            # Count by priority
            priority_counts = {priority.value: 0 for priority in Priority}
            for task in self.tasks.values():
                priority_counts[task["priority"]] += 1
            
            # Category statistics
            category_counts = {}
            for task in self.tasks.values():
                if task["category"]:
                    category_counts[task["category"]] = category_counts.get(task["category"], 0) + 1
            
            # Tag statistics
            tag_counts = {}
            for task in self.tasks.values():
                for tag in task["tags"]:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Time statistics
            completed_tasks = [t for t in self.tasks.values() if t["status"] == TaskStatus.COMPLETED.value]
            overdue_tasks = []
            upcoming_tasks = []
            now = datetime.now()
            
            for task in self.tasks.values():
                if task["due_date"] and task["status"] != TaskStatus.COMPLETED.value:
                    due = datetime.fromisoformat(task["due_date"])
                    if due < now:
                        overdue_tasks.append(task["id"])
                    elif (due - now).days <= 7:
                        upcoming_tasks.append(task["id"])
            
            # Efficiency statistics
            efficiency_data = []
            for task in completed_tasks:
                if task["estimated_hours"] and task["actual_hours"]:
                    efficiency_data.append({
                        "task_id": task["id"],
                        "estimated": task["estimated_hours"],
                        "actual": task["actual_hours"],
                        "efficiency": (task["estimated_hours"] / task["actual_hours"]) * 100
                    })
            
            avg_efficiency = sum(e["efficiency"] for e in efficiency_data) / len(efficiency_data) if efficiency_data else None
            
            return ToolResponse(
                success=True,
                data={
                    "total_tasks": total_tasks,
                    "status_breakdown": status_counts,
                    "priority_breakdown": priority_counts,
                    "category_breakdown": category_counts,
                    "top_tags": dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                    "time_sensitive": {
                        "overdue": len(overdue_tasks),
                        "overdue_tasks": overdue_tasks[:10],
                        "upcoming_week": len(upcoming_tasks),
                        "upcoming_tasks": upcoming_tasks[:10]
                    },
                    "productivity": {
                        "completed_count": len(completed_tasks),
                        "completion_rate": round(len(completed_tasks) / total_tasks * 100, 1),
                        "average_efficiency": round(avg_efficiency, 1) if avg_efficiency else None,
                        "tasks_with_time_tracking": len(efficiency_data)
                    },
                    "system_info": {
                        "total_categories": len(self.categories),
                        "total_tags": len(self.tags)
                    }
                }
            )
            
        except Exception as e:
            return self.handle_error("task_stats", e)
    
    def _is_valid_transition(self, from_status: TaskStatus, to_status: TaskStatus) -> bool:
        """Check if a status transition is valid"""
        valid_transitions = {
            TaskStatus.PENDING: [TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
            TaskStatus.IN_PROGRESS: [TaskStatus.PENDING, TaskStatus.BLOCKED, TaskStatus.REVIEW, TaskStatus.COMPLETED, TaskStatus.CANCELLED],
            TaskStatus.BLOCKED: [TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
            TaskStatus.REVIEW: [TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.CANCELLED],
            TaskStatus.COMPLETED: [TaskStatus.ARCHIVED],
            TaskStatus.CANCELLED: [TaskStatus.ARCHIVED],
            TaskStatus.ARCHIVED: []
        }
        
        return to_status in valid_transitions.get(from_status, []) or to_status == from_status
