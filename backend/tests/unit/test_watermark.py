import pytest
import numpy as np
import cv2
from src.core.embedding import WatermarkEmbedder
from src.core.extraction import WatermarkExtractor
from src.core.geometry import GeometryProcessor

@pytest.fixture
def embedder():
    return WatermarkEmbedder()

@pytest.fixture
def extractor():
    return WatermarkExtractor()

@pytest.fixture
def geometry():
    return GeometryProcessor()

@pytest.fixture
def sample_image():
    # Create a random 256x256 image
    return np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8)

def test_log_mask_generation(embedder, sample_image):
    gray = cv2.cvtColor(sample_image, cv2.COLOR_BGR2GRAY)
    mask = embedder.generate_log_mask(gray)
    assert mask.shape == gray.shape
    assert mask.min() >= 0
    # Mask might go above 1.0 due to scaling, but should be reasonable

def test_embed_extract_cycle(embedder, extractor, sample_image):
    text = "TEST"
    # Embed
    watermarked = embedder.embed_watermark_dct(sample_image, text, alpha=1.0)
    assert watermarked.shape == sample_image.shape
    
    # Extract
    extracted_text = extractor.extract_watermark_dct(watermarked)
    
    # Check if extracted text starts with the original text
    # Note: The extractor reads all blocks, so it will have trailing garbage
    assert extracted_text.startswith(text)

def test_geometry_processor_init(geometry):
    assert geometry.orb is not None
    assert geometry.matcher is not None

def test_alignment_identity(geometry, sample_image):
    # Aligning image to itself should return the image (or very close)
    aligned = geometry.align_image(sample_image, sample_image)
    assert aligned is not None
    assert aligned.shape == sample_image.shape
    # Difference should be zero
    diff = np.mean(np.abs(sample_image - aligned))
    assert diff < 1.0

