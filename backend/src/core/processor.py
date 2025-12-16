import cv2
import numpy as np
from fastapi import UploadFile
import io

class ImageProcessor:
    @staticmethod
    async def load_image(file: UploadFile) -> np.ndarray:
        """
        從 FastAPI 的 UploadFile 物件異步加載圖像到 numpy 陣列 (BGR 格式)。

        Args:
            file (UploadFile): 用戶上傳的圖像文件。

        Returns:
            np.ndarray: 以 BGR 色彩空間表示的圖像 numpy 陣列。
        
        Raises:
            ValueError: 如果無法解碼圖像。
        """
        # 異步讀取上傳文件的內容
        contents = await file.read()
        # 將原始二進制數據轉換為 numpy 陣列
        nparr = np.frombuffer(contents, np.uint8)
        # 使用 OpenCV 從 numpy 陣列中解碼圖像。IMREAD_COLOR 表示以彩色圖像加載。
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("無法解碼圖像")
        return img

    @staticmethod
    def resize_image(image: np.ndarray, width: int = None, height: int = None) -> np.ndarray:
        """
        調整圖像大小。如果只提供寬度或高度之一，則保持寬高比。

        Args:
            image (np.ndarray): 要調整大小的圖像。
            width (int, optional): 目標寬度。
            height (int, optional): 目標高度。

        Returns:
            np.ndarray: 調整大小後的圖像。
        """
        if width is None and height is None:
            return image
        
        h, w = image.shape[:2]
        
        if width is None:
            # 如果只提供了高度，則根據高度計算寬度以保持寬高比
            r = height / float(h)
            dim = (int(w * r), height)
        elif height is None:
            # 如果只提供了寬度，則根據寬度計算高度以保持寬高比
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            # 如果寬度和高度都提供了，則直接使用
            dim = (width, height)
            
        # 使用 OpenCV 調整圖像大小。INTER_AREA 適用於縮小圖像。
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    @staticmethod
    def save_image(image: np.ndarray, path: str) -> str:
        """
        將 numpy 陣列保存為圖像文件。

        Args:
            image (np.ndarray): 要保存的圖像。
            path (str): 保存路徑。

        Returns:
            str: 保存文件的路徑。
        """
        cv2.imwrite(path, image)
        return path

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        將 BGR 圖像轉換為灰階圖像。

        Args:
            image (np.ndarray): BGR 格式的彩色圖像。

        Returns:
            np.ndarray: 灰階圖像。
        """
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
