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
from backend.contracts.review import ReviewFeedback


class ImageReviewAgent(BaseAgent):
    """
    Quality control reviewer for generated panel artwork.
    Inspects images/metadata against prompts and visual guidelines.
    Produces ReviewFeedback artifacts with review_score (0-100), confidence, and identified issues.
    Strictly follows the principle: Review, don't rewrite.
    """

    @property
    def agent_id(self) -> str:
        return "image_review_agent"

    @property
    def agent_type(self) -> str:
        return "IMAGE_REVIEW"

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
        target_artifact_id = "target_image_1"
        prompt = ""
        expected_details = "Manga style line art"

        for sec in context.sections:
            if sec.section_type in (
                ContextSectionType.ARTIFACT,
                ContextSectionType.UPSTREAM_ARTIFACT,
            ) and isinstance(sec.content, dict):
                if sec.content.get("artifact_type") == ArtifactType.GENERATED_IMAGE.value:
                    target_artifact_id = sec.content.get("artifact_id", target_artifact_id)
                    project_id = sec.content.get("project_id", project_id)
                    data = sec.content.get("data", {})
                    prompt = data.get("prompt", prompt)
            elif sec.section_type == ContextSectionType.GOAL and isinstance(sec.content, dict):
                if not prompt:
                    prompt = sec.content.get("prompt", "")

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("image_review.jinja")
        rendered_prompt = template.render(
            target_artifact_id=target_artifact_id,
            prompt=prompt or "Default panel image prompt",
            expected_details=expected_details,
        )

        rendered_prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{ReviewFeedback.model_json_schema()}"

        tool_req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": rendered_prompt, "temperature": 0.2, "max_tokens": 2048},
        )
        tool_resp = await tool_executor.execute(tool_req)

        if not tool_resp or not tool_resp.success:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"Image review failed: {tool_resp.error_message if tool_resp else 'No response'}",
            )

        text_output = tool_resp.output_data.get("text", "")
        feedback = OutputParser.parse_json(text_output, ReviewFeedback)

        if feedback is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="JSON validation error: failed to parse ReviewFeedback from model output.",
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=feedback.confidence if feedback.confidence is not None else 0.9,
            reasoning_rationale=f"Evaluated image quality score: {feedback.review_score}/100. Passed: {feedback.passed}.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=rendered_prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.REVIEW_FEEDBACK,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=feedback.model_dump(),
            parent_artifact_id=target_artifact_id,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_review_feedback_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
