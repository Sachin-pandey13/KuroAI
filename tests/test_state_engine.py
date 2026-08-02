"""
Test: Project State Engine (Milestone 2)
Validates that the ProjectStateEngine correctly owns project state
and references artifacts by ID from the ArtifactRegistry.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.contracts.artifact import Artifact, ArtifactType
from backend.contracts.goal import CreativeGoal, GoalStatus
from backend.contracts.project_state import AutonomyLevel
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.state_engine import (
    ArtifactAlreadyAttachedError,
    ArtifactNotRegisteredError,
    ProjectNotFoundError,
    ProjectStateEngine,
)


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def engine(registry: ArtifactRegistry) -> ProjectStateEngine:
    return ProjectStateEngine(artifact_registry=registry)


class TestCreateProject:
    def test_create_project_returns_state(self, engine):
        state = engine.create_project("My Manga", "A dark fantasy manga")
        assert state.title == "My Manga"
        assert state.project_id is not None

    def test_create_project_sets_defaults(self, engine):
        state = engine.create_project("Test", "Test project")
        assert state.autonomy_level == AutonomyLevel.GUIDED
        assert state.version == 1
        assert state.active_goals == []
        assert state.artifacts == {}

    def test_create_project_with_autonomy(self, engine):
        state = engine.create_project(
            "Auto Manga", "Full auto", autonomy_level=AutonomyLevel.AUTONOMOUS_STUDIO
        )
        assert state.autonomy_level == AutonomyLevel.AUTONOMOUS_STUDIO

    def test_create_multiple_projects(self, engine):
        p1 = engine.create_project("Project 1", "First")
        p2 = engine.create_project("Project 2", "Second")
        assert p1.project_id != p2.project_id
        assert engine.project_count == 2


class TestGetProject:
    def test_get_project_by_id(self, engine):
        state = engine.create_project("Test", "Desc")
        retrieved = engine.get_project(state.project_id)
        assert retrieved.title == "Test"

    def test_get_project_unknown_raises(self, engine):
        with pytest.raises(ProjectNotFoundError):
            engine.get_project("nonexistent-id")


class TestGetState:
    def test_get_state_returns_active(self, engine):
        engine.create_project("Active", "The active project")
        state = engine.get_state()
        assert state.title == "Active"

    def test_get_state_no_project_raises(self, engine):
        with pytest.raises(ProjectNotFoundError):
            engine.get_state()

    def test_set_active_project(self, engine):
        p1 = engine.create_project("P1", "First")
        engine.create_project("P2", "Second")
        # p2 is active (last created)
        assert engine.get_state().title == "P2"
        engine.set_active_project(p1.project_id)
        assert engine.get_state().title == "P1"


class TestAddGoal:
    def test_add_goal(self, engine):
        engine.create_project("Test", "Desc")
        goal = CreativeGoal(
            title="Draft Chapter 1",
            description="Write the opening chapter",
            target_milestone="STORY_DRAFT",
        )
        engine.add_goal(goal)
        state = engine.get_state()
        assert len(state.active_goals) == 1
        assert state.active_goals[0].title == "Draft Chapter 1"

    def test_add_multiple_goals(self, engine):
        engine.create_project("Test", "Desc")
        for i in range(3):
            engine.add_goal(
                CreativeGoal(
                    title=f"Goal {i}",
                    description=f"Description {i}",
                    target_milestone=f"MILESTONE_{i}",
                )
            )
        assert len(engine.get_state().active_goals) == 3

    def test_update_goal_status(self, engine):
        engine.create_project("Test", "Desc")
        goal = CreativeGoal(
            title="Draft Story",
            description="Write the story",
            target_milestone="STORY",
        )
        engine.add_goal(goal)
        updated = engine.update_goal_status(goal.goal_id, GoalStatus.COMPLETED)
        assert updated.status == GoalStatus.COMPLETED


class TestAttachDetachArtifact:
    def test_attach_artifact(self, engine, registry):
        engine.create_project("Test", "Desc")
        artifact = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"name": "Kuro"},
        )
        registry.register(artifact)
        engine.attach_artifact(artifact.artifact_id)
        assert artifact.artifact_id in engine.get_attached_artifact_ids()

    def test_attach_unregistered_raises(self, engine):
        engine.create_project("Test", "Desc")
        with pytest.raises(ArtifactNotRegisteredError):
            engine.attach_artifact("nonexistent-artifact-id")

    def test_attach_duplicate_raises(self, engine, registry):
        engine.create_project("Test", "Desc")
        artifact = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
        )
        registry.register(artifact)
        engine.attach_artifact(artifact.artifact_id)
        with pytest.raises(ArtifactAlreadyAttachedError):
            engine.attach_artifact(artifact.artifact_id)

    def test_detach_artifact(self, engine, registry):
        engine.create_project("Test", "Desc")
        artifact = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.SCENE_SCRIPT,
            owner_agent="story_agent",
        )
        registry.register(artifact)
        engine.attach_artifact(artifact.artifact_id)
        engine.detach_artifact(artifact.artifact_id)
        assert artifact.artifact_id not in engine.get_attached_artifact_ids()
        # Artifact still exists in registry after detach
        assert registry.exists(artifact.artifact_id) is True

    def test_detach_unknown_raises(self, engine):
        engine.create_project("Test", "Desc")
        with pytest.raises(ArtifactNotRegisteredError):
            engine.detach_artifact("nonexistent-id")


class TestMutateState:
    def test_mutate_metadata(self, engine):
        engine.create_project("Test", "Desc")
        engine.mutate_state({"metadata": {"genre": "dark_fantasy", "rating": "PG-13"}})
        state = engine.get_state()
        assert state.metadata["genre"] == "dark_fantasy"
        assert state.version == 2

    def test_mutate_style_guidelines(self, engine):
        engine.create_project("Test", "Desc")
        engine.mutate_state({"style_guidelines": {"art_style": "seinen", "line_weight": "heavy"}})
        state = engine.get_state()
        assert state.style_guidelines["art_style"] == "seinen"

    def test_mutate_title(self, engine):
        engine.create_project("Old Title", "Desc")
        engine.mutate_state({"title": "New Title"})
        assert engine.get_state().title == "New Title"

    def test_mutate_increments_version(self, engine):
        engine.create_project("Test", "Desc")
        assert engine.get_state().version == 1
        engine.mutate_state({"metadata": {"key": "val"}})
        assert engine.get_state().version == 2
        engine.mutate_state({"metadata": {"key2": "val2"}})
        assert engine.get_state().version == 3


class TestTransactionStubs:
    def test_begin_transaction_does_not_raise(self, engine):
        engine.create_project("Test", "Desc")
        engine.begin_transaction()  # Should not raise

    def test_commit_does_not_raise(self, engine):
        engine.create_project("Test", "Desc")
        engine.commit()  # Should not raise

    def test_rollback_does_not_raise(self, engine):
        engine.create_project("Test", "Desc")
        engine.rollback_transaction()  # Should not raise


# =====================================================================
# Behavioral / Integration Tests
# =====================================================================


class TestBehavioralScenarios:
    """
    End-to-end behavioral tests validating the Artifact Registry ↔
    Project State Engine ownership boundary.
    """

    def test_scenario_1_create_register_attach_verify(self, engine, registry):
        """
        Create Project → Register Character → Attach Character →
        State contains Character ID.
        """
        engine.create_project("Manga Project", "A dark fantasy manga")
        character = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"name": "Kuro", "hair": "black", "eyes": "red"},
        )
        registry.register(character)
        engine.attach_artifact(character.artifact_id)

        state = engine.get_state()
        assert character.artifact_id in state.artifacts
        assert state.artifacts[character.artifact_id].data["name"] == "Kuro"

    def test_scenario_2_register_story_attach_retrieve(self, engine, registry):
        """
        Register Story → Attach Story → Retrieve Project → Story exists.
        """
        engine.create_project("Story Project", "Test story")
        story = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
            data={"title": "Chapter 1", "beats": ["intro", "conflict"]},
        )
        registry.register(story)
        engine.attach_artifact(story.artifact_id)

        retrieved = engine.get_state()
        assert story.artifact_id in retrieved.artifacts
        assert retrieved.artifacts[story.artifact_id].data["title"] == "Chapter 1"

    def test_scenario_3_mutate_metadata_persists(self, engine):
        """
        Mutate Project Metadata → Reload State → Metadata persists.
        """
        engine.create_project("Meta Project", "Testing metadata")
        engine.mutate_state(
            {
                "metadata": {"genre": "horror", "chapters": 12},
                "style_guidelines": {"palette": "dark"},
            }
        )
        reloaded = engine.get_state()
        assert reloaded.metadata["genre"] == "horror"
        assert reloaded.metadata["chapters"] == 12
        assert reloaded.style_guidelines["palette"] == "dark"

    def test_scenario_4_attach_unknown_artifact_raises(self, engine):
        """
        Attempt to attach unknown Artifact → Raise ArtifactNotRegisteredError.
        """
        engine.create_project("Error Project", "Testing errors")
        with pytest.raises(ArtifactNotRegisteredError):
            engine.attach_artifact("totally-fake-artifact-id-12345")

    def test_scenario_5_full_project_assembly(self, engine, registry):
        """
        Full project assembly: create project, register multiple artifacts,
        attach all, verify state integrity.
        """
        engine.create_project("Full Manga", "Complete assembly test")

        character = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.CHARACTER_PROFILE,
            owner_agent="character_agent",
            data={"name": "Yuki"},
        )
        story = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.STORY_OUTLINE,
            owner_agent="story_agent",
            data={"title": "Prologue"},
        )
        panel = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.GENERATED_IMAGE,
            owner_agent="image_agent",
            data={"scene": "opening_shot"},
        )

        for art in [character, story, panel]:
            registry.register(art)
            engine.attach_artifact(art.artifact_id)

        state = engine.get_state()
        assert len(state.artifacts) == 3
        assert len(engine.get_attached_artifact_ids()) == 3
        assert registry.count == 3

    def test_scenario_6_detach_does_not_delete_from_registry(self, engine, registry):
        """
        Detaching an artifact removes reference from project state but
        preserves the artifact in the registry (separation of concerns).
        """
        engine.create_project("Detach Test", "Testing detach")
        artifact = Artifact(
            project_id="proj-001",
            artifact_type=ArtifactType.WORLD_LORE,
            owner_agent="story_agent",
            data={"world": "fantasy realm"},
        )
        registry.register(artifact)
        engine.attach_artifact(artifact.artifact_id)

        # Detach from project
        engine.detach_artifact(artifact.artifact_id)
        assert artifact.artifact_id not in engine.get_state().artifacts

        # Still exists in registry
        assert registry.exists(artifact.artifact_id) is True
        assert registry.get(artifact.artifact_id).data["world"] == "fantasy realm"
