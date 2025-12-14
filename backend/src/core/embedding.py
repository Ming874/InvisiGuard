import cv2
import numpy as np
from scipy.fftpack import dct, idct

class WatermarkEmbedder:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size

    def generate_log_mask(self, image_gray: np.ndarray, base_alpha: float = 1.0) -> np.ndarray:
        """
        Generate a Human Visual System (HVS) mask using Laplacian of Gaussian (LoG).
        High values in textured areas, low values in smooth areas.
        """
        # Apply Gaussian Blur to reduce noise
        blurred = cv2.GaussianBlur(image_gray, (3, 3), 0)
        
        # Calculate Laplacian to detect edges/texture
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian = np.abs(laplacian)
        
        # Normalize to range [0, 1]
        mask = cv2.normalize(laplacian, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        
        # Scale mask: alpha_map = base_alpha * (1 + k * mask)
        # k is a gain factor, let's assume k=2 for now (up to 3x strength in edges)
        k = 2.0
        alpha_map = base_alpha * (1 + k * mask)
        
        return alpha_map

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _idct2(self, block):
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def text_to_bits(self, text: str) -> list[int]:
        """Convert string to list of bits."""
        bits = []
        for char in text:
            binval = bin(ord(char))[2:].rjust(8, '0')
            bits.extend([int(b) for b in binval])
        return bits

    def embed_watermark_dct(self, image: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
        """
        Embed watermark into image using DCT and HVS masking.
        """
        h, w = image.shape[:2]
        
        # Convert to YUV color space
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        # Generate HVS mask
        mask = self.generate_log_mask(y_channel, base_alpha=alpha)
        
        # Convert text to bits
        bits = self.text_to_bits(text)
        num_bits = len(bits)
        
        # Embed bits
        bit_idx = 0
        
        # Iterate over blocks
        # We use a simple strategy: 1 bit per block for robustness
        # In a real "God of War" scenario, we might use Spread Spectrum or Repetition Code
        
        processed_y = y_channel.copy()
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if bit_idx >= num_bits:
                    break
                
                # Get block
                block = processed_y[i:i+self.block_size, j:j+self.block_size]
                
                # DCT
                dct_block = self._dct2(block)
                
                # Embed in mid-frequency coefficients (e.g., (4,3) and (3,4))
                # Using a simple differential method or QIM
                # Here we use a simplified additive method modulated by the mask
                
                # Get local alpha from the center of the block
                local_alpha = mask[i + self.block_size//2, j + self.block_size//2]
                
                # Embedding logic:
                # If bit is 1, ensure C1 > C2 + gap
                # If bit is 0, ensure C2 > C1 + gap
                # C1, C2 are selected mid-freq coefficients
                c1_idx = (4, 3)
                c2_idx = (3, 4)
                
                c1 = dct_block[c1_idx]
                c2 = dct_block[c2_idx]
                
                gap = local_alpha * 5.0 # Scaling factor
                
                bit = bits[bit_idx]
                
                if bit == 1:
                    if c1 <= c2 + gap:
                        diff = (c2 + gap - c1) / 2.0
                        dct_block[c1_idx] += diff
                        dct_block[c2_idx] -= diff
                else:
                    if c2 <= c1 + gap:
                        diff = (c1 + gap - c2) / 2.0
                        dct_block[c2_idx] += diff
                        dct_block[c1_idx] -= diff
                
                # IDCT
                processed_y[i:i+self.block_size, j:j+self.block_size] = self._idct2(dct_block)
                
                bit_idx += 1
        
        # Merge channels back
        processed_y = np.clip(processed_y, 0, 255).astype(np.uint8)
        
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
            
        return watermarked
