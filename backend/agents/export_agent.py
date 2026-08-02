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
from backend.contracts.export import ExportManifest


class ExportAgent(BaseAgent):
    """
    Compiles existing layout specs, panel images, and speech bubbles into an ExportManifest artifact.
    Strictly focuses on packaging artifacts into printable/publishable formats — performs NO creative reasoning.
    """

    @property
    def agent_id(self) -> str:
        return "export_agent"

    @property
    def agent_type(self) -> str:
        return "EXPORT"

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
        pages_data = []
        parent_artifact_ids = []

        for sec in context.sections:
            if sec.section_type in (
                ContextSectionType.ARTIFACT,
                ContextSectionType.UPSTREAM_ARTIFACT,
            ) and isinstance(sec.content, dict):
                art_type = sec.content.get("artifact_type")
                art_id = sec.content.get("artifact_id")
                if art_id:
                    parent_artifact_ids.append(art_id)
                if sec.content.get("project_id"):
                    project_id = sec.content["project_id"]

                if art_type == ArtifactType.MANGA_PAGE_LAYOUT.value:
                    layout_data = sec.content.get("data", {})
                    pages_data.append(
                        {
                            "page_number": layout_data.get("page_number", 1),
                            "grid_style": layout_data.get("grid_style", "DYNAMIC"),
                            "panels": [
                                {
                                    "panel_number": s.get("panel_number", 1),
                                    "image_asset_path": f"/assets/panel_{s.get('panel_number', 1)}.png",
                                    "shot_type": s.get("shot_type", "Standard"),
                                    "speech_bubbles": [],
                                }
                                for s in layout_data.get("slots", [])
                            ],
                        }
                    )

        if not pages_data:
            pages_data = [
                {
                    "page_number": 1,
                    "grid_style": "DEFAULT_GRID",
                    "panels": [
                        {
                            "panel_number": 1,
                            "image_asset_path": "/assets/panel_1.png",
                            "shot_type": "Wide",
                            "speech_bubbles": [],
                        }
                    ],
                }
            ]

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("export_manifest.jinja")
        prompt = template.render(
            project_id=project_id,
            title=f"Manga Project {project_id}",
            pages=pages_data,
        )

        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{ExportManifest.model_json_schema()}"

        tool_req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": prompt, "temperature": 0.1, "max_tokens": 4096},
        )
        tool_resp = await tool_executor.execute(tool_req)

        if not tool_resp or not tool_resp.success:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"Export manifest generation failed: {tool_resp.error_message if tool_resp else 'No response'}",
            )

        text_output = tool_resp.output_data.get("text", "")
        manifest = OutputParser.parse_json(text_output, ExportManifest)

        if manifest is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message="JSON validation error: failed to parse ExportManifest from model output.",
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.99,
            reasoning_rationale=f"Compiled export manifest for {manifest.total_pages} page(s). PDF Path: {manifest.output_pdf_path}",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.EXPORT_PDF,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=manifest.model_dump(),
            parent_artifact_id=parent_artifact_ids[0] if parent_artifact_ids else None,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_export_pdf_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
