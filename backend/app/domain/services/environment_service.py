"""Environment service for managing environments."""

from typing import List, Optional, Dict, Any

from environment.agentbenchx_env.base import BaseEnvironment


class EnvironmentService:
    """Service for managing environments."""

    def __init__(self):
        # In a real implementation, this would connect to a database or environment registry
        # For now, we'll use an in-memory store
        self._environments: Dict[str, BaseEnvironment] = {}

    async def register_environment(self, environment: BaseEnvironment) -> BaseEnvironment:
        """Register an environment."""
        self._environments[environment.environment_id] = environment
        return environment

    async def get_environment(self, environment_id: str) -> Optional[BaseEnvironment]:
        """Get an environment by ID."""
        return self._environments.get(environment_id)

    async def list_environments(self, skip: int = 0, limit: int = 100) -> List[BaseEnvironment]:
        """List environments."""
        environments = list(self._environments.values())
        return environments[skip:skip + limit]

    async def unregister_environment(self, environment_id: str) -> bool:
        """Unregister an environment."""
        if environment_id in self._environments:
            del self._environments[environment_id]
            return True
        return False