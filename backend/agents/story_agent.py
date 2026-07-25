from typing import Optional
from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.agents.tool_executor import BaseToolExecutor


class StoryAgent(BaseAgent):
    """
    Drafts story outlines, scene scripts, and dialogue beats formatted for manga.
    Receives AgentContext and an injected BaseToolExecutor.
    """

    @property
    def agent_id(self) -> str:
        return "story_agent"

    @property
    def agent_type(self) -> str:
        return "STORY"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        """
        Execute narrative drafting task:
        1. Extract prompt/goal from AgentContext sections.
        2. Execute GENERATE_TEXT capability via tool_executor.
        3. Produce Artifact(artifact_type=ArtifactType.STORY_OUTLINE).
        4. Attach DecisionTrace with ExecutionProvenance.
        """
        prompt = f"Draft narrative outline for goal {context.goal_id}"
        if context.sections:
            for sec in context.sections:
                if sec.content and isinstance(sec.content, dict):
                    prompt += f" Context: {sec.content.get('prompt', '') or sec.content.get('goal', '')}"

        tool_resp = None
        text_output = f"[StoryAgent] Outline draft for goal {context.goal_id}"
        model_name = "default-text-model"
        provider_name = "default-text-provider"
        capability_used = []

        if tool_executor is not None:
            tool_req = ToolRequest(
                capability_type=CapabilityType.GENERATE_TEXT,
                parameters={"prompt": prompt, "goal_id": context.goal_id},
            )
            tool_resp = await tool_executor.execute(tool_req)
            if tool_resp and tool_resp.success:
                text_output = tool_resp.output_data.get("text", text_output)
                model_name = tool_resp.model_name
                provider_name = tool_resp.provider_name
                capability_used.append(str(CapabilityType.GENERATE_TEXT))

        project_id = "default_project"
        if context.sections and context.sections[0].content and isinstance(context.sections[0].content, dict):
            project_id = context.sections[0].content.get("project_id", project_id)

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.95,
            reasoning_rationale=f"Generated narrative outline using {provider_name}/{model_name}.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=model_name,
                provider_name=provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data={"outline": text_output, "goal_id": context.goal_id},
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.goal_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_story_outline_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=capability_used,
        )
