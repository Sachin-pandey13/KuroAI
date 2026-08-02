import sys

try:
    from pipeline.prompt_composer import PromptComposer
except ImportError:
    PromptComposer = None  # type: ignore[assignment, misc]

if PromptComposer is None:
    print("Error: Legacy pipeline.prompt_composer module is unavailable in this environment.")
    sys.exit(1)

scene = {
    "emotion": "loneliness",
    "camera": "wide angle",
    "lighting": "neon rain",
    "visual_prompt": "a young boy standing alone in a futuristic city street at night",
}

composer = PromptComposer()
result = composer.compose(scene)

print("PROMPT:\n", result["prompt"])
print("\nNEGATIVE:\n", result["negative_prompt"])
