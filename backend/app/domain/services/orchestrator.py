"""Execution orchestrator service for AgentBenchX."""

import asyncio
import time
from typing import Dict, Any, Optional, List
from uuid import uuid4

from backend.app.domain.tasks.models import Task
from backend.app.domain.traces.models import (
    Trace,
    create_task_started_event,
    create_agent_started_event,
    create_action_requested_event,
    create_tool_executed_event,
    create_action_completed_event,
    create_agent_completed_event,
    create_task_completed_event,
    create_error_event,
    TraceEventType,
    ExecutionContext,
    ActionExecution
)
from backend.app.domain.tools.models import Action, ActionResult
from agents.base.agent import BaseAgent, AgentResponse
from environment.agentbenchx_env.base import BaseEnvironment


class OrchestratorConfig:
    """Configuration for the orchestrator."""
    def __init__(
        self,
        max_steps: int = 10,
        step_timeout: float = 30.0,
        trace_metadata: Optional[Dict[str, Any]] = None
    ):
        self.max_steps = max_steps
        self.step_timeout = step_timeout
        self.trace_metadata = trace_metadata or {}


class ExecutionResult:
    """Result of executing a task through the orchestrator."""
    def __init__(
        self,
        run_id: str,
        task_id: str,
        agent_id: str,
        environment_id: str,
        status: str,
        trace: Trace,
        start_time: float,
        end_time: Optional[float] = None,
        error: Optional[str] = None
    ):
        self.run_id = run_id
        self.task_id = task_id
        self.agent_id = agent_id
        self.environment_id = environment_id
        self.status = status  # SUCCESS, FAILED, TIMEOUT
        self.trace = trace
        self.start_time = start_time
        self.end_time = end_time
        self.error = error
        self.duration = (end_time - start_time) if end_time else None


