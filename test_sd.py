import torch
from diffusers import StableDiffusionPipeline

MODEL_PATH = "models/sd15/model.safetensors"

pipe = StableDiffusionPipeline.from_single_file(
    MODEL_PATH,
    torch_dtype=torch.float16
).to("cuda")

pipe.enable_attention_slicing()

prompt = """
black and white manga panel,
young athletic male character taking mirror selfie,
lean muscular build,
phone covering face,
standing in tiled indoor room,
bathroom setting,
dramatic shadows,
detailed ink shading,
clean line art,
high contrast lighting,
professional manga style
"""

image = pipe(
    prompt,
    num_inference_steps=30,
    guidance_scale=7.5
).images[0]

image.save("test_output.png")
print("Image saved as test_output.png")