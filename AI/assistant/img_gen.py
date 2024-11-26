import torch
from huggingface_hub import login
from diffusers import StableDiffusionPipeline
from safetensors.torch import load_file

# Log in with your Hugging Face token to access the model repository
login("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")

# Check if a GPU is available and use it; otherwise, fallback to CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load model weights from a safetensor file
# This loads pre-trained model weights that will be used for inference
fp16_model = load_file("flux1-dev-fp8.safetensors")

# Load the Stable Diffusion pipeline with the appropriate precision settings
# Using float16 for GPU (memory optimization) or standard precision for CPU
pipe = StableDiffusionPipeline.from_pretrained(
    "black-forest-labs/FLUX.1-schnell", 
    torch_dtype=torch.float16,  # Use float16 for memory optimization if GPU is available
    revision="fp16" if device == "cuda" else "main"  # Use a specific model revision based on the device
)

# Move the model to the appropriate device (GPU or CPU)
pipe.to(device)

# Enable attention slicing to reduce memory usage during inference
# This is useful for reducing the VRAM needed by breaking the attention computation into smaller parts
pipe.enable_attention_slicing()

# Define the text prompt for image generation
prompt = "A cat hitting the griddy"

# Set a random seed for reproducibility, ensuring the same output each time
seed = 42

# Create a random number generator with the specified seed
# This generator will be used to ensure consistent results during inference
generator = torch.Generator(device).manual_seed(seed)

# Run inference with the model to generate an image
# Use automatic mixed precision (autocast) to optimize memory usage on the GPU
with torch.autocast("cuda"):  # Enable mixed precision for faster and more memory-efficient computation
    image = pipe(
        prompt,
        guidance_scale=7.5,  # Controls the strength of the guidance; higher values can lead to more precise adherence to the prompt
        num_inference_steps=50,  # Number of denoising steps; more steps generally lead to higher quality images
        generator=generator  # Use the predefined random generator for reproducibility
    ).images[0]

# Save the generated image to a file
image.save("flux-schnell.png")