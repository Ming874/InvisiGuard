import cv2
import numpy as np
from typing import Tuple, Optional, List

class GeometryProcessor:
    def __init__(self, nfeatures: int = 5000, scaleFactor: float = 1.2, nlevels: int = 8):
        # Initialize ORB detector with tuned parameters for robustness
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
        # Initialize BFMatcher
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    def extract_features(self, image: np.ndarray) -> Tuple[Tuple[cv2.KeyPoint], np.ndarray]:
        """
        Extract ORB keypoints and descriptors from an image.
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        keypoints, descriptors = self.orb.detectAndCompute(gray, None)
        return keypoints, descriptors

    def align_image(self, original: np.ndarray, suspect: np.ndarray) -> Optional[np.ndarray]:
        """
        Align suspect image to match original image geometry using ORB + RANSAC.
        Returns the aligned version of the suspect image.
        """
        # 1. Extract features
        kp1, des1 = self.extract_features(original)
        kp2, des2 = self.extract_features(suspect)

        if des1 is None or des2 is None:
            print("No descriptors found.")
            return None

        # 2. Match features
        matches = self.matcher.match(des1, des2)
        
        # Sort matches by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Keep top matches (e.g., top 15% or min 10)
        num_good_matches = int(len(matches) * 0.15)
        num_good_matches = max(num_good_matches, 10) # Ensure at least 10 matches if possible
        
        if len(matches) < num_good_matches:
            good_matches = matches
        else:
            good_matches = matches[:num_good_matches]

        if len(good_matches) < 4:
            print("Not enough matches to compute homography.")
            return None

        # 3. Extract location of good matches
        # kp1 is original, kp2 is suspect
        # We want to find H that maps suspect (kp2) to original (kp1)
        src_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # 4. Find Homography
        # Maps src_pts (suspect) -> dst_pts (original)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        if M is None:
            print("Homography computation failed.")
            return None

        # 5. Warp perspective
        h, w = original.shape[:2]
        aligned_img = cv2.warpPerspective(suspect, M, (w, h))

        return aligned_img

class SynchTemplate:
    """
    Configuration for the DFT synchronization template.
    """
    def __init__(self, frequency: float = 0.1, angle: float = 45.0, strength: float = 5.0, peak_width: int = 3):
        self.frequency = frequency  # Cycles per pixel (0.0 - 0.5)
        self.angle = angle
        self.strength = strength
        self.peak_width = peak_width

def embed_synch_template(image: np.ndarray, template: SynchTemplate) -> np.ndarray:
    """
    Embeds a synchronization template (peaks) into the DFT magnitude spectrum of the image.
    """
    if len(image.shape) == 3:
        yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        y, u, v = cv2.split(yuv)
    else:
        y = image.copy()
        u, v = None, None

    h, w = y.shape
    cx, cy = w // 2, h // 2

    # 1. DFT
    dft = np.fft.fft2(y.astype(float))
    dft_shift = np.fft.fftshift(dft)

    # 2. Add peaks
    # 4 peaks at angle, angle+90, angle+180, angle+270
    angles = [template.angle, template.angle + 90, template.angle + 180, template.angle + 270]
    
    for ang in angles:
        rad_angle = np.deg2rad(ang)
        
        # Calculate radius in bins based on frequency
        # fx = u/W, fy = v/H
        # We want sqrt((u/W)^2 + (v/H)^2) = freq
        # Let's assume isotropic frequency for simplicity (circular ring)
        # But in DFT bins, u = freq * W * cos(theta), v = freq * H * sin(theta)
        
        freq_u = int(template.frequency * w * np.cos(rad_angle))
        freq_v = int(template.frequency * h * np.sin(rad_angle))
        
        px, py = cx + freq_u, cy + freq_v
        
        # Apply to a small region
        r = template.peak_width // 2
        for i in range(-r, r+1):
            for j in range(-r, r+1):
                if 0 <= py+i < h and 0 <= px+j < w:
                    # Boost magnitude
                    dft_shift[py+i, px+j] *= template.strength

    # 3. Inverse DFT
    f_ishift = np.fft.ifftshift(dft_shift)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    
    # Clip to valid range
    img_back = np.clip(img_back, 0, 255).astype(np.uint8)

    if u is not None and v is not None:
        yuv_merged = cv2.merge([img_back, u, v])
        result = cv2.cvtColor(yuv_merged, cv2.COLOR_YUV2BGR)
        return result
    else:
        return img_back

def detect_rotation_scale(image: np.ndarray, template: SynchTemplate) -> Tuple[float, float]:
    """
    Detects rotation and scale from the image using the synchronization template.
    Returns (rotation_degrees, scale_factor).
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
    
    # Zero out DC and very low freqs (radius < 10)
    y_grid, x_grid = np.ogrid[:h, :w]
    dist_from_center = np.sqrt((x_grid - cx)**2 + (y_grid - cy)**2)
    magnitude[dist_from_center < 10] = 0
    
    # 2. Find strongest peak
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(magnitude)
    peak_x, peak_y = max_loc
    
    if max_val == 0:
        return 0.0, 1.0
        
    # 3. Calculate properties
    dx = peak_x - cx
    dy = peak_y - cy
    
    # Detected frequency
    # fx = dx/w, fy = dy/h
    fx = dx / w
    fy = dy / h
    detected_freq = np.sqrt(fx**2 + fy**2)
    
    # Detected angle
    detected_angle = np.degrees(np.arctan2(dy, dx))
    
    # 4. Calculate Scale
    # scale = target / detected
    # If detected freq is 0.2 and target is 0.1, image was scaled down by 0.5.
    # So scale factor of image is 0.5.
    scale = detected_freq / template.frequency if template.frequency > 0 else 1.0
    # Wait, if image is 0.5x, freq doubles.
    # detected = target / image_scale
    # image_scale = target / detected
    scale = template.frequency / detected_freq if detected_freq > 0 else 1.0
    
    # 5. Calculate Rotation
    # Normalize angle difference to [-45, 45] assuming 90-degree symmetry
    diff = detected_angle - template.angle
    while diff > 45: diff -= 90
    while diff < -45: diff += 90
    
    rotation = diff
    
    return rotation, scale

def correct_geometry(image: np.ndarray, rotation: float, scale: float) -> np.ndarray:
    """
    Corrects the geometry of the image based on detected rotation and scale.
    """
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    
    # We want to undo the rotation and scale.
    # If image is scaled by 0.5 (smaller), we need to scale by 1/0.5 = 2.0.
    # If image is rotated by 10 deg, we need to rotate by -10.
    
    recover_scale = 1.0 / scale if scale > 0 else 1.0
    recover_rotation = rotation
    
    M = cv2.getRotationMatrix2D(center, recover_rotation, recover_scale)
    
    # Determine new bounding box to avoid cropping?
    # For now, keep original size, as we expect to recover the original view.
    corrected = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LINEAR)
    
    return corrected

