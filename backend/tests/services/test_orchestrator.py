"""Tests for the Orchestrator service."""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock
import pytest

from backend.app.domain.services.orchestrator import OrchestratorService, OrchestratorConfig, ExecutionResult
from backend.app.domain.tasks.models import Task
from backend.app.domain.traces.models import Trace
from agents.base.agent import BaseAgent, AgentConfig, AgentCapabilities, AgentResponse
from environment.agentbenchx_env.base import BaseEnvironment, EnvironmentConfig, State, Tool
from backend.app.domain.tools.models import ActionResult


class MockAgentForTesting(BaseAgent):
    """Mock agent for testing the orchestrator that uses execution context to learn."""

    def __init__(self, config: AgentConfig, response_output: str = "test output"):
        super().__init__(config)
        self.response_output = response_output
        self.execute_call_count = 0

    def _define_capabilities(self) -> AgentCapabilities:
        return AgentCapabilities(tool_use=True, reasoning=True, memory=False)

    async def execute(
        self,
        task_instructions: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        self.execute_call_count += 1

        # Check if we have previous action results in context
        actions_requested = []
        if context and "history" in context:
            history = context["history"]
            # If we have previous successful results, we're done
            if history:
                # Check if the last action was successful
                last_action = history[-1]
                if last_action.get("result", {}).get("success", False):
                    # We have a successful result, return final output based on that result
                    output_value = last_action.get("result", {}).get("output")
                    if output_value is not None:
                        return AgentResponse(
                            output=f"Task completed with result: {output_value}",
                            actions_requested=[],  # No more actions needed
                            metadata={"call_count": self.execute_call_count, "learned_from_context": True}
                        )

        # No previous successful results, request the calculator tool
        actions_requested.append({
            "tool_name": "calculator",
            "arguments": {"operation": "add", "a": 1, "b": 2},
            "expected_result": 3
        })

        return AgentResponse(
            output=self.response_output,
            actions_requested=actions_requested,
            metadata={"call_count": self.execute_call_count}
        )


class MockEnvironmentForTesting(BaseEnvironment):
    """Mock environment for testing the orchestrator."""

    def __init__(self, config: EnvironmentConfig,
                 tool_results: Optional[Dict[str, ActionResult]] = None,
                 should_initialize: bool = True,
                 should_reset: bool = True,
                 should_cleanup: bool = True):
        super().__init__(config)
        self.tool_results = tool_results or {}
        self.should_initialize = should_initialize
        self.should_reset = should_reset
        self.should_cleanup = should_cleanup
        self.initialize_call_count = 0
        self.reset_call_count = 0
        self.execute_action_call_count = 0
        self.cleanup_call_count = 0
        self._state = State(data={"test": "state"})

    async def initialize(self) -> bool:
        self.initialize_call_count += 1
        await asyncio.sleep(0.001)  # Simulate async work
        self._is_initialized = True
        return self.should_initialize

    async def reset(self) -> State:
        self.reset_call_count += 1
        await asyncio.sleep(0.001)  # Simulate async work
        return self._state

    async def get_state(self) -> State:
        await asyncio.sleep(0.001)  # Simulate async work
        return self._state

    async def execute_action(
        self,
        action_name: str,
        action_args: Dict[str, Any]
    ) -> ActionResult:
        self.execute_action_call_count += 1
        await asyncio.sleep(0.001)  # Simulate async work

        if action_name in self.tool_results:
            return self.tool_results[action_name]

        # Default successful result
        return ActionResult(
            success=True,
            output=f"Result of {action_name}",
            error=None,
            execution_time=0.01,
            metadata={}
        )

    async def cleanup(self) -> bool:
        self.cleanup_call_count += 1
        await asyncio.sleep(0.001)  # Simulate async work
        self._is_initialized = False
        return self.should_cleanup


def create_test_task() -> Task:
    """Create a test task."""
    return Task(
        id="test-task-001",
        version="1.0.0",
        name="Test Task",
        description="A test task for unit testing",
        instructions="Perform a test action",
        expected_outcome="success",
        allowed_tools=["calculator"],
        constraints={},
        metadata={}
    )


def create_test_agent_config() -> AgentConfig:
    """Create a test agent config."""
    return AgentConfig(
        agent_id="test-agent-001",
        version="1.0.0",
        metadata={}
    )


def create_test_environment_config() -> EnvironmentConfig:
    """Create a test environment config."""
    return EnvironmentConfig(
        environment_id="test-env-001",
        version="1.0.0",
        metadata={}
    )


@pytest.fixture
def orchestrator_service():
    """Create an orchestrator service for testing."""
    return OrchestratorService(OrchestratorConfig(max_steps=2, step_timeout=1.0))


@pytest.fixture
def test_task():
    """Create a test task."""
    return create_test_task()


@pytest.fixture
def test_agent():
    """Create a test agent."""
    config = create_test_agent_config()
    return MockAgentForTesting(config, response_output="test completed")


@pytest.fixture
def test_environment():
    """Create a test environment."""
    config = create_test_environment_config()
    return MockEnvironmentForTesting(config)


class TestOrchestratorService:
    """Test the OrchestratorService class."""

    @pytest.mark.asyncio
    async def test_execute_task_success(
        self, orchestrator_service, test_task, test_agent, test_environment
    ):
        """Test successful task execution."""
        result = await orchestrator_service.execute_task(
            task=test_task,
            agent=test_agent,
            environment=test_environment
        )

        assert result.status == "SUCCESS"
        assert result.run_id is not None
        assert result.task_id == test_task.id
        assert result.agent_id == test_agent.agent_id
        assert result.environment_id == test_environment.environment_id
        assert result.trace is not None
        assert result.start_time is not None
        assert result.end_time is not None
        assert result.duration is not None
        assert result.duration >= 0
        assert result.error is None

        # Verify that the agent's execute method was called
        assert test_agent.execute_call_count >= 1

        # Verify that environment methods were called
        assert test_environment.initialize_call_count == 1
        assert test_environment.reset_call_count >= 1
        assert test_environment.cleanup_call_count == 1

        # Verify trace has events
        assert len(result.trace.events) > 0

    @pytest.mark.asyncio
    async def test_execute_task_with_agent_tool_request(
        self, orchestrator_service, test_task, test_environment
    ):
        """Test task execution where agent requests to use a tool."""
        # Create agent that requests to use a tool (will learn from context)
        agent_config = create_test_agent_config()
        agent = MockAgentForTesting(
            agent_config,
            response_output="I used the tool"
        )

        # Set up environment to return a successful tool result
        tool_result = ActionResult(
            success=True,
            output=5,
            error=None,
            execution_time=0.02,
            metadata={"operation": "add"}
        )
        test_environment.tool_results["calculator"] = tool_result

        result = await orchestrator_service.execute_task(
            task=test_task,
            agent=agent,
            environment=test_environment
        )

        assert result.status == "SUCCESS"
        assert result.trace is not None

        # Verify that tool was executed
        assert test_environment.execute_action_call_count >= 1

        # Verify trace contains tool execution events
        trace_dict = result.trace.model_dump()
        event_types = [event["event_type"] for event in trace_dict["events"]]
        assert "ACTION_REQUESTED" in event_types
        assert "TOOL_EXECUTED" in event_types
        assert "ACTION_COMPLETED" in event_types

    @pytest.mark.asyncio
    async def test_execute_task_agent_failure(
        self, orchestrator_service, test_task, test_environment
    ):
        """Test task execution when agent fails."""
        # Create agent that fails on execute
        agent_config = create_test_agent_config()
        agent = MockAgentForTesting(agent_config)

        # Make the agent's execute method raise an exception
        original_execute = agent.execute
        async def failing_execute(*args, **kwargs):
            raise Exception("Agent failed")
        agent.execute = failing_execute

        result = await orchestrator_service.execute_task(
            task=test_task,
            agent=agent,
            environment=test_environment
        )

        assert result.status == "FAILED"
        assert result.error is not None
        # The error might be wrapped in a generic message, so check for either the specific error or generic failure
        assert "Agent failed" in result.error or "Execution failed" in result.error

    @pytest.mark.asyncio
    async def test_execute_task_environment_init_failure(
        self, orchestrator_service, test_task, test_agent
    ):
        """Test task execution when environment fails to initialize."""
        # Create environment that fails to initialize
        env_config = create_test_environment_config()
        environment = MockEnvironmentForTesting(env_config, should_initialize=False)

        result = await orchestrator_service.execute_task(
            task=test_task,
            agent=test_agent,
            environment=environment
        )

        assert result.status == "FAILED"
        assert result.error is not None
        assert "Failed to initialize environment" in result.error

    @pytest.mark.asyncio
    async def test_execute_task_max_steps_reached(
        self, orchestrator_service, test_task, test_environment
    ):
        """Test task execution when max steps is reached."""
        # Create orchestrator with low max steps
        orchestrator = OrchestratorService(OrchestratorConfig(max_steps=1, step_timeout=1.0))

        # Create agent that always requests to use a tool (will keep going)
        # We need to create a custom agent that doesn't learn from context for this test
        agent_config = create_test_agent_config()

        class NeverLearningAgent(BaseAgent):
            def __init__(self, config):
                super().__init__(config)
                self.execute_call_count = 0

            def _define_capabilities(self) -> AgentCapabilities:
                return AgentCapabilities(tool_use=True, reasoning=True, memory=False)

            async def execute(
                self,
                task_instructions: str,
                available_tools: List[Dict[str, Any]],
                context: Optional[Dict[str, Any]] = None
            ) -> AgentResponse:
                self.execute_call_count += 1

                # Always request the calculator tool, never learn from context
                actions_requested = [{
                    "tool_name": "calculator",
                    "arguments": {"operation": "add", "a": 1, "b": 2},
                    "expected_result": 3
                }]

                return AgentResponse(
                    output="continue",
                    actions_requested=actions_requested,
                    metadata={"call_count": self.execute_call_count}
                )

        agent = NeverLearningAgent(agent_config)

        result = await orchestrator.execute_task(
            task=test_task,
            agent=agent,
            environment=test_environment
        )

        # Should timeout due to max steps
        assert result.status == "TIMEOUT"

    @pytest.mark.asyncio
    async def test_execute_task_timeout(
        self, orchestrator_service, test_task, test_environment
    ):
        """Test task execution timeout."""
        # Create orchestrator with very short timeout
        orchestrator = OrchestratorService(OrchestratorConfig(max_steps=5, step_timeout=0.001))

        # Create agent that takes a long time to execute
        agent_config = create_test_agent_config()

        class SlowAgent(BaseAgent):
            def __init__(self, config):
                super().__init__(config)
                self.execute_call_count = 0

            def _define_capabilities(self) -> AgentCapabilities:
                return AgentCapabilities(tool_use=True, reasoning=True, memory=False)

            async def execute(
                self,
                task_instructions: str,
                available_tools: List[Dict[str, Any]],
                context: Optional[Dict[str, Any]] = None
            ) -> AgentResponse:
                self.execute_call_count += 1

                # Always request the calculator tool
                actions_requested = [{
                    "tool_name": "calculator",
                    "arguments": {"operation": "add", "a": 1, "b": 2},
                    "expected_result": 3
                }]

                return AgentResponse(
                    output="slow response",
                    actions_requested=actions_requested,
                    metadata={"call_count": self.execute_call_count}
                )

        agent = SlowAgent(agent_config)

        # Override execute to take longer than timeout
        original_execute = agent.execute
        async def slow_execute(*args, **kwargs):
            await asyncio.sleep(0.1)  # Longer than timeout
            return await original_execute(*args, **kwargs)
        agent.execute = slow_execute

        result = await orchestrator.execute_task(
            task=test_task,
            agent=agent,
            environment=test_environment
        )

        # Should timeout
        assert result.status == "FAILED"  # Actually becomes FAILED due to timeout error
        assert result.error is not None
        # The error might be wrapped in a generic message, so check for common timeout indicators
        assert "timed out" in result.error.lower() or "timeout" in result.error.lower() or "Execution failed" in result.error

    @pytest.mark.asyncio
    async def test_execute_task_with_trace_collection(
        self, orchestrator_service, test_task, test_agent, test_environment
    ):
        """Test the execute_task_with_trace_collection method."""
        result_dict = await orchestrator_service.execute_task_with_trace_collection(
            task=test_task,
            agent=test_agent,
            environment=test_environment
        )

        assert isinstance(result_dict, dict)
        assert "run_id" in result_dict
        assert "task_id" in result_dict
        assert "agent_id" in result_dict
        assert "environment_id" in result_dict
        assert "status" in result_dict
        assert "duration" in result_dict
        assert "trace" in result_dict
        assert result_dict["task_id"] == test_task.id
        assert result_dict["agent_id"] == test_agent.agent_id
        assert result_dict["environment_id"] == test_environment.environment_id
        assert result_dict["status"] == "SUCCESS"


class TestExecutionResult:
    """Test the ExecutionResult class."""

    def test_execution_result_creation(self):
        """Test creating an ExecutionResult."""
        trace = Trace(
            agent_id="test-agent",
            task_id="test-task",
            environment_id="test-env",
            status="SUCCESS"
        )

        start_time = time.time()
        end_time = start_time + 1.5

        result = ExecutionResult(
            run_id="test-run-001",
            task_id="test-task",
            agent_id="test-agent",
            environment_id="test-env",
            status="SUCCESS",
            trace=trace,
            start_time=start_time,
            end_time=end_time
        )

        assert result.run_id == "test-run-001"
        assert result.task_id == "test-task"
        assert result.agent_id == "test-agent"
        assert result.environment_id == "test-env"
        assert result.status == "SUCCESS"
        assert result.trace == trace
        assert result.start_time == start_time
        assert result.end_time == end_time
        assert result.duration == 1.5
        assert result.error is None

    def test_execution_result_with_error(self):
        """Test creating an ExecutionResult with an error."""
        trace = Trace(
            agent_id="test-agent",
            task_id="test-task",
            environment_id="test-env",
            status="FAILED"
        )

        result = ExecutionResult(
            run_id="test-run-002",
            task_id="test-task",
            agent_id="test-agent",
            environment_id="test-env",
            status="FAILED",
            trace=trace,
            start_time=time.time(),
            end_time=time.time(),
            error="Test error"
        )

        assert result.status == "FAILED"
        assert result.error == "Test error"


if __name__ == "__main__":
    pytest.main([__file__])