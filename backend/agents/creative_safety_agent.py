from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class CreativeSafetyAgent(BaseAgent):
    """
    Validates content against safety policies.
    Instead of hard rejection, provides:
    - Explainable reason for policy violation
    - 3 policy-compliant alternative suggestions
    - Constructive creative guidance
    """

    @property
    def agent_id(self) -> str:
        return "creative_safety_agent"

    @property
    def agent_type(self) -> str:
        return "CREATIVE_SAFETY"

    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("CreativeSafetyAgent.execute stub")
