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
from backend.contracts.dialogue import SceneDialogue

class DialogueAgent(BaseAgent):
    """
    Writes compelling dialogue for a given SceneScript based on CharacterProfiles.
    Produces SpeechBubble artifacts.
    """

    @property
    def agent_id(self) -> str:
        return "dialogue_agent"

    @property
    def agent_type(self) -> str:
        return "DIALOGUE"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        if tool_executor is None:
            return AgentResult(task_id=context.task_id, agent_id=self.agent_id, agent_type=self.agent_type, success=False, error_message="No tool executor provided")

        project_id = "default_project"
        scene_panels = []
        characters = []
        parent_artifact_ids = []
        
        for sec in context.sections:
            if sec.section_type == ContextSectionType.ARTIFACT and isinstance(sec.content, dict):
                if sec.content.get("artifact_type") == ArtifactType.SCENE_SCRIPT.value:
                    project_id = sec.content.get("project_id", project_id)
                    parent_artifact_ids.append(sec.content.get("artifact_id"))
                    scene_panels = sec.content.get("data", {}).get("panels", [])
                elif sec.content.get("artifact_type") == ArtifactType.CHARACTER_PROFILE.value:
                    characters.append(sec.content.get("data", {}))

        env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
        template = env.get_template("dialogue.jinja")
        prompt = template.render(
            scene_panels=scene_panels,
            characters=characters
        )
        
        prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{SceneDialogue.model_json_schema()}"

        tool_req = ToolRequest(
            capability_type=CapabilityType.GENERATE_TEXT,
            parameters={"prompt": prompt, "temperature": 0.8, "max_tokens": 4096},
        )
        tool_resp = await tool_executor.execute(tool_req)
        
        if not tool_resp or not tool_resp.success:
            return AgentResult(
                task_id=context.task_id, 
                agent_id=self.agent_id, 
                agent_type=self.agent_type, 
                success=False, 
                error_message=f"Dialogue generation failed: {tool_resp.error_message if tool_resp else 'No response'}"
            )

        text_output = tool_resp.output_data.get("text", "")
        scene_dialogue = OutputParser.parse_json(text_output, SceneDialogue)
        
        if scene_dialogue is None:
            return AgentResult(
                task_id=context.task_id,
                agent_id=self.agent_id,
                agent_type=self.agent_type,
                success=False,
                error_message=f"JSON validation error: failed to parse SceneDialogue from model output."
            )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.9,
            reasoning_rationale="Generated SceneDialogue using Pydantic JSON schema.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name=tool_resp.model_name,
                provider_name=tool_resp.provider_name,
                prompt=prompt[:300],
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.SPEECH_BUBBLE,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=scene_dialogue.model_dump(),
            parent_artifact_id=parent_artifact_ids[0] if parent_artifact_ids else None,
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_dialogue_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
