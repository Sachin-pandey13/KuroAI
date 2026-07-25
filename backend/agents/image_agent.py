from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class ImageAgent(BaseAgent):
    """
    Generates manga panel artwork via the Capability Registry.
    Uses character blueprints, prompts, style guides, and ControlNet/IP-Adapter references.
    """

    @property
    def agent_id(self) -> str:
        return "image_agent"

    @property
    def agent_type(self) -> str:
        return "IMAGE"

    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("ImageAgent.execute stub")
