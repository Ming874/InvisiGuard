import pytest
import numpy as np
import cv2
from src.core.geometry import SynchTemplate, embed_synch_template, detect_rotation_scale, correct_geometry
from src.core.visualization import generate_signal_heatmap

def test_synch_template_embedding():
    # Create a random image (not zeros, so multiplication works)
    image = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
    template = SynchTemplate(frequency=0.1, angle=45.0, strength=50.0)
    
    # Embed
    embedded = embed_synch_template(image, template)
    
    # Check if image changed
    assert not np.array_equal(image, embedded)
    
    # Check if peaks are detectable
    rotation, scale = detect_rotation_scale(embedded, template)
    
    # Since we didn't rotate/scale, should be close to 0 and 1
    assert abs(rotation) < 5.0
    assert abs(scale - 1.0) < 0.1

def test_rotation_recovery():
    # Create image with pattern
    image = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
    template = SynchTemplate(frequency=0.1, angle=45.0, strength=100.0)
    
    # Embed
    embedded = embed_synch_template(image, template)
    
    # Rotate by 30 degrees
    h, w = embedded.shape
    M = cv2.getRotationMatrix2D((w//2, h//2), 30, 1.0)
    rotated = cv2.warpAffine(embedded, M, (w, h))
    
    # Detect
    rotation, scale = detect_rotation_scale(rotated, template)
    
    # Should detect approx 30 degrees
    # Note: The detector returns rotation relative to template angle.
    # If we rotated image by 30, the peaks also rotated by 30.
    # So detected angle should be template.angle + 30.
    # The function returns (detected_angle - template.angle).
    # So it should return -30 (due to Y-down coordinate system).
    
    print(f"Detected rotation: {rotation}")
    assert abs(rotation - (-30.0)) < 5.0

def test_scale_recovery():
    # Create image
    image = np.random.randint(0, 255, (256, 256), dtype=np.uint8)
    template = SynchTemplate(frequency=0.1, angle=45.0, strength=100.0)
    
    # Embed
    embedded = embed_synch_template(image, template)
    
    # Scale by 0.8
    scaled = cv2.resize(embedded, None, fx=0.8, fy=0.8)
    
    # Detect
    rotation, scale = detect_rotation_scale(scaled, template)
    
    print(f"Detected scale: {scale}")
    # Scale factor of image is 0.8.
    # The detector calculates scale = template.freq / detected.freq
    # If image is smaller, freq is higher?
    # Spatial period T. Freq f = 1/T.
    # If image scaled by s < 1, features are smaller (in pixels)? No, wait.
    # If I resize 100x100 to 50x50 (s=0.5).
    # A wave with period 10px in 100x100 becomes period 5px in 50x50.
    # Period decreases -> Freq increases.
    # So detected_freq = original_freq / s.
    # s = original_freq / detected_freq.
    # My code: scale = template.frequency / detected_freq.
    # So it should be correct.
    
    assert abs(scale - 0.8) < 0.1

def test_heatmap_generation():
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add some difference
    cv2.rectangle(img2, (10, 10), (20, 20), (255, 255, 255), -1)
    
    heatmap = generate_signal_heatmap(img1, img2)
    
    assert heatmap.shape == img1.shape
    assert heatmap.dtype == np.uint8
