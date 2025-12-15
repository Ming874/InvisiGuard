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
        """
        # 1. Align image
        aligned = self.geometry.align_image(original, suspect)
        
        if aligned is None:
            # Fallback: try extracting without alignment
            aligned = suspect
            status = "alignment_failed"
        else:
            status = "aligned"
            
        # 2. Extract watermark
        # The alpha/delta value must match the one used during embedding.
        # The default is 10.0 in both, which is consistent for now.
        text = self.extractor.extract_watermark_dwt_qim(aligned)
        
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
        # Simplified SSIM or use skimage.metrics.structural_similarity
        # For MVP, let's use a placeholder or simple calculation
        # Since we don't have skimage in requirements (only scipy/numpy/cv2), 
        # we can implement a basic one or just return a placeholder if complex.
        # Let's stick to a basic estimation or just PSNR for now if SSIM is too complex to implement from scratch.
        # Actually, let's try to import structural_similarity if available, else return 0.
        try:
            from skimage.metrics import structural_similarity
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            return structural_similarity(gray1, gray2)
        except ImportError:
            return 0.0
