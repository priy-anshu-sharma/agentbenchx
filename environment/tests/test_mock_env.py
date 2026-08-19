"""Tests for the MockEnvironment."""

import asyncio
import pytest
from environment.agentbenchx_env.mock import MockEnvironment, MockEnvironmentConfig
from environment.agentbenchx_env.base import EnvironmentConfig


@pytest.mark.asyncio
async def test_mock_environment_initialization():
    """Test that the mock environment initializes correctly."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0",
        initial_value=5.0
    )
    env = MockEnvironment(config)

    # Initially not initialized
    assert env._is_initialized == False

    # Initialize
    result = await env.initialize()
    assert result == True
    assert env._is_initialized == True
    assert env._value == 5.0

    # Check state
    state = await env.get_state()
    assert state.data["initialized"] == True
    assert state.data["value"] == 5.0


@pytest.mark.asyncio
async def test_mock_environment_reset():
    """Test that the mock environment resets correctly."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0",
        initial_value=10.0
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Change the value
    env._value = 100.0

    # Reset
    state = await env.reset()
    assert env._value == 10.0
    assert state.data["reset"] == True
    assert state.data["value"] == 10.0


@pytest.mark.asyncio
async def test_mock_environment_calculator_add():
    """Test the calculator add operation."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute addition
    result = await env.execute_action("calculator", {
        "operation": "add",
        "a": 15,
        "b": 27
    })

    assert result.success == True
    assert result.output == 42
    assert "operation" in result.metadata
    assert result.metadata["operation"] == "add"

    # Check that environment state was updated
    state = await env.get_state()
    assert state.data["value"] == 42
    assert "last_calculation" in state.data


@pytest.mark.asyncio
async def test_mock_environment_calculator_subtract():
    """Test the calculator subtract operation."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute subtraction
    result = await env.execute_action("calculator", {
        "operation": "subtract",
        "a": 50,
        "b": 30
    })

    assert result.success == True
    assert result.output == 20

    # Check that environment state was updated
    state = await env.get_state()
    assert state.data["value"] == 20


@pytest.mark.asyncio
async def test_mock_environment_calculator_multiply():
    """Test the calculator multiply operation."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute multiplication
    result = await env.execute_action("calculator", {
        "operation": "multiply",
        "a": 6,
        "b": 7
    })

    assert result.success == True
    assert result.output == 42

    # Check that environment state was updated
    state = await env.get_state()
    assert state.data["value"] == 42


@pytest.mark.asyncio
async def test_mock_environment_calculator_divide():
    """Test the calculator divide operation."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute division
    result = await env.execute_action("calculator", {
        "operation": "divide",
        "a": 84,
        "b": 2
    })

    assert result.success == True
    assert result.output == 42.0

    # Check that environment state was updated
    state = await env.get_state()
    assert state.data["value"] == 42.0


@pytest.mark.asyncio
async def test_mock_environment_calculator_divide_by_zero():
    """Test division by zero handling."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute division by zero
    result = await env.execute_action("calculator", {
        "operation": "divide",
        "a": 42,
        "b": 0
    })

    assert result.success == False
    assert result.error == "Division by zero"
    assert result.output is None


@pytest.mark.asyncio
async def test_mock_environment_unknown_tool():
    """Test executing an unknown tool."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute unknown tool
    result = await env.execute_action("unknown_tool", {"arg": "value"})

    assert result.success == False
    assert "Unknown tool: unknown_tool" in result.error
    assert result.output is None


@pytest.mark.asyncio
async def test_mock_environment_missing_args():
    """Test executing a tool with missing arguments."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execute calculator with missing args
    result = await env.execute_action("calculator", {
        "operation": "add"
        # Missing 'a' and 'b'
    })

    assert result.success == False
    assert "Missing required arguments" in result.error
    assert result.output is None


@pytest.mark.asyncio
async def test_mock_environment_failure_simulation():
    """Test that the environment can simulate failure."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0",
        should_fail=True
    )
    env = MockEnvironment(config)

    # Initialization should fail
    result = await env.initialize()
    assert result == False

    # Even getting state should fail (but still return a state)
    state = await env.get_state()
    assert "error" in state.data


@pytest.mark.asyncio
async def test_mock_environment_fail_on_specific_tool():
    """Test that the environment can fail on a specific tool."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0",
        fail_on_tool="calculator"
    )
    env = MockEnvironment(config)

    await env.initialize()

    # Execution should fail
    result = await env.execute_action("calculator", {
        "operation": "add",
        "a": 10,
        "b": 5
    })

    assert result.success == False
    assert "Mock environment failed on calculator action" in result.error
    assert result.output is None


@pytest.mark.asyncio
async def test_mock_environment_tool_registration():
    """Test tool registration functionality."""
    config = MockEnvironmentConfig(
        environment_id="test-env",
        version="1.0.0"
    )
    env = MockEnvironment(config)

    # Initially should have calculator tool
    tools = env.tools
    assert len(tools) == 1
    assert tools[0].name == "calculator"

    # Register another tool
    from environment.agentbenchx_env.base import Tool
    new_tool = Tool(
        name="echo",
        description="Echoes back the input",
        input_schema={
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        }
    )
    env.register_tool(new_tool)

    # Should now have two tools
    tools = env.tools
    assert len(tools) == 2
    tool_names = [t.name for t in tools]
    assert "calculator" in tool_names
    assert "echo" in tool_names

    # Unregister a tool
    result = env.unregister_tool("calculator")
    assert result == True

    # Should now have only one tool
    tools = env.tools
    assert len(tools) == 1
    assert tools[0].name == "echo"

    # Try to unregister non-existent tool
    result = env.unregister_tool("nonexistent")
    assert result == False