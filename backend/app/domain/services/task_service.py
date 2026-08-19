"""Task service for managing tasks."""

from typing import List, Optional, Dict, Any
from uuid import uuid4

from backend.app.domain.tasks.models import Task, TaskCreate, TaskUpdate


class TaskService:
    """Service for managing tasks."""

    def __init__(self):
        # In a real implementation, this would connect to a database
        # For now, we'll use an in-memory store
        self._tasks: Dict[str, Task] = {}

    async def create_task(self, task_create: TaskCreate) -> Task:
        """Create a new task."""
        task = Task(**task_create.model_dump())
        self._tasks[task.id] = task
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    async def list_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        """List tasks."""
        tasks = list(self._tasks.values())
        return tasks[skip:skip + limit]

    async def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update a task."""
        if task_id not in self._tasks:
            return None

        task = self._tasks[task_id]
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        self._tasks[task_id] = task
        return task

    async def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False