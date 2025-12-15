import cv2
import numpy as np
import pywt
from scipy.fftpack import dct, idct
from .geometry import embed_synch_template, SynchTemplate
from reedsolo import RSCodec

# Reed-Solomon parameters
N_ECC_SYMBOLS = 10 # Number of ECC symbols (can correct N_ECC_SYMBOLS / 2 errors)


class WatermarkEmbedder:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # Initialize Reed-Solomon encoder
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def generate_log_mask(self, image_gray: np.ndarray, base_alpha: float = 1.0) -> np.ndarray:
        # (Original method unchanged)
        blurred = cv2.GaussianBlur(image_gray, (3, 3), 0)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian = np.abs(laplacian)
        mask = cv2.normalize(laplacian, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        k = 2.0
        alpha_map = base_alpha * (1 + k * mask)
        return alpha_map

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _idct2(self, block):
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def text_to_bits(self, text: str) -> list[int]:
        """Convert string to list of bits with Header, Length, and Reed-Solomon error correction."""
        header = "INV"
        length = len(text)
        
        max_data_len = 255 - N_ECC_SYMBOLS
        # We need 4 bytes for the header ("INV") and the length field.
        max_text_len = max_data_len - 4
        if length > max_text_len:
            raise ValueError(f"Text too long (max {max_text_len} chars for current Reed-Solomon config)")
            
        payload_str = header + chr(length) + text
        data = bytearray(payload_str, 'utf-8')
        
        # Pad data to a fixed size for a constant-size RS block
        padded_data = data + b'\0' * (max_data_len - len(data))

        # The encode method appends the ECC symbols to the data
        packet = self.rsc.encode(padded_data) # packet is now always 255 bytes
        
        encoded_bits = []
        for byte in packet:
            binval = bin(byte)[2:].rjust(8, '0')
            encoded_bits.extend([int(b) for b in binval])
        return encoded_bits

    def embed_watermark_dwt_qim(self, image: np.ndarray, text: str, alpha: float = 10.0) -> np.ndarray:
        """Embed watermark using DWT and QIM."""
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
        
        bits = self.text_to_bits(text)
        
        # DWT decomposition
        coeffs = pywt.dwt2(y_channel, 'haar')
        LL, (LH, HL, HH) = coeffs
        
        ll_flat = LL.flatten()
        
        if len(bits) > len(ll_flat):
            raise ValueError("Not enough space in the image to embed the watermark.")
            
        # QIM embedding
        delta = 10.0 # Fixed delta for now
        
        for i in range(len(bits)):
            c = ll_flat[i]
            b = bits[i]
            
            q = round(c / delta)
            
            if b == 0 and q % 2 != 0: # If bit is 0, quantizer must be even
                q -= 1
            elif b == 1 and q % 2 == 0: # If bit is 1, quantizer must be odd
                q += 1
            
            ll_flat[i] = q * delta
            
        LL_w = ll_flat.reshape(LL.shape)
        
        # Inverse DWT
        coeffs_w = (LL_w, (LH, HL, HH))
        y_channel_w = pywt.idwt2(coeffs_w, 'haar')
        
        # Merge channels back
        processed_y = np.clip(y_channel_w, 0, 255).astype(np.uint8)
        
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
        
        # Synchronization template is still important
        template = SynchTemplate()
        watermarked = embed_synch_template(watermarked, template)
            
        return watermarked

    def embed_watermark_dct(self, image: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
        """Original DCT-based embedding method."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        mask = self.generate_log_mask(y_channel, base_alpha=alpha)
        bits = self.text_to_bits(text)
        num_bits = len(bits)
        bit_idx = 0
        processed_y = y_channel.copy()
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if bit_idx >= num_bits: break
                block = processed_y[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                local_alpha = mask[i + self.block_size//2, j + self.block_size//2]
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                base_strength = 2.0
                gap = (base_strength * alpha) + (local_alpha * 5.0 * alpha)
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
                processed_y[i:i+self.block_size, j:j+self.block_size] = self._idct2(dct_block)
                bit_idx += 1
            if bit_idx >= num_bits: break

        processed_y = np.clip(processed_y, 0, 255).astype(np.uint8)
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
            
        template = SynchTemplate()
        watermarked = embed_synch_template(watermarked, template)
        return watermarked
