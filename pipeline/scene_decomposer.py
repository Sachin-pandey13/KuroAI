import random
import yaml
from pathlib import Path


STYLE_PATH = Path("configs/visual_style.yaml")


class SceneDecomposer:
    def __init__(self):
        with open(STYLE_PATH, "r") as f:
            self.style = yaml.safe_load(f)

    def decompose(self, scene: dict) -> dict:
        camera = random.choice(self.style["camera_angles"])
        lighting = random.choice(self.style["lighting"])

        positive_prompt = (
            f"{scene['visual_prompt']}, "
            f"{self.style['base_style']['description']}, "
            f"{self.style['base_style']['linework']}, "
            f"{self.style['base_style']['shading']}, "
            f"{camera}, {lighting}"
        )

        return {
            "scene_id": scene["scene_id"],
            "positive_prompt": positive_prompt,
            "negative_prompt": ", ".join(self.style["negative_prompt"]),
            "camera": camera,
            "lighting": lighting,
            "style_anchor": self.style["style_anchor"]
        }
