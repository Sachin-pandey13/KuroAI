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
from backend.contracts.scene import SceneScript


class ScenePlannerAgent(BaseAgent):
    """
    Expands a StoryBeat into a detailed SceneScript containing panel descriptions.
    """

    @property
    def agent_id(self) -> str:
        return "scene_planner_agent"

    @property
    def agent_type(self) -> str:
        return "SCENE_PLANNER"

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
        story_beat = ""
        parent_artifact_ids = []

        for sec in context.sections:
            if sec.section_type == ContextSectionType.ARTIFACT and isinstance(sec.content, dict):
                # Look for a StoryOutline or StoryBeat
                if sec.content.get("artifact_type") == ArtifactType.STORY_OUTLINE.value:
                    project_id = sec.content.get("project_id", project_id)
                    parent_artifact_ids.append(sec.content.get("artifact_id"))
                    # In a real scenario, the TaskScheduler would pass a specific beat.
                    # For now, we take the whole outline or a summary.
                    story_beat = str(sec.content.get("data", {}))

        if not story_beat:
            # Fallback for testing
            story_beat = "Default story beat text."

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("scene_script.jinja")
        prompt = template.render(story_beat=story_beat)

        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{SceneScript.model_json_schema()}"

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
                error_message=f"Scene generation failed: {tool_resp.error_message if tool_resp else 'No response'}",
            )

        text_output = tool_resp.output_data.get("text", "")
        scene_script = OutputParser.parse_json(text_output, SceneScript)

        if scene_script is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="JSON validation error: failed to parse SceneScript from model output.",
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.9,
            reasoning_rationale="Generated SceneScript using Pydantic JSON schema.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.SCENE_SCRIPT,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=scene_script.model_dump(),
            parent_artifact_id=parent_artifact_ids[0] if parent_artifact_ids else None,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_scene_script_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
