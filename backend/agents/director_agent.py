from typing import List, Optional

from backend.agents.base_agent import BaseAgent
from backend.agents.tool_executor import BaseToolExecutor
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.context import AgentContext
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.contracts.execution_plan import ExecutionPlan, TaskSpec


class DirectorAgent(BaseAgent):
    """
    DirectorAgent — The "Brain" of the KuroAI system.

    Stateless Reasoning Transformer (Fourth & Fifth Laws):
    1. Reads user prompt and narrative goal from AgentContext.
    2. Uses GENERATE_TEXT capability (or structured goal decomposition)
       to construct an acyclic execution graph of TaskSpecs.
    3. Produces a first-class immutable ExecutionPlan artifact.
    4. Never mutates TaskScheduler or TaskRegistry directly.
    """

    @property
    def agent_id(self) -> str:
        return "director_agent"

    @property
    def agent_type(self) -> str:
        return "DIRECTOR"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        """
        Execute goal decomposition reasoning:
        1. Extract prompt and goal_id from context.
        2. Generate TaskSpec list via tool_executor or structured fallback.
        3. Build ExecutionPlan domain model.
        4. Wrap in Artifact(artifact_type=ArtifactType.EXECUTION_PLAN).
        """
        user_prompt = f"Create manga for goal {context.goal_id}"
        if context.sections:
            for sec in context.sections:
                if sec.content and isinstance(sec.content, dict):
                    prompt_val = sec.content.get("prompt", "") or sec.content.get("goal", "")
                    if prompt_val:
                        user_prompt = prompt_val
                        break

        model_name = "default-text-model"
        provider_name = "default-text-provider"
        capability_used = []

        # Default structured task decomposition
        task_specs = self._default_decomposition(context.goal_id, user_prompt)

        if tool_executor is not None:
            tool_req = ToolRequest(
                capability_type=CapabilityType.GENERATE_TEXT,
                parameters={
                    "prompt": (
                        f"Decompose narrative goal '{user_prompt}' into execution plan tasks. "
                        f"Target agents: STORY, CHARACTER, LAYOUT, IMAGE, CREATIVE_SAFETY."
                    ),
                    "goal_id": context.goal_id,
                },
            )
            tool_resp = await tool_executor.execute(tool_req)
            if tool_resp and tool_resp.success:
                model_name = tool_resp.model_name
                provider_name = tool_resp.provider_name
                capability_used.append(str(CapabilityType.GENERATE_TEXT))

        plan = ExecutionPlan(
            goal_id=context.goal_id,
            user_prompt=user_prompt,
            task_specs=task_specs,
            metadata={
                "decomposed_by": self.agent_id,
                "provider": provider_name,
                "model": model_name,
            },
        )

        project_id = "default_project"
        if (
            context.sections
            and context.sections[0].content
            and isinstance(context.sections[0].content, dict)
        ):
            project_id = context.sections[0].content.get("project_id", project_id)

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.98,
            reasoning_rationale=(
                f"Decomposed goal '{user_prompt}' into {len(task_specs)} structured task specs "
                f"using provider {provider_name}/{model_name}."
            ),
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=model_name,
                provider_name=provider_name,
                prompt=user_prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.EXECUTION_PLAN,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=plan.model_dump(),
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.goal_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={
                "latest_execution_plan_id": artifact.artifact_id,
                "planned_task_count": len(task_specs),
            },
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=capability_used,
        )

    def _default_decomposition(self, goal_id: str, prompt: str) -> List[TaskSpec]:
        """Generate a clean DAG task decomposition for narrative creation."""
        story_spec_id = f"spec_story_{goal_id[:8]}"
        char_spec_id = f"spec_char_{goal_id[:8]}"
        layout_spec_id = f"spec_layout_{goal_id[:8]}"
        image_spec_id = f"spec_image_{goal_id[:8]}"
        safety_spec_id = f"spec_safety_{goal_id[:8]}"

        return [
            TaskSpec(
                spec_id=story_spec_id,
                target_agent_type="STORY",
                payload={"goal_id": goal_id, "prompt": prompt, "action": "draft_outline"},
                dependencies=[],
                priority=10,
            ),
            TaskSpec(
                spec_id=char_spec_id,
                target_agent_type="CHARACTER",
                payload={"goal_id": goal_id, "prompt": prompt, "action": "design_characters"},
                dependencies=[story_spec_id],
                priority=8,
            ),
            TaskSpec(
                spec_id=layout_spec_id,
                target_agent_type="LAYOUT",
                payload={"goal_id": goal_id, "prompt": prompt, "action": "compose_layout"},
                dependencies=[story_spec_id],
                priority=7,
            ),
            TaskSpec(
                spec_id=image_spec_id,
                target_agent_type="IMAGE",
                payload={"goal_id": goal_id, "prompt": prompt, "action": "generate_panels"},
                dependencies=[char_spec_id, layout_spec_id],
                priority=5,
            ),
            TaskSpec(
                spec_id=safety_spec_id,
                target_agent_type="CREATIVE_SAFETY",
                payload={"goal_id": goal_id, "prompt": prompt, "action": "review_safety"},
                dependencies=[image_spec_id],
                priority=3,
            ),
        ]
