from pipeline.prompt_composer import PromptComposer
from inference.stability_image_adapter import StabilityImageAdapter
from inference.character_adapter import CharacterManager
from PIL import Image


class ImageGenerator:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        self.prompt_composer = PromptComposer()
        self.image_adapter = StabilityImageAdapter()
        self.character_manager = CharacterManager()

    def generate(self, scene: dict) -> Image.Image:
        """
        Expected scene format:

        {
            "character": {
                "name": "Ryu",
                "hair": "short messy black hair",
                "eyes": "sharp dark eyes",
                "build": "lean athletic build",
                "face_shape": "defined jawline"
            },
            "description": "standing in heavy rain, dramatic lighting"
        }
        """

        # 1️⃣ Extract character data
        character_data = scene.get("character")

        if not character_data:
            raise ValueError("Scene must contain 'character' field.")

        name = character_data["name"]

        # 2️⃣ Register character (assign seed if first time)
        self.character_manager.register(character_data)

        # 3️⃣ Get deterministic seed
        seed = self.character_manager.get_seed(name)

        # 4️⃣ Build identity prompt block
        identity_block = self.character_manager.get_prompt_block(name)

        # 5️⃣ Compose scene-specific prompt
        prompt_data = self.prompt_composer.compose(scene)
        scene_prompt = prompt_data["prompt"]

        # 6️⃣ Merge identity + scene
        full_prompt = f"{identity_block}, {scene_prompt}"

        # 7️⃣ Generate image with fixed seed
        image = self.image_adapter.generate(
            full_prompt,
            seed=seed
        )

        return image