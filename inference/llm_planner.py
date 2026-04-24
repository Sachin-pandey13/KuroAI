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

Convert the story idea into **4 sequential manga panels** that advance the story.

CRITICAL RULES:
- Each scene must represent the **next event** in the story.
- Scenes must **progress the narrative**.
- Do NOT refine the same character pose across scenes.
- Each panel should show **new actions or characters**.
- Focus on storytelling like a comic panel sequence.

Return STRICT JSON only.

JSON format:
{{
  "title": "",
  "scenes": [
    {{
      "scene_id": 1,
      "emotion": "",
      "camera": "",
      "lighting": "",
      "visual_prompt": "",
      "dialogue": [
        {{
          "speaker": "",
          "text": ""
        }}
      ]
    }}
  ]
}}

Example progression:

Scene 1:
A lone samurai stands in a neon cyberpunk street at night.

Scene 2:
A masked villain approaches the samurai from the shadows saying
"I'm going to kill you."

Scene 3:
The samurai throws a powerful punch at the villain.

Scene 4:
The villain collapses onto the wet neon-lit pavement.

Story idea:
{idea}
"""

        response = self.client.chat.completions.create(
            model="mistral",
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6
        )

        content = response.choices[0].message.content

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("⚠ Invalid JSON returned by LLM:")
            print(content)
            raise