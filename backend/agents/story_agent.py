from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult


class StoryAgent(BaseAgent):
    """
    Drafts plot arcs, scene beats, and dialogue formatted for manga panels.
    """

    @property
    def agent_id(self) -> str:
        return "story_agent"

    @property
    def agent_type(self) -> str:
        return "STORY"

    async def execute(self, context: AgentContext) -> AgentResult:
        raise NotImplementedError("StoryAgent.execute stub")