class OrchestratorService:
    """Service that orchestrates agent-environment-trace interactions."""

    def __init__(self, config: Optional[OrchestratorConfig] = None):
        self.config = config or OrchestratorConfig()

    async def execute_task(
        self,
        task: Task,
        agent: BaseAgent,
        environment: BaseEnvironment
    ) -> ExecutionResult:
        """
        Execute a task using the given agent and environment.

        Args:
            task: The task to execute
            agent: The agent to use for execution
            environment: The environment to execute in

        Returns:
            ExecutionResult containing the outcome and trace
        """
        run_id = str(uuid4())
        start_time = time.time()

        # Initialize trace
        trace = Trace(
            agent_id=agent.agent_id,
            task_id=task.id,
            environment_id=environment.environment_id,
            status="RUNNING"
        )

        try:
            # Initialize environment
            init_success = await environment.initialize()
            if not init_success:
                raise Exception("Failed to initialize environment")

            # Reset environment to initial state
            await environment.reset()

            # Add task started event
            trace.add_event(
                create_task_started_event(
                    task_id=task.id,
                    task_name=task.name,
                    metadata=self.config.trace_metadata
                )
            )

            # Add agent started event
            trace.add_event(
                create_agent_started_event(
                    agent_id=agent.agent_id,
                    agent_type=agent.__class__.__name__,
                    metadata=self.config.trace_metadata
                )
            )

            # Execute agent loop with execution context
            step_count = 0
            final_output = None
            error_occurred = False
            execution_history = []  # Track action executions for context

            while step_count < self.config.max_steps and not error_occurred:
                step_count += 1

                try:
                    # Create execution context with history
                    available_tools = [tool.model_dump() for tool in environment.tools]
                    context = ExecutionContext(
                        run_id=run_id,
                        task_id=task.id,
                        step=step_count,
                        available_tools=available_tools,
                        history=execution_history.copy(),  # Provide copy of history
                        metadata=self.config.trace_metadata
                    )

                    # Execute agent with timeout
                    agent_response = await asyncio.wait_for(
                        agent.execute(
                            task_instructions=task.instructions,
                            available_tools=available_tools,
                            context=context.model_dump()  # Convert to dict for backward compatibility
                        ),
                        timeout=self.config.step_timeout
                    )

                    # Process any actions requested by the agent
                    if agent_response.actions_requested:
                        for action_request in agent_response.actions_requested:
                            # Create action object
                            action = Action(
                                tool_name=action_request.get("tool_name", "unknown"),
                                arguments=action_request.get("arguments", {}),
                                metadata=action_request.get("metadata", {})
                            )

                            # Add action requested event to trace
                            trace.add_event(
                                create_action_requested_event(
                                    action_id=action.action_id,
                                    tool_name=action.tool_name,
                                    arguments=action.arguments,
                                    metadata=action.metadata
                                )
                            )

                            # Execute action in environment
                            action_result = await asyncio.wait_for(
                                environment.execute_action(
                                    action_name=action.tool_name,
                                    action_args=action.arguments
                                ),
                                timeout=self.config.step_timeout
                            )

                            # Add tool executed event to trace
                            trace.add_event(
                                create_tool_executed_event(
                                    action_id=action.action_id,
                                    tool_name=action.tool_name,
                                    success=action_result.success,
                                    output=action_result.output,
                                    error=action_result.error,
                                    execution_time=action_result.execution_time,
                                    metadata=action_result.metadata
                                )
                            )

                            # Add action completed event to trace
                            trace.add_event(
                                create_action_completed_event(
                                    action_id=action.action_id,
                                    success=action_result.success,
                                    output=action_result.output,
                                    error=action_result.error,
                                    metadata=action_result.metadata
                                )
                            )

                            # Add to execution history for context
                            action_execution = ActionExecution(
                                action_id=action.action_id,
                                tool_name=action.tool_name,
                                arguments=action.arguments,
                                result=action_result.model_dump(),
                                timestamp=time.time()
                            )
                            execution_history.append(action_execution)

                            # If action failed, we might want to stop or handle differently
                            if not action_result.success:
                                # For now, continue but note the failure
                                pass
                    else:
                        # No actions requested, check if agent has final output
                        if agent_response.output:
                            final_output = agent_response.output
                            break  # Agent is done

                    # If agent didn't request actions and didn't provide output,
                    # we might want to continue or break based on implementation
                    if not agent_response.actions_requested and not agent_response.output:
                        # Agent might be done or waiting - for now, break after one step
                        break

                except asyncio.TimeoutError:
                    error_occurred = True
                    trace.add_event(
                        create_error_event(
                            error_message=f"Step {step_count} timed out",
                            error_type="TIMEOUT",
                            metadata={"step": step_count}
                        )
                    )
                    break
                except Exception as e:
                    error_occurred = True
                    trace.add_event(
                        create_error_event(
                            error_message=f"Step {step_count} failed: {str(e)}",
                            error_type="EXECUTION_ERROR",
                            metadata={"step": step_count, "exception": str(e)}
                        )
                    )
                    break

            # Add agent completed event
            trace.add_event(
                create_agent_completed_event(
                    agent_id=agent.agent_id,
                    success=not error_occurred,
                    output=final_output,
                    error=None if not error_occurred else "Agent execution failed",
                    metadata={"steps_taken": step_count}
                )
            )

            # Determine final status
            if error_occurred:
                final_status = "FAILED"
            elif final_output is not None:
                # Agent completed successfully with output
                final_status = "SUCCESS"
            elif step_count >= self.config.max_steps:
                final_status = "TIMEOUT"
            else:
                final_status = "SUCCESS"

            # Add task completed/failed event
            if final_status == "SUCCESS":
                trace.add_event(
                    create_task_completed_event(
                        task_id=task.id,
                        success=True,
                        output=final_output,
                        metadata={"steps_taken": step_count}
                    )
                )
            else:
                trace.add_event(
                    create_error_event(
                        error_message=f"Task failed with status: {final_status}",
                        error_type="TASK_FAILED",
                        metadata={"steps_taken": step_count, "final_status": final_status}
                    )
                )

            # Update trace status
            trace.status = final_status

            end_time = time.time()

            return ExecutionResult(
                run_id=run_id,
                task_id=task.id,
                agent_id=agent.agent_id,
                environment_id=environment.environment_id,
                status=final_status,
                trace=trace,
                start_time=start_time,
                end_time=end_time,
                error=None if not error_occurred else "Execution failed"
            )

        except Exception as e:
            # Handle unexpected errors
            end_time = time.time()

            # Add error event to trace if possible
            try:
                trace.add_event(
                    create_error_event(
                        error_message=f"Orchestrator error: {str(e)}",
                        error_type="ORCHESTRATOR_ERROR",
                        metadata={"exception": str(e)}
                    )
                )
                trace.status = "FAILED"
            except:
                # If we can't even add to trace, create a minimal trace
                trace = Trace(
                    agent_id=agent.agent_id,
                    task_id=task.id,
                    environment_id=environment.environment_id,
                    status="FAILED"
                )
                trace.add_event(
                    create_error_event(
                        error_message=f"Orchestrator error: {str(e)}",
                        error_type="ORCHESTRATOR_ERROR",
                        metadata={"exception": str(e)}
                    )
                )

            return ExecutionResult(
                run_id=run_id,
                task_id=task.id,
                agent_id=agent.agent_id,
                environment_id=environment.environment_id,
                status="FAILED",
                trace=trace,
                start_time=start_time,
                end_time=end_time,
                error=str(e)
            )
        finally:
            # Cleanup environment
            try:
                await environment.cleanup()
            except:
                pass  # Ignore cleanup errors

    async def execute_task_with_trace_collection(
        self,
        task: Task,
        agent: BaseAgent,
        environment: BaseEnvironment
    ) -> Dict[str, Any]:
        """
        Execute a task and return a dictionary representation suitable for API responses.

        Args:
            task: The task to execute
            agent: The agent to use for execution
            environment: The environment to execute in

        Returns:
            Dictionary containing execution results
        """
        result = await self.execute_task(task, agent, environment)

        return {
            "run_id": result.run_id,
            "task_id": result.task_id,
            "agent_id": result.agent_id,
            "environment_id": result.environment_id,
            "status": result.status,
            "duration": result.duration,
            "error": result.error,
            "trace": result.trace.model_dump()
        }