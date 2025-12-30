import numpy as np
import cv2
from src.core.embedding import WatermarkEmbedder
from src.core.extraction import WatermarkExtractor
from src.core.geometry import GeometryProcessor
from src.core.visualization import generate_signal_heatmap
from src.core.processor import ImageProcessor
import os
import uuid

class WatermarkService:
    def __init__(self):
        self.embedder = WatermarkEmbedder()
        self.extractor = WatermarkExtractor()
        self.geometry = GeometryProcessor()
        self.processor = ImageProcessor()

    async def embed(self, image: np.ndarray, text: str, alpha: float) -> dict:
        """
        Orchestrate the embedding process.
        Returns dict with paths and metrics.
        """
        # 1. Embed watermark using the new DWT+QIM method
        watermarked_image = self.embedder.embed_watermark_dwt_qim(image, text, alpha)
        
        # 2. Generate Signal Map
        signal_map = generate_signal_heatmap(image, watermarked_image)
        
        # 3. Calculate metrics (PSNR, SSIM)
        psnr = self._calculate_psnr(image, watermarked_image)
        ssim = self._calculate_ssim(image, watermarked_image)
        
        # 4. Save result
        filename = f"{uuid.uuid4()}.png"
        output_path = os.path.join("static/processed", filename)
        self.processor.save_image(watermarked_image, output_path)
        
        signal_filename = f"signal_{filename}"
        signal_path = os.path.join("static/processed", signal_filename)
        self.processor.save_image(signal_map, signal_path)
        
        return {
            "image_url": f"/static/processed/{filename}",
            "signal_map_url": f"/static/processed/{signal_filename}",
            "psnr": round(psnr, 2),
            "ssim": round(ssim, 4)
        }

    async def extract(self, original: np.ndarray, suspect: np.ndarray) -> dict:
        """
        Orchestrate the extraction process with geometric alignment.
        This function extracts watermark by comparing the original (unwatermarked) 
        and suspect (watermarked) images.
        """
        print(f"[Extract Service] Original shape: {original.shape}, Suspect shape: {suspect.shape}")
        
        # 1. Align suspect to match original geometry
        aligned = self.geometry.align_image(original, suspect)
        print(f"[Extract Service] Alignment result: {aligned is not None}")
        
        if aligned is None:
            # Fallback: try without alignment
            aligned = suspect
            status = "alignment_failed"
        else:
            status = "aligned"
        
        # 2. Extract watermark from the aligned suspect image
        # For Extract (with original), we extract directly from the watermarked image
        # The watermarked image should contain the embedded watermark
        text = self.extractor.extract_watermark_dwt_qim(aligned)
        
        # 3. If extraction failed, log details for debugging
        if "failed" in text.lower() or "invalid" in text.lower() or "not enough" in text.lower():
            # Try DCT fallback method
            text_dct = self.extractor.extract_watermark_dct(aligned)
            if not ("failed" in text_dct.lower() or "invalid" in text_dct.lower()):
                text = text_dct
                status = f"{status}_dct_fallback"
        
        return {
            "extracted_text": text,
            "status": status
        }

    async def verify(self, suspect: np.ndarray) -> dict:
        """
        Orchestrate the blind verification process.
        """
        # 1. Extract with blind alignment
        text, metadata = self.extractor.extract_with_blind_alignment(suspect)
        
        # 2. Determine verification status
        verified = bool(text and len(text) > 0)
        
        return {
            "verified": verified,
            "watermark_text": text,
            "confidence": 1.0 if verified else 0.0,
            "metadata": metadata
        }

    def _calculate_psnr(self, img1: np.ndarray, img2: np.ndarray) -> float:
        mse = np.mean((img1 - img2) ** 2)
        if mse == 0:
            return 100.0
        return 20 * np.log10(255.0 / np.sqrt(mse))

    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> float:
        try:
            from skimage.metrics import structural_similarity
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            return structural_similarity(gray1, gray2)
        except ImportError:
            print("Warning: scikit-image not found. SSIM calculation skipped.")
            return 0.0
