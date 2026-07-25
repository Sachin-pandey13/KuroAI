# pipeline/prompt_composer.py

class PromptComposer:

    def __init__(self):

        # Character identity anchors
        self.hero_identity = (
            "Akira, lean anime fighter, messy black hair, sharp eyes, red scarf"
        )

        self.villain_identity = (
            "Gorath, huge armored villain, bulky body, dark armor, glowing red eyes"
        )

        self.emotion_map = {
            "loneliness": "isolated atmosphere",
            "sadness": "melancholic mood",
            "anger": "aggressive stance",
            "determination": "confident stance",
            "fear": "tense atmosphere",
            "hope": "calm confident mood",
            "battle": "dynamic action scene"
        }

        self.camera_map = {
            "wide angle": "wide cinematic shot showing full environment",
            "medium shot": "mid shot showing characters and surroundings",
            "close up": "close-up facial detail",
            "low angle": "low angle cinematic shot",
            "high angle": "high angle cinematic shot"
        }

        self.lighting_map = {
            "neon": "cyberpunk neon lighting",
            "dim": "dim dramatic lighting",
            "dramatic": "high contrast cinematic lighting",
            "soft": "soft lighting"
        }

        self.global_style = (
            "manga panel composition, black and white manga style, "
            "clean ink lineart, detailed shading, cinematic composition"
        )

        self.negative_prompt = (
            "low quality, blurry, distorted anatomy, extra limbs, bad hands, "
            "watermark, text, logo"
        )

    def compose(self, scene: dict) -> dict:

        base_visual = scene.get("visual_prompt", "")
        description = scene.get("description", "")

        emotion_tokens = self.emotion_map.get(
            scene.get("emotion", "").lower(), ""
        )

        camera_tokens = self.camera_map.get(
            scene.get("camera", "").lower(), "wide cinematic shot"
        )

        lighting_tokens = self.lighting_map.get(
            scene.get("lighting", "").lower(), ""
        )

        # Detect character dynamic data
        villain_data = scene.get("villain")
        if villain_data:
            villain_name = villain_data.get("name", "Gorath")
            villain_desc = f"{villain_name}, {villain_data.get('build', '')}, {villain_data.get('eyes', '')}"
        else:
            villain_desc = self.villain_identity

        visual_lower = base_visual.lower()
        character_action_block = ""
        if "gorath" in visual_lower or "villain" in visual_lower or "fight" in visual_lower or "battle" in visual_lower or "clash" in visual_lower:
            character_action_block = f"fighting {villain_desc}, both characters visible"
            camera_tokens = "wide cinematic shot, full body action scene"

        prompt_parts = [
            character_action_block,
            base_visual,
            description,
            emotion_tokens,
            camera_tokens,
            lighting_tokens,
            self.global_style
        ]

        prompt = ", ".join(filter(None, prompt_parts))

        return {
            "prompt": prompt,
            "negative_prompt": self.negative_prompt
        }