from openai import OpenAI
import json


class StoryPlannerLLM:
    def __init__(self):
        self.client = OpenAI(
            base_url="http://127.0.0.1:1234/v1",
            api_key="lm-studio"
        )

    def generate_story_plan(self, idea: str) -> dict:
        prompt = f"""
You are an AI director for a manga generation system.

Return ONLY valid JSON.
No markdown.
No explanation.

JSON format:
{{
  "title": "",
  "scenes": [
    {{
      "scene_id": 1,
      "emotion": "",
      "camera": "",
      "lighting": "",
      "visual_prompt": ""
    }}
  ]
}}

Idea:
{idea}
"""

        response = self.client.chat.completions.create(
            model="phi-3-medium-4k-instruct",
            messages=[
                {"role": "system", "content": "You output strict JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return json.loads(response.choices[0].message.content)
