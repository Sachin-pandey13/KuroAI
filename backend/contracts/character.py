from typing import List

from pydantic import BaseModel, Field


class CharacterAppearance(BaseModel):
    hair: str = Field(description="Hair style and color")
    eyes: str = Field(description="Eye color and shape")
    build: str = Field(description="Physical body build and height")
    clothing: str = Field(description="Typical attire or specific outfit for this arc")
    distinguishing_features: str = Field(description="Scars, tattoos, or notable accessories")


class CharacterRelationship(BaseModel):
    target_character_id: str = Field(description="ID of the character this relates to")
    relationship_type: str = Field(description="E.g., Ally, Enemy, Sibling, Mentor")
    dynamic: str = Field(description="Brief description of how they interact")


class CharacterProfile(BaseModel):
    character_id: str = Field(description="Unique identifier for this character")
    name: str = Field(description="Full name of the character")
    age: str = Field(description="Approximate age")
    role: str = Field(description="Narrative role (Protagonist, Antagonist, Supporting, etc.)")
    personality: str = Field(description="Key personality traits and flaws")
    backstory: str = Field(description="Brief history of the character prior to the story")
    appearance: CharacterAppearance
    relationships: List[CharacterRelationship] = Field(default_factory=list)
