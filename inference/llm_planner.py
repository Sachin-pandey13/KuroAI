from openai import OpenAI
import json

class StoryPlannerLLM:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://127.0.0.1:11434/v1",
            api_key="ollama"
        )

    def generate_story_plan(self, idea: str) -> dict:
        prompt = f"""
You are a professional manga storyboard director.

Convert the story idea into exactly **4 sequential manga scenes** (Scene 1, Scene 2, Scene 3, Scene 4).

CRITICAL RULES:
- Each scene must represent the next sequential event in the story.
- Scenes must progress the narrative dynamically.
- Each scene must have a visual description for image generation and dialogue.
- Dialogue MUST be an array of objects, containing "speaker" and "text" keys. Never return an empty string for dialogue. If no one speaks in a scene, add a narrator dialogue (e.g. speaker: "Narrator", text: "...").
- Maintain character consistency: name the protagonist "Akira" and antagonist "Gorath" (if applicable), or specify clear character names.

Return STRICT JSON only. Do not wrap in markdown or add explanations.

JSON structure:
{{
  "title": "A short descriptive title of the story",
  "scenes": [
    {{
      "scene_id": 1,
      "emotion": "determination",
      "camera": "medium shot",
      "lighting": "dramatic",
      "visual_prompt": "Akira, a brave warrior with messy black hair, sharp dark eyes, and a red scarf, unsheathes his sword as wind blows dust around him.",
      "dialogue": [
        {{
          "speaker": "Akira",
          "text": "This ends today, Gorath!"
        }}
      ]
    }},
    {{
      "scene_id": 2,
      "emotion": "fear",
      "camera": "close up",
      "lighting": "neon",
      "visual_prompt": "Gorath, the huge armored villain with glowing red eyes, smiles maliciously from the shadows.",
      "dialogue": [
        {{
          "speaker": "Gorath",
          "text": "You are foolish to challenge me."
        }}
      ]
    }},
    {{
      "scene_id": 3,
      "emotion": "battle",
      "camera": "wide angle",
      "lighting": "dramatic",
      "visual_prompt": "Akira with messy black hair and red scarf clashes swords with Gorath in a high-voltage spark-flying sword battle.",
      "dialogue": [
        {{
          "speaker": "Narrator",
          "text": "The clash of steel echoes through the desolate neon valley."
        }}
      ]
    }},
    {{
      "scene_id": 4,
      "emotion": "victory",
      "camera": "wide angle",
      "lighting": "soft",
      "visual_prompt": "Akira stands victorious looking at the horizon, his red scarf fluttering, while Gorath lies defeated on the ground.",
      "dialogue": [
        {{
          "speaker": "Akira",
          "text": "The valley is safe once more."
        }}
      ]
    }}
  ]
}}

Story idea:
{idea}
"""

        response = self.client.chat.completions.create(
            model="mistral",
            messages=[
                {"role": "system", "content": "You output strict, valid JSON only. Do not include markdown codeblocks or any text other than the raw JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        content = response.choices[0].message.content.strip()

        # Clean markdown code blocks if present
        if content.startswith("```"):
            # find first newline and last ```
            first_newline = content.find("\n")
            last_backtick = content.rfind("```")
            if first_newline != -1 and last_backtick != -1:
                content = content[first_newline:last_backtick].strip()
            elif content.startswith("```json"):
                content = content[7:].strip()
            elif content.startswith("```"):
                content = content[3:].strip()
            if content.endswith("```"):
                content = content[:-3].strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON returned by LLM:")
            print(content)
            # Try a basic cleanup of trailing commas or unmatched brackets if simple
            raise