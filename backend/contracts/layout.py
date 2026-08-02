from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class PanelImportance(str, Enum):
    KEY_REVEAL = "KEY_REVEAL"  # Major dramatic focus / full-width
    ESTABLISHING = "ESTABLISHING"  # Setting establishing shot
    ACTION = "ACTION"  # High-energy action sequence
    DIALOGUE = "DIALOGUE"  # Standard conversation beat
    REACTION = "REACTION"  # Close-up reaction


class RelativePosition(str, Enum):
    TOP_FULL = "TOP_FULL"
    TOP_LEFT = "TOP_LEFT"
    TOP_RIGHT = "TOP_RIGHT"
    MID_LEFT = "MID_LEFT"
    MID_RIGHT = "MID_RIGHT"
    MID_FULL = "MID_FULL"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"
    BOTTOM_FULL = "BOTTOM_FULL"
    SPLASH_FULL = "SPLASH_FULL"


class SemanticPanelSlot(BaseModel):
    slot_id: str = Field(description="Unique identifier for this panel slot")
    panel_number: int = Field(description="Sequential panel number on the page")
    importance: PanelImportance = Field(description="Semantic storytelling weight")
    shot_type: str = Field(description="Close-up, Medium shot, Wide shot, Dutch angle, etc.")
    relative_position: RelativePosition = Field(
        description="Semantic positioning on page layout grid"
    )
    aspect_ratio_suggestion: str = Field(description="E.g., 16:9, 1:1, 4:3, 9:16 vertical splash")
    visual_description: str = Field(description="Action/framing summary for renderer guidance")


class MangaPageLayout(BaseModel):
    page_number: int = Field(description="Page index within the chapter/volume")
    total_panels: int = Field(description="Total panels on this page")
    grid_style: str = Field(description="E.g., DYNAMIC_ACTION, CONVERSATIONAL_2X2, FULL_SPLASH")
    slots: List[SemanticPanelSlot] = Field(
        default_factory=list, description="Ordered semantic panel specifications"
    )
