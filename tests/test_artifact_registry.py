"""
Test: Artifact Registry (Milestone 2)
Validates that the ArtifactRegistry correctly owns artifact lifecycle:
register, get, exists, update_metadata, update_data, update_status,
list_by_type, list_by_project, remove, and error handling.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from backend.engine.artifact_registry import (
    ArtifactRegistry,
    ArtifactNotFoundError,
    ArtifactAlreadyExistsError,
)
from backend.contracts.artifact import Artifact, ArtifactType, ArtifactStatus


@pytest.fixture
def registry() -> ArtifactRegistry:
    return ArtifactRegistry()


@pytest.fixture
def sample_character(registry: ArtifactRegistry) -> Artifact:
    artifact = Artifact(
        project_id="proj-001",
        artifact_type=ArtifactType.CHARACTER_PROFILE,
        owner_agent="character_agent",
        data={"name": "Kuro", "hair": "black", "eyes": "red"},
    )
    return artifact


@pytest.fixture
def sample_story(registry: ArtifactRegistry) -> Artifact:
    return Artifact(
        project_id="proj-001",
        artifact_type=ArtifactType.STORY_OUTLINE,
        owner_agent="story_agent",
        data={"title": "Chapter 1", "beats": ["intro", "conflict", "resolution"]},
    )


class TestRegister:
    def test_register_returns_id(self, registry, sample_character):
        artifact_id = registry.register(sample_character)
        assert artifact_id == sample_character.artifact_id

    def test_register_stores_artifact(self, registry, sample_character):
        registry.register(sample_character)
        assert registry.count == 1

    def test_register_duplicate_raises(self, registry, sample_character):
        registry.register(sample_character)
        with pytest.raises(ArtifactAlreadyExistsError):
            registry.register(sample_character)


class TestGet:
    def test_get_returns_correct_artifact(self, registry, sample_character):
        registry.register(sample_character)
        result = registry.get(sample_character.artifact_id)
        assert result.data["name"] == "Kuro"

    def test_get_unknown_raises(self, registry):
        with pytest.raises(ArtifactNotFoundError):
            registry.get("nonexistent-id")


class TestExists:
    def test_exists_returns_true(self, registry, sample_character):
        registry.register(sample_character)
        assert registry.exists(sample_character.artifact_id) is True

    def test_exists_returns_false(self, registry):
        assert registry.exists("nonexistent-id") is False


class TestUpdateMetadata:
    def test_update_metadata_merges(self, registry, sample_character):
        registry.register(sample_character)
        registry.update_metadata(sample_character.artifact_id, {"style": "manga", "mood": "dark"})
        artifact = registry.get(sample_character.artifact_id)
        assert artifact.metadata["style"] == "manga"
        assert artifact.metadata["mood"] == "dark"

    def test_update_metadata_preserves_existing(self, registry, sample_character):
        sample_character.metadata = {"existing_key": "value"}
        registry.register(sample_character)
        registry.update_metadata(sample_character.artifact_id, {"new_key": "new_value"})
        artifact = registry.get(sample_character.artifact_id)
        assert artifact.metadata["existing_key"] == "value"
        assert artifact.metadata["new_key"] == "new_value"

    def test_update_metadata_unknown_raises(self, registry):
        with pytest.raises(ArtifactNotFoundError):
            registry.update_metadata("nonexistent-id", {"key": "val"})


class TestUpdateData:
    def test_update_data_merges(self, registry, sample_character):
        registry.register(sample_character)
        registry.update_data(sample_character.artifact_id, {"hair": "white"})
        artifact = registry.get(sample_character.artifact_id)
        assert artifact.data["hair"] == "white"
        assert artifact.data["name"] == "Kuro"  # preserved


class TestUpdateStatus:
    def test_update_status(self, registry, sample_character):
        registry.register(sample_character)
        assert sample_character.status == ArtifactStatus.DRAFT
        registry.update_status(sample_character.artifact_id, ArtifactStatus.ACTIVE)
        artifact = registry.get(sample_character.artifact_id)
        assert artifact.status == ArtifactStatus.ACTIVE


class TestListByType:
    def test_list_by_type_filters_correctly(self, registry, sample_character, sample_story):
        registry.register(sample_character)
        registry.register(sample_story)
        characters = registry.list_by_type(ArtifactType.CHARACTER_PROFILE)
        stories = registry.list_by_type(ArtifactType.STORY_OUTLINE)
        assert len(characters) == 1
        assert len(stories) == 1
        assert characters[0].data["name"] == "Kuro"

    def test_list_by_type_empty(self, registry):
        result = registry.list_by_type(ArtifactType.GENERATED_IMAGE)
        assert result == []


class TestListByProject:
    def test_list_by_project(self, registry, sample_character, sample_story):
        registry.register(sample_character)
        registry.register(sample_story)
        results = registry.list_by_project("proj-001")
        assert len(results) == 2

    def test_list_by_project_empty(self, registry):
        results = registry.list_by_project("nonexistent-project")
        assert results == []


class TestRemove:
    def test_remove_returns_artifact(self, registry, sample_character):
        registry.register(sample_character)
        removed = registry.remove(sample_character.artifact_id)
        assert removed.artifact_id == sample_character.artifact_id
        assert registry.count == 0

    def test_remove_unknown_raises(self, registry):
        with pytest.raises(ArtifactNotFoundError):
            registry.remove("nonexistent-id")

    def test_remove_then_get_raises(self, registry, sample_character):
        registry.register(sample_character)
        registry.remove(sample_character.artifact_id)
        with pytest.raises(ArtifactNotFoundError):
            registry.get(sample_character.artifact_id)
