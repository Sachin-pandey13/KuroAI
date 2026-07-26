from typing import List, Optional
from pydantic import BaseModel, Field

class StoryBeat(BaseModel):
    beat_id: str = Field(description="Unique identifier for this beat")
    title: str = Field(description="Short title for the beat")
    summary: str = Field(description="Detailed narrative summary of what happens in this beat")
    emotional_arc: str = Field(description="The emotional shift or tone of this beat")
    setting: str = Field(description="The primary location for this beat")

class StoryOutline(BaseModel):
    project_id: str
    title: str = Field(description="Working title of the story")
    logline: str = Field(description="One sentence summary of the story")
    beats: List[StoryBeat] = Field(description="Chronological list of story beats", default_factory=list)
