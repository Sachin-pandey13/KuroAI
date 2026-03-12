# pipeline/prompt_composer.py

class PromptComposer:
    def __init__(self):
        self.emotion_map = {
            "loneliness": "isolated subject, empty environment, distant framing, solitude atmosphere",
            "sadness": "downcast posture, melancholic mood, soft shadows",
            "anger": "tense posture, sharp contrast lighting, dramatic shadows",
            "determination": "strong stance, forward motion, dynamic composition",
            "fear": "dramatic lighting, heavy shadows, tense atmosphere",
            "hope": "soft glow lighting, upward gaze, gentle contrast"
        }

        self.camera_map = {
            "wide angle": "cinematic wide shot, subject small in frame",
            "close up": "close-up shot, facial focus",
            "medium shot": "medium framing, character centered",
            "low angle": "low angle shot, powerful perspective",
            "high angle": "high angle shot, vulnerability perspective"
        }

        self.lighting_map = {
            "neon": "cyberpunk neon lighting, glowing reflections",
            "neon rain": "neon lighting, rain reflections, wet streets",
            "dim": "low light, ambient shadows",
            "dramatic": "high contrast lighting, cinematic shadows",
            "soft": "soft diffused lighting"
        }

        # Style always last for consistency
        self.global_style = (
            "black and white manga style, clean lineart, detailed ink shading, "
            "cinematic composition, high quality"
        )

        self.negative_prompt = (
            "low quality, blurry, distorted anatomy, extra limbs, bad hands, "
            "watermark, text, logo, cropped, deformed face"
        )

    def compose(self, scene: dict) -> dict:
        emotion_tokens = self.emotion_map.get(
            scene.get("emotion", "").lower(),
            ""
        )

        camera_tokens = self.camera_map.get(
            scene.get("camera", "").lower(),
            ""
        )

        lighting_tokens = self.lighting_map.get(
            scene.get("lighting", "").lower(),
            scene.get("lighting", "")
        )

        base_visual = scene.get("visual_prompt", "")
        description = scene.get("description", "")

        # Order matters for stability:
        # 1. Base visual description
        # 2. Scene description
        # 3. Emotion
        # 4. Camera
        # 5. Lighting
        # 6. Global style

        prompt = ", ".join(
            filter(None, [
                base_visual,
                description,
                emotion_tokens,
                camera_tokens,
                lighting_tokens,
                self.global_style
            ])
        )

        return {
            "prompt": prompt,
            "negative_prompt": self.negative_prompt
        }