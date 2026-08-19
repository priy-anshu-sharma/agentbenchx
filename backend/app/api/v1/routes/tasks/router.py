"""Task management API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.app.domain.tasks.models import Task, TaskCreate, TaskUpdate
from backend.app.domain.services.task_service import TaskService

router = APIRouter()


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_create: TaskCreate,
    task_service: TaskService = Depends()
):
    """Create a new task."""
    return await task_service.create_task(task_create)


@router.get("/", response_model=List[Task])
async def list_tasks(
    task_service: TaskService = Depends(),
    skip: int = 0,
    limit: int = 100
):
    """List tasks."""
    return await task_service.list_tasks(skip=skip, limit=limit)


@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: str,
    task_service: TaskService = Depends()
):
    """Get a task by ID."""
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    task_service: TaskService = Depends()
):
    """Update a task."""
    task = await task_service.update_task(task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    task_service: TaskService = Depends()
):
    """Delete a task."""
    deleted = await task_service.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None