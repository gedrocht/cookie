import torch
from diffusers import StableDiffusionPipeline

# Load the Stable Diffusion v1.4 model with memory optimizations
pipe = StableDiffusionPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4",
    torch_dtype=torch.float16  # Use float16 precision to reduce memory usage
)

# Move the model to the GPU
pipe = pipe.to("cuda")

# Optional: Enable gradient checkpointing if memory is tight
# pipe.enable_gradient_checkpointing()

# Define your prompt
prompt = "A beautiful landscape with sunset colors"

# Generate an image and save it
image = pipe(prompt).images[0]
image.save("output_image.png")

print("Image generated and saved as output_image.png")

