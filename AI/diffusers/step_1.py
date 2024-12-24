import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16
).to("cuda")

# Define the initial prompt
initial_prompt = "a man gently holding an attractive, nude woman from behind, softly kissing her shoulder, with his hands resting on her torso, warm lighting, intimate setting, highly detailed, photorealistic"

# Generate the initial image
initial_image = pipe(initial_prompt).images[0]
initial_image.save("initial_image.png")

