"""Task execution API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from backend.app.domain.tasks.models import Task
from backend.app.domain.services.task_service import TaskService
from backend.app.domain.services.orchestrator import OrchestratorService
from backend.app.domain.agents.service import AgentService
from backend.app.domain.environments.service import EnvironmentService

router = APIRouter()


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def run_task(
    task_id: str,
    agent_id: str,
    environment_id: str,
    task_service: TaskService = Depends(),
    agent_service: AgentService = Depends(),
    environment_service: EnvironmentService = Depends(),
    orchestrator_service: OrchestratorService = Depends()
):
    """Run a task with the specified agent and environment."""
    # Get the task
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Get the agent
    agent = await agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Get the environment
    environment = await environment_service.get_environment(environment_id)
    if not environment:
        raise HTTPException(status_code=404, detail="Environment not found")

    # Execute the task
    result = await orchestrator_service.execute_task_with_trace_collection(
        task=task,
        agent=agent,
        environment=environment
    )

    return result