from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from src.api.schemas import WatermarkResponse, ExtractionResponse, WatermarkResponseData
from src.core.processor import ImageProcessor
from src.services.watermark import WatermarkService

router = APIRouter()
watermark_service = WatermarkService()

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "InvisiGuard API"}

@router.post("/embed", response_model=WatermarkResponse)
async def embed_watermark(
    file: UploadFile = File(...),
    text: str = Form(...),
    alpha: float = Form(1.0)
):
    try:
        # Load image
        image = await ImageProcessor.load_image(file)
        
        # Process
        result = await watermark_service.embed(image, text, alpha)
        
        return WatermarkResponse(
            status="success",
            data=WatermarkResponseData(**result)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/extract", response_model=ExtractionResponse)
async def extract_watermark(
    original_file: UploadFile = File(...),
    suspect_file: UploadFile = File(...)
):
    try:
        # Load images
        original = await ImageProcessor.load_image(original_file)
        suspect = await ImageProcessor.load_image(suspect_file)
        
        # Process
        result = await watermark_service.extract(original, suspect)
        
        return ExtractionResponse(
            status="success",
            data=ExtractionResponseData(
                decoded_text=result["extracted_text"],
                confidence=1.0 if result["status"] == "aligned" else 0.5,
                is_match=True,
                debug_info=None
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
