"""
AgentRegistry — Storage and lookup subsystem for registered BaseAgent instances.

Mirrors the architecture established by:
    ArtifactRegistry  → owns artifacts
    TaskRegistry      → owns tasks
    CapabilityRegistry → owns providers
    AgentRegistry     → owns agents

The AgentRuntime resolves agents by agent_type via this registry.
"""

from typing import Dict, List

from backend.agents.base_agent import BaseAgent


class AgentNotFoundError(Exception):
    """Raised when no agent is registered for the requested agent_type."""

    pass


class AgentAlreadyRegisteredError(Exception):
    """Raised when an agent_type is already registered."""

    pass


class AgentRegistry:
    """
    Stores and resolves BaseAgent instances by their agent_type.

    Registration example:
        registry = AgentRegistry()
        registry.register_agent(StoryAgent())

    Resolution example (by AgentRuntime):
        agent = registry.get_agent("STORY")
    """

    def __init__(self) -> None:
        self._agents: Dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent instance.
        Raises AgentAlreadyRegisteredError if agent_type is already registered.
        """
        if agent.agent_type in self._agents:
            raise AgentAlreadyRegisteredError(
                f"Agent type '{agent.agent_type}' is already registered. "
                f"Unregister first or use replace_agent()."
            )
        self._agents[agent.agent_type] = agent

    def replace_agent(self, agent: BaseAgent) -> None:
        """Register or overwrite an existing agent for a given agent_type."""
        self._agents[agent.agent_type] = agent

    def unregister_agent(self, agent_type: str) -> None:
        """Remove an agent from the registry."""
        self._agents.pop(agent_type, None)

    def get_agent(self, agent_type: str) -> BaseAgent:
        """
        Retrieve the agent registered for agent_type.
        Raises AgentNotFoundError if not registered.
        """
        if agent_type not in self._agents:
            raise AgentNotFoundError(
                f"No agent registered for type '{agent_type}'. "
                f"Registered types: {list(self._agents.keys())}"
            )
        return self._agents[agent_type]

    def exists(self, agent_type: str) -> bool:
        """Return True if an agent is registered for agent_type."""
        return agent_type in self._agents

    def list_agents(self) -> List[str]:
        """Return all registered agent_type strings."""
        return list(self._agents.keys())
