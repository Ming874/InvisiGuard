import numpy as np
import cv2

def generate_signal_heatmap(original: np.ndarray, watermarked: np.ndarray, alpha_map: np.ndarray = None) -> np.ndarray:
    """
    生成一個高對比度的浮水印信號熱圖可視化。

    這個函數的目的是以視覺化的方式展示浮水印被嵌入到圖像的哪些區域，以及強度如何。
    它通過比較原始圖像和帶浮水印的圖像，或者直接使用一個強度圖(alpha_map)來實現。

    Args:
        original (np.ndarray): 原始圖像 (BGR 格式)。
        watermarked (np.ndarray): 帶浮水印的圖像 (BGR 格式)。
        alpha_map (np.ndarray, optional): 可選的顯式 alpha 圖 (浮點數 0-1)。如果為 None，則從差異中推斷。

    Returns:
        np.ndarray: 一個帶有熱圖疊加的 BGR 圖像。
    """
    # 1. 如果沒有提供 alpha_map，則計算差異
    if alpha_map is None:
        # 計算原始圖像和帶浮水印圖像之間的絕對差異。
        # 這些差異就是浮水印信號。
        diff = cv2.absdiff(original, watermarked)
        # 如果是彩色圖像，將差異轉換為灰階
        if len(diff.shape) == 3:
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # 將差異正規化到 0-255 的範圍。
        # 浮水印造成的差異通常非常小（例如，像素值只有 1-5 的變化）。
        # 我們需要將這個微小的差異拉伸到完整的 0-255 範圍，以便能夠看到它。
        alpha_map = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    else:
        # 如果提供了 alpha_map (範圍是 0-1 的浮點數)，則將其縮放到 0-255 的範圍。
        if alpha_map.dtype != np.uint8:
            alpha_map = (alpha_map * 255).astype(np.uint8)
            
    # 2. 應用色彩映射
    # cv2.COLORMAP_JET 是一個常見的色彩映射，它會將灰階圖像轉換為從藍色（低值）到紅色（高值）的彩色圖像。
    # 這使得我們可以很容易地看出浮水印信號在哪裡最強。
    heatmap = cv2.applyColorMap(alpha_map, cv2.COLORMAP_JET)
    
    # 3. 疊加到原始圖像上
    # 我們將熱圖和原始圖像混合在一起，這樣就可以在原始圖像上看到浮水印的位置。
    # 這裡，我們讓熱圖佔 30% 的權重，原始圖像佔 70% 的權重。
    overlay = cv2.addWeighted(heatmap, 0.3, original, 0.7, 0)
    
    return overlay
