from typing import List

from pydantic import BaseModel, Field


class PanelDescription(BaseModel):
    panel_number: int = Field(description="Sequential panel number within the scene")
    setting_details: str = Field(description="Specific visual details of the background/setting")
    action: str = Field(description="What is happening visually in the panel")
    characters_present: List[str] = Field(description="List of character IDs present in this panel")
    camera_angle: str = Field(
        description="Suggested camera angle (e.g., Close-up, Wide shot, Dutch angle)"
    )


class SceneScript(BaseModel):
    scene_id: str = Field(description="Unique identifier for this scene")
    beat_id: str = Field(description="The story beat this scene belongs to")
    location: str = Field(description="Primary location of the scene")
    time_of_day: str = Field(description="Time of day (e.g., Day, Night, Twilight)")
    panels: List[PanelDescription] = Field(
        description="Ordered list of panels making up the scene", default_factory=list
    )
