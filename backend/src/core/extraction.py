import cv2
import numpy as np
import pywt
from scipy.fftpack import dct
from .geometry import detect_rotation_scale, correct_geometry, SynchTemplate
from reedsolo import RSCodec, ReedSolomonError

# Reed-Solomon parameters (must match embedder)
N_ECC_SYMBOLS = 10
RS_BLOCK_SIZE = 255 # Max block size for GF(2^8)

class WatermarkExtractor:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # Initialize Reed-Solomon decoder
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _parse_payload(self, payload: bytearray) -> str:
        """Parses the decoded payload to extract the message."""
        try:
            # Header
            header = payload[:3].decode('utf-8', errors='ignore')
            if header != "INV":
                return "Invalid Header"

            # Length
            length_val = payload[3]

            if length_val == 0:
                return ""
            
            # Data
            end_index = 4 + length_val
            message_bytes = payload[4:end_index]
            message = message_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
            
            return message
        except Exception as e:
            return f"Payload parsing error: {str(e)}"

    def _decode_rs_stream(self, bits: list[int]) -> str:
        """Decodes a list of bits using Reed-Solomon and parses the payload."""
        if len(bits) < RS_BLOCK_SIZE * 8:
            return f"Not enough data for watermark (found {len(bits)} bits, need {RS_BLOCK_SIZE * 8})"

        packet = bytearray()
        num_bytes = RS_BLOCK_SIZE
        bits_to_decode = bits[:num_bytes*8]
        for i in range(num_bytes):
            byte_str = "".join(map(str, bits_to_decode[i*8:(i+1)*8]))
            packet.append(int(byte_str, 2))
        
        try:
            # The decode method returns the corrected data
            decoded_data, _, _ = self.rsc.decode(packet)
            return self._parse_payload(decoded_data)
        except ReedSolomonError:
            return "Reed-Solomon decoding failed: Too many errors"
        except Exception as e:
            return f"Reed-Solomon decoding error: {str(e)}"

    def extract_watermark_dwt_qim(self, image: np.ndarray, alpha: float = 10.0) -> str:
        """Extract watermark using DWT and QIM."""
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        # DWT decomposition
        coeffs = pywt.dwt2(y_channel, 'haar')
        LL, _ = coeffs
        
        ll_flat = LL.flatten()
        num_bits_to_extract = RS_BLOCK_SIZE * 8
        
        if num_bits_to_extract > len(ll_flat):
            return "Not enough data in image to extract watermark."
            
        # QIM extraction
        delta = alpha
        extracted_bits = []
        
        for i in range(num_bits_to_extract):
            c = ll_flat[i]
            q = round(c / delta)
            
            if q % 2 == 0:
                extracted_bits.append(0)
            else:
                extracted_bits.append(1)
                
        return self._decode_rs_stream(extracted_bits)

    def extract_watermark_dct(self, image: np.ndarray) -> str:
        """Extract watermark from image using DCT."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        raw_extracted_bits = []
        packet_len_bits = RS_BLOCK_SIZE * 8
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if len(raw_extracted_bits) >= packet_len_bits: break
                block = y_channel[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                if c1 > c2:
                    raw_extracted_bits.append(1)
                else:
                    raw_extracted_bits.append(0)
            if len(raw_extracted_bits) >= packet_len_bits: break
        
        return self._decode_rs_stream(raw_extracted_bits)

    def extract_with_blind_alignment(self, image: np.ndarray) -> tuple[str, dict]:
        """
        Extract watermark with blind geometric correction.
        """
        template = SynchTemplate()
        rotation, scale = detect_rotation_scale(image, template)
        
        corrected_image = correct_geometry(image, rotation, scale)
        
        # We need a way to select which extractor to use.
        # For now, default to the new DWT method.
        # The 'alpha' must be known by the extractor. This needs to be coordinated.
        text = self.extract_watermark_dwt_qim(corrected_image, alpha=10.0)
        
        metadata = {
            "rotation_detected": rotation,
            "scale_detected": scale,
            "geometry_corrected": True,
            "method": "DWT+QIM"
        }
        
        if "failed" in text or "Invalid" in text or "Not enough" in text:
             # Fallback to DCT
            text_dct = self.extract_watermark_dct(corrected_image)
            if not ("failed" in text_dct or "Invalid" in text_dct or "Not enough" in text_dct):
                text = text_dct
                metadata["method"] = "DCT"


        return text, metadata
