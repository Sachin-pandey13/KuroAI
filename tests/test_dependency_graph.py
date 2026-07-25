"""
Test: Dependency Graph & Selective Invalidation Engine (Milestone 3)
Verifies Stages 1-5: Node/Edge Integrity, Cycle Detection, Topological Sort,
Traversal, Selective Invalidation (First Law), Dirty Queries, and The Golden Test of KuroAI.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.engine.dependency_graph import (
    DependencyGraph,
    CycleDetectedError,
    NodeNotFoundError,
    EdgeNotFoundError,
)
from backend.contracts.dependency import DependencyNode, DependencyEdge, EdgeType
from backend.contracts.artifact import ArtifactState, ArtifactType


@pytest.fixture
def graph() -> DependencyGraph:
    return DependencyGraph()


# =====================================================================
# Stage 1 — Graph Structure & Integrity Tests
# =====================================================================

class TestGraphStructure:
    def test_add_node(self, graph):
        node = graph.create_node("art-001", "STORY_OUTLINE")
        assert graph.has_node("art-001")
        assert graph.node_count == 1

    def test_remove_node(self, graph):
        graph.create_node("art-001", "STORY_OUTLINE")
        graph.remove_node("art-001")
        assert not graph.has_node("art-001")
        assert graph.node_count == 0

    def test_remove_unknown_node_raises(self, graph):
        with pytest.raises(NodeNotFoundError):
            graph.remove_node("nonexistent-node")

    def test_add_edge(self, graph):
        graph.create_node("src", "STORY_OUTLINE")
        graph.create_node("tgt", "SCENE_SCRIPT")
        graph.connect("src", "tgt")
        assert graph.has_edge("src", "tgt")
        assert graph.edge_count == 1
        assert "tgt" in graph.get_downstream("src")
        assert "src" in graph.get_upstream("tgt")

    def test_remove_edge(self, graph):
        graph.create_node("src", "STORY_OUTLINE")
        graph.create_node("tgt", "SCENE_SCRIPT")
        graph.connect("src", "tgt")
        graph.remove_edge("src", "tgt")
        assert not graph.has_edge("src", "tgt")
        assert graph.edge_count == 0

    def test_clear_graph(self, graph):
        graph.create_node("src", "STORY_OUTLINE")
        graph.create_node("tgt", "SCENE_SCRIPT")
        graph.connect("src", "tgt")
        graph.clear()
        assert graph.node_count == 0
        assert graph.edge_count == 0


# =====================================================================
# Stage 2 — Validation & Topological Sort Tests
# =====================================================================

class TestValidationAndTopoSort:
    def test_simple_cycle_detection_raises(self, graph):
        """A -> B -> A raises CycleDetectedError immediately on add_edge."""
        graph.create_node("A", "STORY_OUTLINE")
        graph.create_node("B", "SCENE_SCRIPT")
        graph.connect("A", "B")
        with pytest.raises(CycleDetectedError):
            graph.connect("B", "A")

    def test_complex_cycle_detection_raises(self, graph):
        """A -> B -> C -> D -> A raises CycleDetectedError."""
        graph.create_node("A", "STORY_OUTLINE")
        graph.create_node("B", "SCENE_SCRIPT")
        graph.create_node("C", "PANEL_PROMPT")
        graph.create_node("D", "GENERATED_IMAGE")
        graph.connect("A", "B")
        graph.connect("B", "C")
        graph.connect("C", "D")
        with pytest.raises(CycleDetectedError):
            graph.connect("D", "A")

    def test_topological_sort_linear(self, graph):
        """Story -> Scene -> Prompt -> Image."""
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("Scene", "SCENE_SCRIPT")
        graph.create_node("Prompt", "PANEL_PROMPT")
        graph.create_node("Image", "GENERATED_IMAGE")

        graph.connect("Story", "Scene")
        graph.connect("Scene", "Prompt")
        graph.connect("Prompt", "Image")

        order = graph.topological_sort()
        assert order == ["Story", "Scene", "Prompt", "Image"]

    def test_topological_sort_diamond_dag(self, graph):
        """
        Story
        ├── CharA
        └── CharB
             └── Scene
        """
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("CharA", "CHARACTER_PROFILE")
        graph.create_node("CharB", "CHARACTER_PROFILE")
        graph.create_node("Scene", "SCENE_SCRIPT")

        graph.connect("Story", "CharA")
        graph.connect("Story", "CharB")
        graph.connect("CharA", "Scene")
        graph.connect("CharB", "Scene")

        order = graph.topological_sort()
        assert order.index("Story") < order.index("CharA")
        assert order.index("Story") < order.index("CharB")
        assert order.index("CharA") < order.index("Scene")
        assert order.index("CharB") < order.index("Scene")


# =====================================================================
# Stage 3 — Traversal & Ancestry Tests
# =====================================================================

class TestTraversalAndAncestry:
    @pytest.fixture
    def linear_chain(self, graph):
        graph.create_node("N1", "STORY")
        graph.create_node("N2", "SCENE")
        graph.create_node("N3", "PROMPT")
        graph.create_node("N4", "IMAGE")
        graph.connect("N1", "N2")
        graph.connect("N2", "N3")
        graph.connect("N3", "N4")
        return graph

    def test_get_upstream_downstream(self, linear_chain):
        assert linear_chain.get_upstream("N3") == ["N2"]
        assert linear_chain.get_downstream("N3") == ["N4"]

    def test_ancestors(self, linear_chain):
        ancestors = linear_chain.ancestors("N4")
        assert ancestors == {"N1", "N2", "N3"}

    def test_descendants(self, linear_chain):
        descendants = linear_chain.descendants("N1")
        assert descendants == {"N2", "N3", "N4"}


# =====================================================================
# Stage 4 & 5 — Selective Invalidation & Dirty Queries Tests
# =====================================================================

class TestSelectiveInvalidationAndDirtyQueries:
    def test_selective_invalidation(self, graph):
        graph.create_node("Story", "STORY")
        graph.create_node("Prompt", "PROMPT")
        graph.create_node("Image", "IMAGE")
        graph.connect("Story", "Prompt")
        graph.connect("Prompt", "Image")

        # Invalidate Prompt
        invalidated = graph.invalidate("Prompt", "Prompt edited")
        assert invalidated == {"Image"}

        assert graph.get_node("Story").state == ArtifactState.ACTIVE
        assert graph.get_node("Prompt").state == ArtifactState.ACTIVE  # Modified source
        assert graph.get_node("Image").state == ArtifactState.STALE  # Downstream dependent

    def test_dirty_queries(self, graph):
        graph.create_node("Story", "STORY")
        graph.create_node("Prompt", "PROMPT")
        graph.create_node("Image", "IMAGE")
        graph.connect("Story", "Prompt")
        graph.connect("Prompt", "Image")

        graph.invalidate("Story", "Story beats changed")
        dirty_nodes = graph.get_dirty()
        dirty_ids = [n.artifact_id for n in dirty_nodes]
        assert "Prompt" in dirty_ids
        assert "Image" in dirty_ids

        assert graph.is_dirty("Image") is True
        assert graph.is_dirty("Story") is False

        # Clear dirty
        graph.clear_dirty("Image")
        assert graph.is_dirty("Image") is False


# =====================================================================
# Behavioral Scenarios & The Golden Test of KuroAI
# =====================================================================

class TestBehavioralScenarios:

    def test_scenario_dialogue_edit(self, graph):
        """
        Story -> Dialogue -> Speech Bubbles -> Manga Page
        Story -> Character -> Image -> Manga Page

        Dialogue edit -> Speech Bubbles STALE, Images remain ACTIVE.
        """
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("Dialogue", "SCENE_SCRIPT")
        graph.create_node("Bubbles", "SPEECH_BUBBLE")
        graph.create_node("Character", "CHARACTER_PROFILE")
        graph.create_node("Image", "GENERATED_IMAGE")
        graph.create_node("Page", "MANGA_PAGE_LAYOUT")

        graph.connect("Story", "Dialogue")
        graph.connect("Dialogue", "Bubbles")
        graph.connect("Bubbles", "Page")

        graph.connect("Story", "Character")
        graph.connect("Character", "Image")
        graph.connect("Image", "Page")

        # Edit Dialogue
        invalidated = graph.invalidate("Dialogue", "Dialogue line revised")

        assert "Bubbles" in invalidated
        assert "Page" in invalidated
        assert "Image" not in invalidated

        assert graph.get_node("Image").state == ArtifactState.ACTIVE
        assert graph.get_node("Character").state == ArtifactState.ACTIVE
        assert graph.get_node("Bubbles").state == ArtifactState.STALE

    def test_scenario_delete_character(self, graph):
        """
        Delete Character -> All dependents become INVALID.
        """
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("Character", "CHARACTER_PROFILE")
        graph.create_node("Prompt", "PANEL_PROMPT")
        graph.create_node("Image", "GENERATED_IMAGE")

        graph.connect("Story", "Character")
        graph.connect("Character", "Prompt")
        graph.connect("Prompt", "Image")

        graph.remove_node("Character")

        assert not graph.has_node("Character")
        assert graph.get_node("Prompt").state == ArtifactState.INVALID
        assert graph.get_node("Image").state == ArtifactState.INVALID
        assert graph.get_node("Story").state == ArtifactState.ACTIVE

    def test_scenario_shared_dependencies(self, graph):
        """
        Character + WorldLore -> Prompt -> Image
        Multiple parents handled correctly.
        """
        graph.create_node("Char", "CHARACTER_PROFILE")
        graph.create_node("Lore", "WORLD_LORE")
        graph.create_node("Prompt", "PANEL_PROMPT")
        graph.create_node("Image", "GENERATED_IMAGE")

        graph.connect("Char", "Prompt")
        graph.connect("Lore", "Prompt")
        graph.connect("Prompt", "Image")

        invalidated = graph.invalidate("Lore", "Lore revised")
        assert invalidated == {"Prompt", "Image"}
        assert graph.get_node("Char").state == ArtifactState.ACTIVE

    def test_the_golden_test_of_kuroai(self, graph):
        """
        The Golden Test of KuroAI 2.0 (First Law Verification):
        Story
        ├── Dialogue
        └── Character
               └── Prompt
                      └── Image
                             └── Vision Review

        User changes Character hairstyle:
        Expected:
          Story: ACTIVE
          Dialogue: ACTIVE
          Character: ACTIVE (updated)
          Prompt: STALE
          Image: STALE
          Vision Review: STALE
        """
        graph.create_node("Story", "STORY_OUTLINE")
        graph.create_node("Dialogue", "SCENE_SCRIPT")
        graph.create_node("Character", "CHARACTER_PROFILE")
        graph.create_node("Prompt", "PANEL_PROMPT")
        graph.create_node("Image", "GENERATED_IMAGE")
        graph.create_node("VisionReview", "EXPORT_PDF")

        graph.connect("Story", "Dialogue")
        graph.connect("Story", "Character")
        graph.connect("Character", "Prompt")
        graph.connect("Prompt", "Image")
        graph.connect("Image", "VisionReview")

        # Human changes Character hairstyle
        invalidated = graph.invalidate("Character", "Hairstyle modified from spiky to ponytail")

        # Assert exact selective invalidation
        assert invalidated == {"Prompt", "Image", "VisionReview"}

        # Assert First Law properties
        assert graph.get_node("Story").state == ArtifactState.ACTIVE
        assert graph.get_node("Dialogue").state == ArtifactState.ACTIVE
        assert graph.get_node("Character").state == ArtifactState.ACTIVE

        assert graph.get_node("Prompt").state == ArtifactState.STALE
        assert graph.get_node("Image").state == ArtifactState.STALE
        assert graph.get_node("VisionReview").state == ArtifactState.STALE
