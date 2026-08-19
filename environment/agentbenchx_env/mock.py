"""Mock environment for testing purposes."""

import asyncio
import time
from typing import Dict, Any, Optional
from pydantic import Field
from environment.agentbenchx_env.base import (
    BaseEnvironment,
    EnvironmentConfig,
    State,
    Tool
)
from backend.app.domain.tools.models import ActionResult


class MockEnvironmentConfig(EnvironmentConfig):
    """Configuration for the MockEnvironment."""
    initial_value: float = Field(0.0, description="Initial value for the mock environment")
    response_delay: float = Field(0.01, description="Delay in seconds before responding")
    should_fail: bool = Field(False, description="Whether the environment should simulate failure")
    fail_on_tool: str = Field("", description="Tool name that should cause failure")


class MockEnvironment(BaseEnvironment):
    """A mock environment that provides a calculator tool for testing."""

    def __init__(self, config: MockEnvironmentConfig):
        super().__init__(config)
        self.config: MockEnvironmentConfig = config
        self._value = config.initial_value
        self._start_time: Optional[float] = None

        # Register the calculator tool
        self._register_tools()

    def _register_tools(self) -> None:
        """Register the tools available in this environment."""
        calculator_tool = Tool(
            name="calculator",
            description="Performs basic arithmetic operations (add, subtract, multiply, divide)",
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                        "description": "The arithmetic operation to perform"
                    },
                    "a": {
                        "type": "number",
                        "description": "First operand"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second operand"
                    }
                },
                "required": ["operation", "a", "b"]
            }
        )
        self.register_tool(calculator_tool)

    async def initialize(self) -> bool:
        """Initialize the mock environment."""
        await asyncio.sleep(self.config.response_delay)
        if self.config.should_fail:
            return False
        self._start_time = time.time()
        self._value = self.config.initial_value
        self._state.data = {
            "initialized": True,
            "start_time": self._start_time,
            "value": self._value
        }
        self._is_initialized = True
        return True

    async def reset(self) -> State:
        """Reset the environment to its initial state."""
        await asyncio.sleep(self.config.response_delay)
        if self.config.should_fail:
            # Return state but indicate failure in metadata
            self._state.data = {
                "initialized": True,
                "reset_failed": True,
                "value": self.config.initial_value
            }
            return self._state

        self._value = self.config.initial_value
        self._state.data = {
            "initialized": True,
            "reset": True,
            "value": self._value,
            "reset_time": time.time()
        }
        return self._state

    async def get_state(self) -> State:
        """Get the current state of the environment."""
        await asyncio.sleep(self.config.response_delay)
        if self.config.should_fail:
            # Still return state but with error indication
            error_state = State(data={"error": "Failed to get state"})
            return error_state

        # Update standard fields while preserving existing data
        self._state.data.update({
            "initialized": self._is_initialized,
            "value": self._value,
            "last_query": time.time()
        })
        if self._start_time:
            self._state.data["uptime"] = time.time() - self._start_time
        return self._state

    async def execute_action(
        self,
        action_name: str,
        action_args: Dict[str, Any]
    ) -> ActionResult:
        """Execute an action in the mock environment."""
        await asyncio.sleep(self.config.response_delay)

        # Check if we should simulate failure
        if self.config.should_fail:
            return ActionResult(
                success=False,
                output=None,
                error="Mock environment simulated failure",
                execution_time=self.config.response_delay,
                state_change=None,
                metadata={"failed_action": action_name}
            )

        # Check if we should fail on this specific tool
        if self.config.fail_on_tool == action_name:
            return ActionResult(
                success=False,
                output=None,
                error=f"Mock environment failed on {action_name} action",
                execution_time=self.config.response_delay,
                state_change=None,
                metadata={"failed_action": action_name}
            )

        # Handle the calculator tool
        if action_name == "calculator":
            return await self._execute_calculator(action_args)

        # Unknown tool
        return ActionResult(
            success=False,
            output=None,
            error=f"Unknown tool: {action_name}",
            execution_time=self.config.response_delay,
            state_change=None,
            metadata={"attempted_tool": action_name}
        )

    async def _execute_calculator(self, args: Dict[str, Any]) -> ActionResult:
        """Execute the calculator tool."""
        try:
            operation = args.get("operation")
            a = args.get("a")
            b = args.get("b")

            # Validate inputs
            if operation is None or a is None or b is None:
                return ActionResult(
                    success=False,
                    output=None,
                    error="Missing required arguments: operation, a, b",
                    execution_time=self.config.response_delay,
                    state_change=None,
                    metadata={"provided_args": args}
                )

            # Perform the operation
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return ActionResult(
                        success=False,
                        output=None,
                        error="Division by zero",
                        execution_time=self.config.response_delay,
                        state_change=None,
                        metadata={"args": args}
                    )
                result = a / b
            else:
                return ActionResult(
                    success=False,
                    output=None,
                    error=f"Unknown operation: {operation}",
                    execution_time=self.config.response_delay,
                    state_change=None,
                    metadata={"args": args}
                )

            # Update environment state
            old_value = self._value
            self._value = result
            state_change = {
                "value": {
                    "old": old_value,
                    "new": self._value
                },
                "last_operation": {
                    "operation": operation,
                    "operands": [a, b],
                    "result": result
                }
            }
            self._state.data.update({
                "last_calculation": {
                    "operation": operation,
                    "a": a,
                    "b": b,
                    "result": result,
                    "time": time.time()
                },
                "value": self._value
            })

            return ActionResult(
                success=True,
                output=result,
                error=None,
                execution_time=self.config.response_delay,
                state_change=state_change,
                metadata={
                    "operation": operation,
                    "operands": [a, b],
                    "result": result
                }
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output=None,
                error=f"Calculator error: {str(e)}",
                state_change=None,
                metadata={"args": args, "exception": str(e)}
            )

    async def cleanup(self) -> bool:
        """Clean up the mock environment."""
        await asyncio.sleep(self.config.response_delay)
        if self.config.should_fail:
            return False
        self._is_initialized = False
        self._state.data = {
            "cleaned_up": True,
            "cleanup_time": time.time()
        }
        return True