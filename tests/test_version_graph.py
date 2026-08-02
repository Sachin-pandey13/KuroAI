"""
Test: Version Graph & Editability Engine (Milestone 4)
Verifies Stages 1-6: Version Contracts, Timeline Management, Non-Destructive Rollback,
Structural Diff Engine, and Integration Scenarios 1-6.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from backend.contracts.artifact import Artifact, ArtifactState, ArtifactType
from backend.engine.artifact_registry import ArtifactRegistry
from backend.engine.dependency_graph import DependencyGraph
from backend.engine.version_graph import (
    VersionGraph,
    VersionNotFoundError,
)


@pytest.fixture
def vg() -> VersionGraph:
    return VersionGraph()


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def graph() -> DependencyGraph:
    return DependencyGraph()


# =====================================================================
# Unit Tests — Version Recording & Retrieval
# =====================================================================


class TestVersionRecordingAndRetrieval:
    def test_record_first_version(self, vg):
        v1 = vg.record_version("art-001", {"hair": "black"}, {"style": "manga"})
        assert v1.version_number == 1
        assert v1.artifact_id == "art-001"
        assert v1.data_snapshot["hair"] == "black"
        assert vg.has_history("art-001") is True

    def test_sequential_version_numbering(self, vg):
        v1 = vg.record_version("art-001", {"hair": "black"}, {})
        v2 = vg.record_version("art-001", {"hair": "brown"}, {})
        v3 = vg.record_version("art-001", {"hair": "red"}, {})

        assert v1.version_number == 1
        assert v2.version_number == 2
        assert v3.version_number == 3

    def test_snapshot_immutability(self, vg):
        data = {"hair": "black", "nested": {"key": "value"}}
        vg.record_version("art-001", data, {})

        # Mutate local data dictionary
        data["hair"] = "red"
        data["nested"]["key"] = "mutated"

        # Snapshot inside VersionGraph remains pristine
        retrieved = vg.get_version("art-001", 1)
        assert retrieved.data_snapshot["hair"] == "black"
        assert retrieved.data_snapshot["nested"]["key"] == "value"

    def test_get_latest(self, vg):
        vg.record_version("art-001", {"v": 1}, {})
        vg.record_version("art-001", {"v": 2}, {})
        latest = vg.get_latest("art-001")
        assert latest.version_number == 2
        assert latest.data_snapshot["v"] == 2

    def test_get_version(self, vg):
        vg.record_version("art-001", {"v": 1}, {})
        vg.record_version("art-001", {"v": 2}, {})
        v1 = vg.get_version("art-001", 1)
        assert v1.data_snapshot["v"] == 1

    def test_get_version_out_of_bounds_raises(self, vg):
        vg.record_version("art-001", {"v": 1}, {})
        with pytest.raises(VersionNotFoundError):
            vg.get_version("art-001", 99)

    def test_get_history(self, vg):
        vg.record_version("art-001", {"v": 1}, {})
        vg.record_version("art-001", {"v": 2}, {})
        history = vg.get_history("art-001")
        assert len(history) == 2
        assert [v.version_number for v in history] == [1, 2]

    def test_has_history_and_clear_history(self, vg):
        assert vg.has_history("art-001") is False
        vg.record_version("art-001", {"v": 1}, {})
        assert vg.has_history("art-001") is True
        vg.clear_history("art-001")
        assert vg.has_history("art-001") is False


# =====================================================================
# Unit Tests — Structural Version Diff Engine
# =====================================================================


class TestVersionDiffEngine:
    def test_diff_structural_changes(self, vg):
        vg.record_version("art-001", {"hair": "black", "hat": "cap", "eyes": "red"}, {})
        vg.record_version("art-001", {"hair": "red", "glasses": True, "eyes": "red"}, {})

        result = vg.diff("art-001", 1, 2)

        assert result.added == {"glasses": True}
        assert result.removed == {"hat": "cap"}
        assert result.modified == {"hair": {"old": "black", "new": "red"}}
        assert "eyes" in result.unchanged


# =====================================================================
# Integration Scenarios 1 to 6
# =====================================================================


class TestIntegrationScenarios:

    def test_scenario_1_character_hair_progression(self, vg):
        """
        Scenario 1: Character Hair color progression (Black -> Brown -> Red).
        Verify three version snapshots exist.
        """
        vg.record_version(
            "char-01", {"name": "Kuro", "hair": "Black"}, {}, change_summary="Initial draft"
        )
        vg.record_version(
            "char-01", {"name": "Kuro", "hair": "Brown"}, {}, change_summary="Lightened hair"
        )
        vg.record_version("char-01", {"name": "Kuro", "hair": "Red"}, {}, change_summary="Dyed red")

        history = vg.get_history("char-01")
        assert len(history) == 3
        assert [v.data_snapshot["hair"] for v in history] == ["Black", "Brown", "Red"]

    def test_scenario_2_non_destructive_rollback(self, vg):
        """
        Scenario 2: Rollback V3 -> V1 -> V4.
        Verify V1, V2, V3, V4 all preserved, V4 contents == V1, V4.rollback_of == 1.
        """
        vg.record_version("char-01", {"hair": "Black"}, {})
        vg.record_version("char-01", {"hair": "Brown"}, {})
        vg.record_version("char-01", {"hair": "Red"}, {})

        v4 = vg.rollback("char-01", target_version=1, reason="Restored black hair")

        assert v4.version_number == 4
        assert v4.data_snapshot["hair"] == "Black"
        assert v4.rollback_of == 1

        history = vg.get_history("char-01")
        assert len(history) == 4
        assert [v.version_number for v in history] == [1, 2, 3, 4]

    def test_scenario_3_dialogue_diff_calculation(self, vg):
        """
        Scenario 3: Dialogue update diff ("Hello" -> "Hello, Captain").
        Verify diff returns modified dialogue text only.
        """
        vg.record_version("dialogue-01", {"speaker": "Yuki", "text": "Hello"}, {})
        vg.record_version("dialogue-01", {"speaker": "Yuki", "text": "Hello, Captain"}, {})

        diff_res = vg.diff("dialogue-01", 1, 2)
        assert diff_res.added == {}
        assert diff_res.removed == {}
        assert diff_res.modified == {"text": {"old": "Hello", "new": "Hello, Captain"}}
        assert "speaker" in diff_res.unchanged

    def test_scenario_4_rollback_plus_dependency_graph(self, vg, registry, graph):
        """
        Scenario 4: Rollback + Dependency Graph.
        Story -> Scene -> Prompt -> Image
        Rollback Scene Script -> Scene Script ACTIVE, Prompt & Image STALE.
        """
        # Build DAG in Dependency Graph
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("Scene", "SCENE_SCRIPT")
        graph.create_node("Prompt", "PANEL_PROMPT")
        graph.create_node("Image", "GENERATED_IMAGE")

        graph.connect("Story", "Scene")
        graph.connect("Scene", "Prompt")
        graph.connect("Prompt", "Image")

        # Register Artifact in Registry
        scene_art = Artifact(
            artifact_id="Scene",
            project_id="proj-01",
            artifact_type=ArtifactType.SCENE_SCRIPT,
            owner_agent="story_agent",
            data={"text": "Scene v1 draft"},
        )
        registry.register(scene_art)

        # Record versions in Version Graph
        vg.record_version("Scene", {"text": "Scene v1 draft"}, {})
        vg.record_version("Scene", {"text": "Scene v2 draft"}, {})

        # Execute Integrated Rollback
        v3 = vg.rollback_and_invalidate(
            artifact_id="Scene",
            target_version=1,
            artifact_registry=registry,
            dependency_graph=graph,
            reason="Restored original scene draft",
        )

        assert v3.version_number == 3
        assert registry.get("Scene").data["text"] == "Scene v1 draft"
        assert registry.get("Scene").current_version == 3

        # Verify selective invalidation in Dependency Graph
        assert graph.get_node("Story").state == ArtifactState.ACTIVE
        assert graph.get_node("Scene").state == ArtifactState.ACTIVE
        assert graph.get_node("Prompt").state == ArtifactState.STALE
        assert graph.get_node("Image").state == ArtifactState.STALE

    def test_scenario_5_multiple_rollbacks(self, vg):
        """
        Scenario 5: Multiple Rollbacks
        V1 -> V2 -> V3 -> Rollback V1 -> V4 -> Rollback V2 -> V5
        Verify history timeline remains V1, V2, V3, V4, V5 without history deletion.
        """
        vg.record_version("node-01", {"v": 1}, {})
        vg.record_version("node-01", {"v": 2}, {})
        vg.record_version("node-01", {"v": 3}, {})

        v4 = vg.rollback("node-01", 1)  # V4 data = V1 data
        v5 = vg.rollback("node-01", 2)  # V5 data = V2 data

        assert v4.version_number == 4
        assert v4.rollback_of == 1
        assert v4.data_snapshot["v"] == 1

        assert v5.version_number == 5
        assert v5.rollback_of == 2
        assert v5.data_snapshot["v"] == 2

        history = vg.get_history("node-01")
        assert len(history) == 5
        assert [v.version_number for v in history] == [1, 2, 3, 4, 5]

    def test_scenario_6_rollback_latest_version_policy(self, vg):
        """
        Scenario 6: Rollback Latest Version Policy.
        Rollback V3 -> V3: Target version is already current HEAD.
        Preferred policy: No-op return current HEAD without appending redundant version.
        """
        vg.record_version("node-01", {"v": 1}, {})
        vg.record_version("node-01", {"v": 2}, {})
        vg.record_version("node-01", {"v": 3}, {})

        res = vg.rollback("node-01", 3)

        assert res.version_number == 3
        assert len(vg.get_history("node-01")) == 3
