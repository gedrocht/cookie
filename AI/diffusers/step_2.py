from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image

# Load the img2img pipeline
img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "CompVis/stable-diffusion-v1-4", torch_dtype=torch.float16
).to("cuda")

# Open the initial image and apply slight changes in prompt
init_image = Image.open("initial_image.png")
refined_prompt = "an intimate, highly detailed scene of a man holding a woman from behind, warm and soft lighting, photorealistic, enhanced facial features, refined expressions"

# Generate refined image
refined_image = img2img_pipe(prompt=refined_prompt, init_image=init_image, strength=0.5).images[0]
refined_image.save("refined_image.png")


