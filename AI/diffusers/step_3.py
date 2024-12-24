from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# Set up Real-ESRGAN model
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
upscaler = RealESRGANer(scale=4, model=model, model_path="RealESRGAN_x4plus.pth", tile=100)

# Load refined image and upscale
high_res_image, _ = upscaler.enhance(refined_image, outscale=4)
high_res_image.save("high_res_image.png")

