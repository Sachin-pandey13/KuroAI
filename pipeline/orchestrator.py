from inference.story_planner import StoryPlanner
from pipeline.scene_decomposer import SceneDecomposer
from pipeline.page_composer import PageComposer
from inference.image_generator import ImageGenerator


class KuroAIOrchestrator:
    def __init__(self):
        self.planner = StoryPlanner()
        self.decomposer = SceneDecomposer()
        self.composer = PageComposer(panels_per_page=3)
        self.generator = ImageGenerator(output_dir="outputs")

    def run(self, idea: str):
        story = self.planner.generate(idea)

        decomposed = [
            self.decomposer.decompose(scene)
            for scene in story["scenes"]
        ]

        pages = self.composer.compose(decomposed)

        images = [
            self.generator.generate(panel)
            for panel in pages
        ]

        return {
            "title": story["title"],
            "images": images
        }
