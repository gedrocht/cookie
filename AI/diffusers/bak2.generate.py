import torch
from diffusers import StableDiffusionPipeline
import time

# Load the model
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    torch_dtype=torch.float16
).to("cuda")

# Disable the NSFW filter
def dummy(images, **kwargs):
    return images, [False] * len(images)

pipe.safety_checker = dummy

# Define your prompt
# prompt = "A beautiful landscape with sunset colors"
# prompt = "a highly detailed, explicit scene featuring a vagina, photorealistic, soft lighting"
# prompt = "nsfw, porn, sex, a man thrusting his penis into an attractive nude woman from behind, his hands gripping her torso, her face flushed as she moans in pleasure, sensual, intimate setting, highly detailed, photorealistic"
prompt = "penis ejaculating cum, highly detailed, photorealistic"

filename = prompt.replace(" ","_").replace(",","").replace(".","")

for i in range(0,32):
   # Generate an image
   image = pipe(prompt).images[0]
   image.save(f"{filename}_{int(time.time())}.png")
