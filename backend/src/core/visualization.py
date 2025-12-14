import numpy as np
import cv2

def generate_signal_heatmap(original: np.ndarray, watermarked: np.ndarray, alpha_map: np.ndarray = None) -> np.ndarray:
    """
    Generates a high-contrast heatmap visualization of the watermark signal.
    
    Args:
        original: The original image (BGR).
        watermarked: The watermarked image (BGR).
        alpha_map: Optional explicit alpha map (float 0-1). If None, inferred from difference.
        
    Returns:
        A BGR image with the heatmap overlay.
    """
    # 1. Calculate difference if alpha_map not provided
    if alpha_map is None:
        # Compute absolute difference
        diff = cv2.absdiff(original, watermarked)
        # Convert to grayscale
        if len(diff.shape) == 3:
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Normalize to 0-255
        # The difference is usually very small (e.g. 1-5 pixel values).
        # We want to stretch this to full range.
        alpha_map = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    else:
        # If alpha_map is float 0-1, scale to 0-255
        if alpha_map.dtype != np.uint8:
            alpha_map = (alpha_map * 255).astype(np.uint8)
            
    # 2. Apply colormap
    heatmap = cv2.applyColorMap(alpha_map, cv2.COLORMAP_JET)
    
    # 3. Overlay on original
    # 30% heatmap, 70% original
    overlay = cv2.addWeighted(heatmap, 0.3, original, 0.7, 0)
    
    return overlay
