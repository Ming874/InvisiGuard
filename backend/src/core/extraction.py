import cv2
import numpy as np
from scipy.fftpack import dct

class WatermarkExtractor:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def bits_to_text(self, bits: list[int]) -> str:
        """Convert list of bits to string."""
        chars = []
        for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            if len(byte) < 8:
                break
            
            try:
                char_code = int(''.join(map(str, byte)), 2)
                # Simple heuristic: if char is null or non-printable (except common ones), stop or skip?
                # For this MVP, let's just append.
                # But to avoid returning 1000s of garbage chars, maybe we stop at null if we find one?
                # The embedder didn't add null.
                # Let's just return the string.
                if char_code == 0:
                    break
                chars.append(chr(char_code))
            except ValueError:
                continue
                
        return "".join(chars)

    def extract_watermark_dct(self, image: np.ndarray) -> str:
        """
        Extract watermark from image using DCT.
        """
        h, w = image.shape[:2]
        
        # Convert to YUV color space
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        bits = []
        
        # Iterate over blocks
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                # Get block
                block = y_channel[i:i+self.block_size, j:j+self.block_size]
                
                # DCT
                dct_block = self._dct2(block)
                
                # Read coefficients
                c1_idx = (4, 3)
                c2_idx = (3, 4)
                
                c1 = dct_block[c1_idx]
                c2 = dct_block[c2_idx]
                
                if c1 > c2:
                    bits.append(1)
                else:
                    bits.append(0)
        
        return self.bits_to_text(bits)
