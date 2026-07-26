import os
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from pydantic import ValidationError

from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext, ContextSectionType
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.agents.tool_executor import BaseToolExecutor
from backend.agents.output_parser import OutputParser
from backend.contracts.story import StoryOutline

class StoryAgent(BaseAgent):
    """
    Drafts high-level story outlines using Jinja templates and JSON mode.
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
        if tool_executor is None:
            return AgentResult(task_id=context.task_id, agent_id=self.agent_id, agent_type=self.agent_type, success=False, error_message="No tool executor provided")

        project_id = "default_project"
        user_prompt = ""
        director_brief = ""
        
        for sec in context.sections:
            if sec.section_type == ContextSectionType.GOAL and isinstance(sec.content, dict):
                user_prompt = sec.content.get("prompt", str(sec.content))
                project_id = sec.content.get("project_id", project_id)
            elif sec.section_type == ContextSectionType.DIRECTOR_BRIEF:
                director_brief = str(sec.content)

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("story_outline.jinja")
        prompt = template.render(user_prompt=user_prompt, director_brief=director_brief)
        
        # We append JSON instructions since we don't have native response_format integrated in providers yet
        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{StoryOutline.model_json_schema()}"

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
                error_message=f"Story generation failed: {tool_resp.error_message if tool_resp else 'No response'}"
            )

        text_output = tool_resp.output_data.get("text", "")
        story_outline = OutputParser.parse_json(text_output, StoryOutline)
        
        if story_outline is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"JSON validation error: failed to parse StoryOutline from model output."
            )
            
        story_outline.project_id = project_id

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.9,
            reasoning_rationale="Generated StoryOutline using Pydantic JSON schema.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=story_outline.model_dump(),
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_story_outline_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
