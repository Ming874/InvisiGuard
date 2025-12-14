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
