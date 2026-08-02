from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DialogueType(str, Enum):
    SPEECH = "SPEECH"
    THOUGHT = "THOUGHT"
    SHOUT = "SHOUT"
    WHISPER = "WHISPER"
    NARRATION = "NARRATION"


class SpeechBubble(BaseModel):
    bubble_id: str = Field(description="Unique identifier for this bubble")
    panel_number: int = Field(description="The panel this bubble belongs to")
    character_id: Optional[str] = Field(
        description="ID of the character speaking, None if Narration"
    )
    dialogue_type: DialogueType = Field(description="Type of bubble (Speech, Thought, etc.)")
    text: str = Field(description="The actual text content")
    emotion_tag: Optional[str] = Field(
        description="Underlying emotion driving this dialogue line (e.g., Angry, Sad, Neutral)",
        default=None,
    )


class SceneDialogue(BaseModel):
    scene_id: str = Field(description="The scene these speech bubbles belong to")
    bubbles: List[SpeechBubble] = Field(
        description="All speech bubbles in the scene, ordered chronologically", default_factory=list
    )
