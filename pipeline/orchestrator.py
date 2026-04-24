from inference.llm_planner import StoryPlannerLLM
from pipeline.scene_decomposer import SceneDecomposer
from pipeline.page_composer import PageComposer
from inference.image_generator import ImageGenerator
from pipeline.manga_renderer import MangaRenderer
import base64
from io import BytesIO


class KuroAIOrchestrator:
    def __init__(self):
        self.planner = StoryPlannerLLM()
        self.decomposer = SceneDecomposer()
        self.composer = PageComposer(panels_per_page=3)
        self.generator = ImageGenerator(output_dir="outputs")
        self.renderer = MangaRenderer()

    def run(self, idea: str):

        # 1. Generate story plan
        story = self.planner.generate_story_plan(idea)

        # 2. Ensure character consistency
        main_character = {
            "name": "Akira",
            "hair": "messy black hair",
            "eyes": "sharp dark eyes",
            "build": "lean athletic fighter",
            "face_shape": "defined jawline",
            "scarf": "red scarf"
        }

        villain_character = {
            "name": "Gorath",
            "build": "huge armored body",
            "eyes": "glowing red eyes",
            "armor": "heavy battle armor"
        }

        for scene in story.get("scenes", []):

            # attach hero
            if "character" not in scene:
                scene["character"] = main_character

            # attach villain if scene mentions enemy
            visual = scene.get("visual_prompt", "").lower()

            if any(k in visual for k in ["villain", "enemy", "fight", "battle", "kick", "attack"]):
                scene["villain"] = villain_character

        # 3. Scene decomposition
        decomposed = [
            self.decomposer.decompose(scene)
            for scene in story.get("scenes", [])
        ]

        # 4. Panel layout
        pages = self.composer.compose(decomposed)

        # 5. Generate images
        images = []

        for idx, (panel, orig_scene) in enumerate(zip(pages, story.get("scenes", []))):

            panel["character"] = orig_scene["character"]

            if "villain" in orig_scene:
                panel["villain"] = orig_scene["villain"]

            # DEBUG: show prompt used
            print("\n-----------------------------")
            print(f"SCENE {idx}")
            print("VISUAL PROMPT:")
            print(panel.get("visual_prompt", ""))
            print("-----------------------------\n")

            img = self.generator.generate(panel)

            images.append(img)

        # 6. Convert images to base64 for frontend
        base64_images = []

        for img in images:
            buffered = BytesIO()
            img.save(buffered, format="PNG")

            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            base64_images.append(f"data:image/png;base64,{img_str}")

        return {
            "title": story.get("title", idea[:20]),
            "images": base64_images,
            "scenes": story.get("scenes", [])
        }