# inference/character_adapter.py

from typing import Dict


class CharacterManager:
    def __init__(self):
        self.characters: Dict[str, dict] = {}

    def register(self, char_data: dict):
        name = char_data["name"]

        if name not in self.characters:
            seed = abs(hash(name)) % 10_000_000

            self.characters[name] = {
                "descriptor": char_data,
                "seed": seed
            }

    def get_seed(self, name: str) -> int:
        return self.characters[name]["seed"]

    def get_prompt_block(self, name: str) -> str:
        c = self.characters[name]["descriptor"]

        return (
            f"{c['name']}, "
            f"{c.get('hair', '')}, "
            f"{c.get('eyes', '')}, "
            f"{c.get('build', '')}, "
            f"{c.get('face_shape', '')}"
        )