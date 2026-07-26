import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader

from backend.agents.base_agent import BaseAgent
from backend.contracts.context import AgentContext, ContextSectionType
from backend.contracts.agent import AgentResult
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactState
from backend.contracts.capability import CapabilityType, ToolRequest
from backend.contracts.decision_trace import DecisionTrace, ExecutionProvenance
from backend.agents.tool_executor import BaseToolExecutor
from backend.agents.output_parser import OutputParser
from backend.contracts.review import ContinuityReport, ReviewIssue, ReviewSeverity, ReviewCategory


# =====================================================================
# Plugin Continuity Rule Pipeline Interface & Concrete Rules
# =====================================================================

class ContinuityRule(ABC):
    """Abstract Base Class for modular continuity rules."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @abstractmethod
    def evaluate(self, characters: List[Dict[str, Any]], scenes: List[Dict[str, Any]]) -> List[ReviewIssue]:
        """Evaluates narrative data against this specific rule and returns identified issues."""
        pass


class CharacterAppearanceRule(ContinuityRule):
    """Rule verifying character visual descriptors across scenes."""

    @property
    def rule_id(self) -> str:
        return "character_appearance_rule"

    def evaluate(self, characters: List[Dict[str, Any]], scenes: List[Dict[str, Any]]) -> List[ReviewIssue]:
        issues = []
        for char in characters:
            name = char.get("name", "")
            app = char.get("appearance", {})
            hair = app.get("hair", "").lower()
            
            # Simple deterministic rule check: if hair is described as blonde in profile but panel says dark
            for scene in scenes:
                for panel in scene.get("panels", []):
                    action = panel.get("action", "").lower()
                    if name.lower() in action and hair and "dark hair" in action and "blonde" in hair:
                        issues.append(
                            ReviewIssue(
                                issue_id=f"app_{char.get('character_id', 'unk')}_{panel.get('panel_number', 0)}",
                                severity=ReviewSeverity.WARNING,
                                category=ReviewCategory.CHARACTER_APPEARANCE,
                                description=f"Character '{name}' has profile hair '{hair}' but panel action specifies 'dark hair'.",
                                panel_number=panel.get("panel_number"),
                            )
                        )
        return issues


class RelationshipRule(ContinuityRule):
    """Rule checking relationship dynamics across characters."""

    @property
    def rule_id(self) -> str:
        return "relationship_rule"

    def evaluate(self, characters: List[Dict[str, Any]], scenes: List[Dict[str, Any]]) -> List[ReviewIssue]:
        issues = []
        # Checks if sworn enemies are described as best friends without arc justification
        char_map = {c.get("character_id"): c for c in characters}
        for char in characters:
            for rel in char.get("relationships", []):
                target_id = rel.get("target_character_id")
                rel_type = rel.get("relationship_type", "").lower()
                target = char_map.get(target_id)
                if target and rel_type in ("enemy", "rival", "nemesis"):
                    for scene in scenes:
                        for panel in scene.get("panels", []):
                            action = panel.get("action", "").lower()
                            if char.get("name", "").lower() in action and target.get("name", "").lower() in action:
                                if "best friend" in action or "hugs warmly" in action:
                                    issues.append(
                                        ReviewIssue(
                                            issue_id=f"rel_{char.get('character_id')}_{target_id}",
                                            severity=ReviewSeverity.ERROR,
                                            category=ReviewCategory.RELATIONSHIP_DYNAMIC,
                                            description=f"Characters '{char.get('name')}' and '{target.get('name')}' are defined as '{rel_type}' but panel action shows intimate warmth.",
                                            panel_number=panel.get("panel_number"),
                                        )
                                    )
        return issues


# =====================================================================
# ContinuityAgent Implementation
# =====================================================================

class ContinuityAgent(BaseAgent):
    """
    Validates narrative continuity across multiple scenes and character profiles.
    Uses a modular rule pipeline (ContinuityRule) and optional LLM inspection to generate a ContinuityReport.
    """

    def __init__(self, rules: Optional[List[ContinuityRule]] = None):
        self.rules: List[ContinuityRule] = rules if rules is not None else [
            CharacterAppearanceRule(),
            RelationshipRule(),
        ]

    @property
    def agent_id(self) -> str:
        return "continuity_agent"

    @property
    def agent_type(self) -> str:
        return "CONTINUITY"

    async def execute(
        self,
        context: AgentContext,
        tool_executor: Optional[BaseToolExecutor] = None,
    ) -> AgentResult:
        project_id = context.project_id or "default_project"
        characters = []
        scenes = []

        for sec in context.sections:
            if sec.section_type in (ContextSectionType.ARTIFACT, ContextSectionType.UPSTREAM_ARTIFACT) and isinstance(sec.content, dict):
                art_type = sec.content.get("artifact_type")
                if art_type == ArtifactType.CHARACTER_PROFILE.value:
                    characters.append(sec.content.get("data", {}))
                elif art_type == ArtifactType.SCENE_SCRIPT.value:
                    scenes.append(sec.content.get("data", {}))

        # 1. Run deterministic plugin rule pipeline
        rule_issues: List[ReviewIssue] = []
        for rule in self.rules:
            rule_issues.extend(rule.evaluate(characters, scenes))

        # 2. Run LLM evaluation via Jinja prompt if executor provided
        llm_report: Optional[ContinuityReport] = None
        if tool_executor is not None and (characters or scenes):
            env = Environment(loader=FileSystemLoader(os.path.join("backend", "prompts")))
            template = env.get_template("continuity_check.jinja")
            prompt = template.render(characters=characters, scenes=scenes)
            prompt += f"\n\nYou MUST return a valid JSON object adhering to this JSON schema:\n{ContinuityReport.model_json_schema()}"

            tool_req = ToolRequest(
                capability_type=CapabilityType.GENERATE_TEXT,
                parameters={"prompt": prompt, "temperature": 0.3, "max_tokens": 4096},
            )
            tool_resp = await tool_executor.execute(tool_req)

            if tool_resp and tool_resp.success:
                text_output = tool_resp.output_data.get("text", "")
                llm_report = OutputParser.parse_json(text_output, ContinuityReport)

        # Merge results: combine rule issues + LLM report issues
        combined_issues = list(rule_issues)
        score = 100.0
        if llm_report is not None:
            combined_issues.extend(llm_report.issues)
            score = llm_report.review_score
        elif rule_issues:
            # Calculate simple score reduction for rule hits
            errors = sum(1 for i in rule_issues if i.severity == ReviewSeverity.ERROR)
            warnings = sum(1 for i in rule_issues if i.severity == ReviewSeverity.WARNING)
            score = max(0.0, 100.0 - (errors * 25.0 + warnings * 10.0))

        passed = score >= 80.0 and not any(i.severity == ReviewSeverity.ERROR for i in combined_issues)

        final_report = ContinuityReport(
            project_id=project_id,
            passed=passed,
            review_score=score,
            issues=combined_issues,
            characters_checked=[c.get("character_id", "unk") for c in characters],
            scenes_checked=len(scenes),
        )

        decision_trace = DecisionTrace(
            agent_id=self.agent_id,
            confidence_score=0.95,
            reasoning_rationale=f"Evaluated continuity across {len(characters)} characters and {len(scenes)} scenes with {len(self.rules)} rules.",
            context_sources_used=[str(s.section_type) for s in context.sections],
            provenance=ExecutionProvenance(
                model_name="rule_engine_and_llm",
                provider_name="internal",
                prompt=f"Checked {len(combined_issues)} total issues.",
            ),
        )

        artifact = Artifact(
            project_id=project_id,
            artifact_type=ArtifactType.CONTINUITY_REPORT,
            owner_agent=self.agent_id,
            state=ArtifactState.ACTIVE,
            data=final_report.model_dump(),
            decision_trace=decision_trace,
        )

        return AgentResult(
            task_id=context.task_id,
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            success=True,
            state_updates={"latest_continuity_report_id": artifact.artifact_id},
            produced_artifacts=[artifact],
            decision_trace=decision_trace,
            capability_requests=[str(CapabilityType.GENERATE_TEXT)],
        )
