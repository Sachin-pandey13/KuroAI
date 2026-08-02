from typing import Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.context import AgentContext
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance


class ImageAgent(BaseAgent):
    """
    Generates manga panel artwork via the Capability Registry interface (BaseToolExecutor).
    Uses character blueprints, prompts, style guides, and ControlNet/IP-Adapter references.
    """

    @property
    def agent_id(self) -> str:
        return "image_agent"

    @property
    def agent_type(self) -> str:
        return "IMAGE"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        """
        Execute panel image generation task:
        1. Extract prompt and style guidance from AgentContext.
        2. Execute GENERATE_IMAGE capability via injected tool_executor.
        3. Produce Artifact(artifact_type=ArtifactType.GENERATED_IMAGE).
        4. Attach DecisionTrace with ExecutionProvenance.
        """
        prompt = f"Panel illustration for goal {context.goal_id}"
        width = 1024
        height = 1024

        if context.sections:
            for sec in context.sections:
                if sec.content and isinstance(sec.content, dict):
                    if "prompt" in sec.content:
                        prompt = str(sec.content["prompt"])
                    if "width" in sec.content:
                        width = int(sec.content["width"])
                    if "height" in sec.content:
                        height = int(sec.content["height"])

        image_path = f"/output/panel_{context.goal_id}.png"
        model_name = "default-image-model"
        provider_name = "default-image-provider"
        capability_used = []

        if tool_executor is not None:
            tool_req = ToolRequest(
                capability_type=CapabilityType.GENERATE_IMAGE,
                parameters={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                },
            )
            tool_resp = await tool_executor.execute(tool_req)
            if tool_resp and tool_resp.success:
                image_path = tool_resp.output_data.get("image_path", image_path)
                model_name = tool_resp.model_name
                provider_name = tool_resp.provider_name
                capability_used.append(str(CapabilityType.GENERATE_IMAGE))

        project_id = "default_project"
        if (
            context.sections
            and context.sections[0].content
            and isinstance(context.sections[0].content, dict)
        ):
            project_id = context.sections[0].content.get("project_id", project_id)

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.92,
            reasoning_rationale=f"Generated manga panel via {provider_name}/{model_name}.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=model_name,
                provider_name=provider_name,
                prompt=prompt[:300],
                hyperparameters={"width": width, "height": height},
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.GENERATED_IMAGE,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data={
                "image_path": image_path,
                "width": width,
                "height": height,
                "prompt": prompt,
            },
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.goal_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_panel_image_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=capability_used,
        )
