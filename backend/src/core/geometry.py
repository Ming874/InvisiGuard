import cv2
import numpy as np
from typing import Tuple, Optional, List

class GeometryProcessor:
    def __init__(self, nfeatures: int = 5000, scaleFactor: float = 1.2, nlevels: int = 8):
        # 初始化 ORB 偵測器，並調整參數以提高穩健性。
        # ORB (Oriented FAST and Rotated BRIEF) 是一種用於偵測影像中特徵點的演算法，
        # 它對於旋轉和縮放等影像變化具有良好的抵抗能力。
        self.orb = cv2.ORB_create(
            nfeatures=nfeatures,
            scaleFactor=scaleFactor,
            nlevels=nlevels,
            edgeThreshold=31,
            firstLevel=0,
            WTA_K=2,
            scoreType=cv2.ORB_HARRIS_SCORE,
            patchSize=31,
            fastThreshold=20
        )
        # 初始化 BFMatcher (Brute-Force Matcher)，用於特徵點匹配。
        # cv2.NORM_HAMMING 適用於 ORB 等二進位描述符。
        # crossCheck=True 表示只有當兩張影像中的特徵點互相匹配時，才視為一個有效的匹配。
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def extract_features(self, image: np.ndarray) -> Tuple[Tuple[cv2.KeyPoint], np.ndarray]:
        """
        從影像中提取 ORB 關鍵點和描述符。
        """
        # 如果是彩色影像，先轉換為灰階。
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        return keypoints, descriptors

    def align_image(self, original: np.ndarray, suspect: np.ndarray) -> Optional[np.ndarray]:
        """
        使用 ORB + RANSAC 將可疑影像對齊到原始影像的幾何形狀。
        返回對齊後的可疑影像版本。
        """
        # 1. 提取特徵點和描述符
        kp1, des1 = self.extract_features(original)
        kp2, des2 = self.extract_features(suspect)

        if des1 is None or des2 is None:
            print("找不到描述符。")
            return None

        # 2. 匹配特徵點
        matches = self.matcher.match(des1, des2)
        
        # 根據距離對匹配結果進行排序
        matches = sorted(matches, key=lambda x: x.distance)
        
        # 保留最佳的匹配 (例如，前15%或至少10個)
        num_good_matches = int(len(matches) * 0.15)
        num_good_matches = max(num_good_matches, 10)
        
        if len(matches) < num_good_matches:
            good_matches = matches
        else:
            good_matches = matches[:num_good_matches]

        if len(good_matches) < 4:
            print("沒有足夠的匹配來計算單應性矩陣。")
            return None

        # 3. 提取良好匹配的位置
        # kp1 是原始影像, kp2 是可疑影像
        # 我們要找到一個單應性矩陣 H，將可疑影像 (kp2) 的點映射到原始影像 (kp1) 的點
        src_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 4. 尋找單應性矩陣 (Homography)
        # RANSAC 是一種迭代方法，用於從包含“局外點”的觀測數據集中估計數學模型的參數。
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if M is None:
            print("單應性矩陣計算失敗。")
            return None

        # 5. 透視變換
        # 使用計算出的單應性矩陣 M，將可疑影像進行透視變換，使其與原始影像對齊。
        h, w = original.shape[:2]
        aligned_img = cv2.warpPerspective(suspect, M, (w, h))

        return aligned_img

class SynchTemplate:
    """
    DFT 同步模板的配置。
    """
    def __init__(self, frequency: float = 0.1, angle: float = 45.0, strength: float = 5.0, peak_width: int = 3):
        self.frequency = frequency  # 每像素的週期 (0.0 - 0.5)
        self.angle = angle
        self.strength = strength
        self.peak_width = peak_width

def embed_synch_template(image: np.ndarray, template: SynchTemplate) -> np.ndarray:
    """
    將同步模板（頻譜中的峰值）嵌入到影像的 DFT 幅度譜中。
    """
    if len(image.shape) == 3:
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
    else:
        y = image.copy()
        u, v = None, None

    h, w = y.shape
    cx, cy = w // 2, h // 2

    # 1. DFT (離散傅立葉變換) (用於盲驗證): 透過頻譜分析找出週期性的訊號，用來計算旋轉角度。
    dft = np.fft.fft2(y.astype(float))
    dft_shift = np.fft.fftshift(dft)

    # 2. 添加峰值
    # 在角度、角度+90、角度+180、角度+270處添加4個峰值
    angles = [template.angle, template.angle + 90, template.angle + 180, template.angle + 270]
    
    for ang in angles:
        rad_angle = np.deg2rad(ang)
        
        freq_u = int(template.frequency * w * np.cos(rad_angle))
        freq_v = int(template.frequency * h * np.sin(rad_angle))
        
        px, py = cx + freq_u, cy + freq_v
        
        # 在一個小區域內應用
        r = template.peak_width // 2
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                if 0 <= py+i < h and 0 <= px+j < w:
                    # 增強幅度
                    dft_shift[py+i, px+j] *= template.strength

    # 3. 逆 DFT
    f_ishift = np.fft.ifftshift(dft_shift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    # 裁剪到有效範圍
    img_back = np.clip(img_back, 0, 255).astype(np.uint8)

    if u is not None and v is not None:
        yuv_merged = cv2.merge([img_back, u, v])
        result = cv2.cvtColor(yuv_merged, cv2.COLOR_YUV2BGR)
        return result
    else:
        return img_back

def detect_rotation_scale(image: np.ndarray, template: SynchTemplate) -> Tuple[float, float]:
    """
    使用同步模板從影像中偵測旋轉和縮放。
    返回 (旋轉角度, 縮放因子)。
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
        
    h, w = gray.shape
    cx, cy = w // 2, h // 2
    
    # 1. DFT
    dft = np.fft.fft2(gray.astype(float))
    dft_shift = np.fft.fftshift(dft)
    magnitude = np.abs(dft_shift)
    
    # 將直流分量和非常低的頻率歸零 (半徑 < 10)
    y_grid, x_grid = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
    magnitude[dist_from_center < 10] = 0
    
    # 2. 找到最強的峰值
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(magnitude)
    peak_x, peak_y = max_loc
    
    if max_val == 0:
        return 0.0, 1.0
        
    # 3. 計算屬性
    dx = peak_x - cx
    dy = peak_y - cy
    
    # 偵測到的頻率
    fx = dx / w
    fy = dy / h
    detected_freq = np.sqrt(fx**2 + fy**2)
    
    # 偵測到的角度
    detected_angle = np.degrees(np.arctan2(dy, dx))
    
    # 4. 計算縮放
    # 影像縮放因子 = 目標頻率 / 偵測到的頻率
    scale = template.frequency / detected_freq if detected_freq > 0 else 1.0
    
    # 5. 計算旋轉
    # 假設90度對稱，將角度差正規化到[-45, 45]
    diff = detected_angle - template.angle
    while diff > 45: diff -= 90
    while diff < -45: diff += 90
    
    rotation = diff
    
    return rotation, scale

def correct_geometry(image: np.ndarray, rotation: float, scale: float) -> np.ndarray:
    """
    根據偵測到的旋轉和縮放校正影像的幾何形狀。
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # 我們要撤銷旋轉和縮放。
    # 如果影像被縮放了0.5倍（變小），我們需要放大 1/0.5 = 2.0 倍。
    # 如果影像被旋轉了10度，我們需要旋轉-10度。
    
    recover_scale = 1.0 / scale if scale > 0 else 1.0
    recover_rotation = rotation
    
    M = cv2.getRotationMatrix2D(center, recover_rotation, recover_scale)
    
    # 校正影像
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)
    
    return corrected

