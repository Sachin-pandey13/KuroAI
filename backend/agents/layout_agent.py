import os
from typing import Optional

from jinja2 import Environment, FileSystemLoader

from backend.agents.base_agent import BaseAgent
from backend.agents.output_parser import OutputParser
from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.context import AgentContext, ContextSectionType
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.contracts.layout import MangaPageLayout


class LayoutAgent(BaseAgent):
    """
    Translates SceneScripts into semantic MangaPageLayout specifications.
    Determines panel storytelling importance, shot types, relative positions, and aspect ratios.
    """

    @property
    def agent_id(self) -> str:
        return "layout_agent"

    @property
    def agent_type(self) -> str:
        return "LAYOUT"

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

        project_id = context.project_id or "default_project"
        panels = []
        location = "Unknown"
        time_of_day = "Day"
        parent_artifact_id = None

        for sec in context.sections:
            if sec.section_type in (
                ContextSectionType.ARTIFACT,
                ContextSectionType.UPSTREAM_ARTIFACT,
            ) and isinstance(sec.content, dict):
                if sec.content.get("artifact_type") == ArtifactType.SCENE_SCRIPT.value:
                    project_id = sec.content.get("project_id", project_id)
                    parent_artifact_id = sec.content.get("artifact_id")
                    data = sec.content.get("data", {})
                    panels = data.get("panels", [])
                    location = data.get("location", location)
                    time_of_day = data.get("time_of_day", time_of_day)

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("page_layout.jinja")
        prompt = template.render(
            location=location,
            time_of_day=time_of_day,
            panels=panels,
        )

        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{MangaPageLayout.model_json_schema()}"

        tool_req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": prompt, "temperature": 0.7, "max_tokens": 4096},
        )
        tool_resp = await tool_executor.execute(tool_req)

        if not tool_resp or not tool_resp.success:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"Layout generation failed: {tool_resp.error_message if tool_resp else 'No response'}",
            )

        text_output = tool_resp.output_data.get("text", "")
        layout = OutputParser.parse_json(text_output, MangaPageLayout)

        if layout is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="JSON validation error: failed to parse MangaPageLayout from model output.",
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.9,
            reasoning_rationale="Generated semantic MangaPageLayout using Pydantic schema.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.MANGA_PAGE_LAYOUT,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=layout.model_dump(),
            parent_artifact_id=parent_artifact_id,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_layout_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
