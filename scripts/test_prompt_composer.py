from pipeline.prompt_composer import PromptComposer

scene = {
    "emotion": "loneliness",
    "camera": "wide angle",
    "lighting": "neon rain",
    "visual_prompt": "a young boy standing alone in a futuristic city street at night"
}

composer = PromptComposer()
result = composer.compose(scene)

print("PROMPT:\n", result["prompt"])
print("\nNEGATIVE:\n", result["negative_prompt"])
