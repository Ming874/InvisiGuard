
import sys
import os
import numpy as np
import cv2

# Add the src directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mocking dependencies to avoid importing the whole world if not needed
# But better to try importing the actual class first.
try:
    from src.services.watermark import WatermarkService
    print("Successfully imported WatermarkService")
except ImportError as e:
    print(f"Failed to import WatermarkService: {e}")
    sys.exit(1)

def test_ssim():
    service = WatermarkService()
    
    # Create two identical images (random noise)
    img1 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img2 = img1.copy()
    
    # SSIM of identical images should be 1.0
    ssim_identical = service._calculate_ssim(img1, img2)
    print(f"SSIM (Identical): {ssim_identical}")
    
    # Create different images
    img3 = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    ssim_diff = service._calculate_ssim(img1, img3)
    print(f"SSIM (Different): {ssim_diff}")

if __name__ == "__main__":
    test_ssim()
