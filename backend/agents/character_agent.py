import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from backend.agents.base_agent import BaseAgent
from backend.agents.output_parser import OutputParser
from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.character import CharacterProfile
from backend.contracts.context import AgentContext, ContextSectionType
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance


class CharacterAgent(BaseAgent):
    """
    Designs new characters or fleshes out existing ones based on story requirements.
    Produces immutable CharacterProfile artifacts.
    """

    @property
    def agent_id(self) -> str:
        return "character_agent"

    @property
    def agent_type(self) -> str:
        return "CHARACTER"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        if tool_executor is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="No tool executor provided",
            )

        project_id = "default_project"
        story_outline = ""
        instructions = ""
        existing_characters = []
        parent_artifact_ids = []

        for sec in context.sections:
            if sec.section_type == ContextSectionType.ARTIFACT and isinstance(sec.content, dict):
                if sec.content.get("artifact_type") == ArtifactType.STORY_OUTLINE.value:
                    project_id = sec.content.get("project_id", project_id)
                    parent_artifact_ids.append(sec.content.get("artifact_id"))
                    story_outline = str(sec.content.get("data", {}))
                elif sec.content.get("artifact_type") == ArtifactType.CHARACTER_PROFILE.value:
                    existing_characters.append(sec.content.get("data", {}))
            elif sec.section_type == ContextSectionType.GOAL:
                if isinstance(sec.content, dict):
                    instructions = sec.content.get("prompt", str(sec.content))
                else:
                    instructions = str(sec.content)

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("character_profile.jinja")
        prompt = template.render(
            story_outline=story_outline,
            instructions=instructions,
            existing_characters=existing_characters,
        )

        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{CharacterProfile.model_json_schema()}"

        tool_req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": prompt, "temperature": 0.7, "max_tokens": 2048},
        )
        tool_resp = await tool_executor.execute(tool_req)

        if not tool_resp or not tool_resp.success:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"Character generation failed: {tool_resp.error_message if tool_resp else 'No response'}",
            )

        text_output = tool_resp.output_data.get("text", "")
        profile = OutputParser.parse_json(text_output, CharacterProfile)

        if profile is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="JSON validation error: failed to parse CharacterProfile from model output.",
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.9,
            reasoning_rationale="Generated CharacterProfile using Pydantic JSON schema.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=profile.model_dump(),
            parent_artifact_id=parent_artifact_ids[0] if parent_artifact_ids else None,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_character_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
