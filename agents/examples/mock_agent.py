"""Mock agent for testing purposes."""

import asyncio
import json
from typing import Dict, Any, List, Optional
from agents.base.agent import BaseAgent, AgentConfig, AgentCapabilities, AgentResponse


class MockAgentConfig(AgentConfig):
    """Configuration for the MockAgent."""
    response_delay: float = Field(0.01, description="Delay in seconds before responding")
    should_fail: bool = Field(False, description="Whether the agent should simulate failure")
    fail_on_action: str = Field("", description="Action name that should cause failure")


class MockAgent(BaseAgent):
    """A mock agent that can perform simple calculations and follow basic instructions."""

    def __init__(self, config: MockAgentConfig):
        super().__init__(config)
        self.config: MockAgentConfig = config

    def _define_capabilities(self) -> AgentCapabilities:
        """Define the capabilities of this mock agent."""
        return AgentCapabilities(
            tool_use=True,
            reasoning=True,
            memory=False
        )

    async def execute(
        self,
        task_instructions: str,
        available_tools: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Execute the mock agent on a given task.

        For testing, this agent will:
        1. Look for calculation requests in the task
        2. If it sees a tool it can use, request to use it
        3. Return the result
        """
        # Simulate some processing delay
        await asyncio.sleep(self.config.response_delay)

        # Check if we should simulate failure
        if self.config.should_fail:
            return AgentResponse(
                output=None,
                actions_requested=[],
                metadata={"error": "Mock agent simulated failure"}
            )

        # Parse task instructions to see what we need to do
        actions_requested = []
        final_output = None

        # Simple logic: if task contains a calculation request and we have a calculator tool
        if ("calculate" in task_instructions.lower() or "+" in task_instructions or
            "-" in task_instructions or "*" in task_instructions or "/" in task_instructions):

            # Look for a calculator tool
            calculator_tool = None
            for tool in available_tools:
                if tool.get("name") == "calculator":
                    calculator_tool = tool
                    break

            if calculator_tool:
                # Extract numbers from the task (very simple parsing)
                import re
                # Look for patterns like "15 + 27" or similar
                numbers = re.findall(r'\d+\.?\d*', task_instructions)
                if len(numbers) >= 2:
                    try:
                        a = float(numbers[0])
                        b = float(numbers[1])

                        # Determine operation
                        if "+" in task_instructions:
                            result = a + b
                            operation = "add"
                        elif "-" in task_instructions:
                            result = a - b
                            operation = "subtract"
                        elif "*" in task_instructions:
                            result = a * b
                            operation = "multiply"
                        elif "/" in task_instructions:
                            if b != 0:
                                result = a / b
                                operation = "divide"
                            else:
                                result = None
                                operation = "divide"
                        else:
                            # Default to addition
                            result = a + b
                            operation = "add"

                        # Check if we should fail on this specific action
                        if self.config.fail_on_action == operation:
                            return AgentResponse(
                                output=None,
                                actions_requested=[],
                                metadata={"error": f"Mock agent failed on {operation} action"}
                            )

                        # Request to use the calculator tool
                        actions_requested.append({
                            "tool_name": "calculator",
                            "operation": operation,
                            "arguments": {"a": a, "b": b},
                            "expected_result": result
                        })

                        # For now, we'll just return that we want to use the tool
                        # In a real implementation, the environment would execute the tool
                        # and return the result to us
                        final_output = f"I need to use the calculator to {operation} {a} and {b}"

                    except ValueError:
                        pass

        # If we couldn't parse a calculation, give a generic response
        if final_output is None:
            final_output = f"Mock agent received task: {task_instructions[:100]}..."

        return AgentResponse(
            output=final_output,
            actions_requested=actions_requested,
            metadata={
                "agent_type": "MockAgent",
                "processed_instructions": task_instructions
            }
        )