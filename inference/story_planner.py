import json
from jsonschema import validate
from pathlib import Path


SCHEMA_PATH = Path("configs/story_schema.json")


class StoryPlanner:
    def __init__(self):
        with open(SCHEMA_PATH, "r") as f:
            self.schema = json.load(f)

    def _infer_genre(self, idea: str) -> str:
        idea_l = idea.lower()
        if any(k in idea_l for k in ["cyber", "neon", "future"]):
            return "Cyberpunk"
        if any(k in idea_l for k in ["revenge", "dark", "betrayal"]):
            return "Dark Drama"
        if any(k in idea_l for k in ["romance", "love"]):
            return "Romance"
        return "Action"

    def _default_characters(self, genre: str):
        return [
            {
                "name": "Akira",
                "role": "Protagonist",
                "description": f"A determined lead shaped by the harsh realities of a {genre.lower()} world."
            },
            {
                "name": "Raven",
                "role": "Antagonist",
                "description": "A shadowy figure whose motives drive the central conflict."
            }
        ]

    def _scene_templates(self, genre: str):
        return [
            {
                "scene_id": 1,
                "setting": "Rain-soaked city streets at night",
                "action": "The protagonist observes the city from a rooftop.",
                "emotion": "Brooding",
                "visual_prompt": f"{genre.lower()} manga style, night city, rain, dramatic lighting"
            },
            {
                "scene_id": 2,
                "setting": "Abandoned industrial district",
                "action": "A confrontation with the antagonist begins.",
                "emotion": "Tension",
                "visual_prompt": f"{genre.lower()} manga style, confrontation, high contrast shadows"
            },
            {
                "scene_id": 3,
                "setting": "Neon-lit alleyway",
                "action": "The truth behind the conflict is revealed.",
                "emotion": "Shock",
                "visual_prompt": f"{genre.lower()} manga style, neon lights, intense expressions"
            }
        ]

    def generate(self, idea: str) -> dict:
        genre = self._infer_genre(idea)

        story = {
            "title": f"{genre} Tale",
            "genre": genre,
            "characters": self._default_characters(genre),
            "scenes": self._scene_templates(genre)
        }

        # Validate against schema (critical)
        validate(instance=story, schema=self.schema)
        return story
