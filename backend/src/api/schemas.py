from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class WatermarkResponseData(BaseModel):
    image_url: str
    signal_map_url: Optional[str] = None
    psnr: float
    ssim: float

class WatermarkResponse(BaseModel):
    status: str = "success"
    data: WatermarkResponseData

class ExtractionDebugInfo(BaseModel):
    aligned_image_url: Optional[str] = None
    matches_found: Optional[int] = None

class ExtractionResponseData(BaseModel):
    decoded_text: str
    confidence: float
    is_match: bool
    debug_info: Optional[ExtractionDebugInfo] = None

class ExtractionResponse(BaseModel):
    status: str = "success"
    data: ExtractionResponseData

class VerificationMetadata(BaseModel):
    rotation_detected: float
    scale_detected: float
    geometry_corrected: bool

class VerificationResponseData(BaseModel):
    verified: bool
    watermark_text: Optional[str]
    confidence: float
    metadata: Optional[VerificationMetadata] = None

class VerificationResponse(BaseModel):
    status: str = "success"
    data: VerificationResponseData
