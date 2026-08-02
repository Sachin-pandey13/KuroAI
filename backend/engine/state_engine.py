from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from backend.contracts.event import Event, EventType
from backend.contracts.goal import CreativeGoal, GoalStatus
from backend.contracts.project_state import AutonomyLevel, ProjectStateModel
from backend.engine.artifact_registry import ArtifactRegistry


class ProjectNotFoundError(Exception):
    """Raised when a project ID does not exist."""

    pass


class ArtifactNotRegisteredError(Exception):
    """Raised when attempting to attach an artifact that doesn't exist in the ArtifactRegistry."""

    pass


class ArtifactAlreadyAttachedError(Exception):
    """Raised when attempting to attach an artifact that is already referenced by the project."""

    pass


class ProjectStateEngine:
    """
    Project State Engine (Blackboard Core).
    Single Source of Truth for project state (Fourth Law).

    Owns project state and references to artifacts.
    Does NOT own artifact lifecycle — that belongs to ArtifactRegistry.

    Lifecycle:
        ArtifactRegistry.register(artifact) → artifact_id
        ProjectStateEngine.attach_artifact(artifact_id) → project references it
    """

    def __init__(
        self, artifact_registry: ArtifactRegistry, event_bus: Optional[Any] = None
    ) -> None:
        self._artifact_registry = artifact_registry
        self._event_bus = event_bus
        self._projects: Dict[str, ProjectStateModel] = {}
        self._active_project_id: Optional[str] = None
        # Track which artifact IDs are attached to each project
        self._project_artifacts: Dict[str, Set[str]] = {}

    def create_project(
        self, title: str, description: str, autonomy_level: AutonomyLevel = AutonomyLevel.GUIDED
    ) -> ProjectStateModel:
        """Initialize a new project state."""
        project = ProjectStateModel(
            title=title,
            description=description,
            autonomy_level=autonomy_level,
        )
        self._projects[project.project_id] = project
        self._project_artifacts[project.project_id] = set()
        self._active_project_id = project.project_id
        return project

    def get_project(self, project_id: str) -> ProjectStateModel:
        """Fetch a project by ID. Raises ProjectNotFoundError if missing."""
        if project_id not in self._projects:
            raise ProjectNotFoundError(f"Project '{project_id}' not found.")
        return self._projects[project_id]

    def get_state(self) -> ProjectStateModel:
        """Retrieve the current active project state."""
        if self._active_project_id is None:
            raise ProjectNotFoundError("No active project.")
        return self.get_project(self._active_project_id)

    def set_active_project(self, project_id: str) -> None:
        """Set the active project by ID."""
        if project_id not in self._projects:
            raise ProjectNotFoundError(f"Project '{project_id}' not found.")
        self._active_project_id = project_id

    def add_goal(self, goal: CreativeGoal) -> None:
        """Publish a new creative goal to the active project."""
        state = self.get_state()
        state.active_goals.append(goal)
        state.updated_at = datetime.utcnow()
        if self._event_bus:
            self._event_bus.publish(
                Event(
                    event_type=EventType.GOAL_PUBLISHED,
                    project_id=state.project_id,
                    payload={"goal_id": goal.goal_id, "title": goal.title},
                )
            )

    def update_goal_status(self, goal_id: str, status: GoalStatus) -> CreativeGoal:
        """Update the status of a goal in the active project."""
        state = self.get_state()
        for goal in state.active_goals:
            if goal.goal_id == goal_id:
                goal.status = status
                goal.updated_at = datetime.utcnow()
                state.updated_at = datetime.utcnow()
                if self._event_bus:
                    self._event_bus.publish(
                        Event(
                            event_type=EventType.GOAL_UPDATED,
                            project_id=state.project_id,
                            payload={
                                "goal_id": goal_id,
                                "status": status.value if hasattr(status, "value") else str(status),
                            },
                        )
                    )
                return goal
        raise ValueError(f"Goal '{goal_id}' not found in active project.")

    def attach_artifact(self, artifact_id: str) -> None:
        """
        Attach an artifact (by reference) to the active project.
        The artifact must already exist in the ArtifactRegistry.
        Raises ArtifactNotRegisteredError if the artifact isn't registered.
        Raises ArtifactAlreadyAttachedError if already attached.
        """
        state = self.get_state()

        # Validate the artifact exists in the registry
        if not self._artifact_registry.exists(artifact_id):
            raise ArtifactNotRegisteredError(
                f"Artifact '{artifact_id}' is not registered in the ArtifactRegistry. "
                f"Register it first before attaching to a project."
            )

        # Check for duplicate attachment
        if artifact_id in self._project_artifacts[state.project_id]:
            raise ArtifactAlreadyAttachedError(
                f"Artifact '{artifact_id}' is already attached to project '{state.project_id}'."
            )

        # Attach: store the reference and update the project state artifacts dict
        self._project_artifacts[state.project_id].add(artifact_id)
        artifact = self._artifact_registry.get(artifact_id)
        state.artifacts[artifact_id] = artifact
        state.updated_at = datetime.utcnow()

    def detach_artifact(self, artifact_id: str) -> None:
        """
        Remove an artifact reference from the active project.
        Does NOT delete the artifact from the registry.
        """
        state = self.get_state()
        if artifact_id not in self._project_artifacts[state.project_id]:
            raise ArtifactNotRegisteredError(
                f"Artifact '{artifact_id}' is not attached to project '{state.project_id}'."
            )
        self._project_artifacts[state.project_id].discard(artifact_id)
        state.artifacts.pop(artifact_id, None)
        state.updated_at = datetime.utcnow()

    def get_attached_artifact_ids(self) -> List[str]:
        """Return the list of artifact IDs attached to the active project."""
        state = self.get_state()
        return list(self._project_artifacts[state.project_id])

    def mutate_state(self, delta: Dict[str, Any]) -> None:
        """
        Apply a state delta mutation to the active project.
        Supports updating metadata, style_guidelines, and character_registry.
        """
        state = self.get_state()
        if "metadata" in delta:
            state.metadata.update(delta["metadata"])
        if "style_guidelines" in delta:
            state.style_guidelines.update(delta["style_guidelines"])
        if "character_registry" in delta:
            state.character_registry.update(delta["character_registry"])
        if "title" in delta:
            state.title = delta["title"]
        if "description" in delta:
            state.description = delta["description"]
        if "autonomy_level" in delta:
            state.autonomy_level = AutonomyLevel(delta["autonomy_level"])
        state.version += 1
        state.updated_at = datetime.utcnow()

        if self._event_bus:
            self._event_bus.publish(
                Event(
                    event_type=EventType.STATE_DELTA_MUTATED,
                    project_id=state.project_id,
                    payload={"version": state.version, "delta": delta},
                )
            )

    def register_listeners(self, bus: Any) -> None:
        """Register ProjectStateEngine reactions on the EventBus."""
        bus.subscribe(EventType.STATE_DELTA_MUTATED, self._on_state_mutated)

    def unregister_listeners(self, bus: Any) -> None:
        """Unregister ProjectStateEngine reactions from the EventBus."""
        bus.unsubscribe(EventType.STATE_DELTA_MUTATED, self._on_state_mutated)

    def _on_state_mutated(self, event: Event) -> None:
        """Observe state mutation events."""
        pass

    # --- Transaction Stubs ---

    def begin_transaction(self) -> None:
        """Begin an atomic state transaction."""
        pass

    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass

    @property
    def project_count(self) -> int:
        """Return total number of managed projects."""
        return len(self._projects)
