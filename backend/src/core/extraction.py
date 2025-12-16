import cv2
import numpy as np
import pywt
from scipy.fftpack import dct
from .geometry import detect_rotation_scale, correct_geometry, SynchTemplate
from reedsolo import RSCodec, ReedSolomonError
from src.utils.logger import get_logger

# T028: 演算法參數常數 - 必須與 embedding.py 中的參數一致
WAVELET = 'haar'  # DWT使用的小波類型
LEVEL = 1  # DWT分解層級
DELTA = 10.0  # QIM量化步長 - 對於嵌入和提取的一致性至關重要

# Reed-Solomon 參數 (必須與嵌入器匹配) - 為抗裁切而增強
N_ECC_SYMBOLS = 30  # 可校正最多 15 個字節的錯誤
RS_BLOCK_SIZE = 255  # GF(2^8) 的最大塊大小

logger = get_logger(__name__)

class WatermarkExtractor:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # 初始化Reed-Solomon解碼器
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _parse_payload(self, payload: bytearray) -> str:
        """解析解碼後的負載以提取訊息。"""
        try:
            # --- 1. 驗證標頭 ---
            # 這是健全性檢查，以確保我們正在處理一個有效的浮水印。
            if len(payload) < 4:
                logger.error(f"[Parse] 負載太短: {len(payload)} 字節 (至少需要 4 字節)")
                return "負載太短 (浮水印已損壞)"
            
            # 檢查是否存在 "INV" 標頭。
            header = payload[:3].decode('utf-8', errors='ignore')
            if header != "INV":
                logger.error(f"[Parse] 無效的標頭: '{header}' (應為 'INV')")
                return f"無效的浮水印標頭 (得到 '{header}', 應為 'INV')"

            # --- 2. 提取長度並驗證 ---
            # 第4個字節儲存了原始訊息的長度。
            length_val = payload[3]
            logger.debug(f"[Parse] 標頭正確, 訊息長度: {length_val}")
            
            # 再次檢查長度是否在有效範圍內。
            max_text_len = 255 - N_ECC_SYMBOLS - 4
            if length_val > max_text_len:
                logger.error(f"[Parse] 無效的長度: {length_val} (最大為 {max_text_len})")
                return f"無效的訊息長度: {length_val} (浮水印已損壞)"

            if length_val == 0:
                logger.warning("[Parse] 空訊息 (長度=0)")
                return ""
            
            # --- 3. 提取並解碼訊息 ---
            end_index = 4 + length_val
            if end_index > len(payload):
                logger.error(f"[Parse] 長度 {length_val} 超出負載大小 {len(payload)}")
                return "訊息長度超出負載大小 (浮水印已損壞)"
            
            message_bytes = payload[4:end_index]
            try:
                # 嘗試使用UTF-8解碼訊息。'strict'模式下，任何錯誤都會引發異常。
                message = message_bytes.decode('utf-8', errors='strict')
                message = message.rstrip('\x00')  # 移除填充的空字節
                logger.info(f"[Parse] 成功提取訊息: '{message}' ({len(message)} 個字符)")
                return message
            except UnicodeDecodeError as e:
                # 如果嚴格解碼失敗，可能是因為一些位元錯誤。
                # 我們嘗試使用 'ignore' 模式進行寬鬆解碼作為備份。
                logger.error(f"[Parse] UTF-8 解碼錯誤: {e}")
                message = message_bytes.decode('utf-8', errors='ignore').rstrip('\x00')
                logger.warning(f"[Parse] 備份解碼 (可能丟失字符): '{message}'")
                return message
            
        except Exception as e:
            logger.error(f"[Parse] 未預期的錯誤: {type(e).__name__}: {str(e)}")
            return f"負載解析錯誤: {type(e).__name__} - {str(e)}"

    def _decode_rs_stream(self, bits: list[int]) -> str:
        """使用Reed-Solomon解碼位元列表並解析負載。"""
        # 確保我們有足夠的位元來構成一個完整的255字節數據包。
        if len(bits) < RS_BLOCK_SIZE * 8:
            logger.error(f"[RS] 位元不足: {len(bits)} (需要 {RS_BLOCK_SIZE * 8})")
            return f"沒有足夠的數據提取浮水印 (找到 {len(bits)} 位元, 需要 {RS_BLOCK_SIZE * 8})"

        # --- 1. 將位元轉換為字節 ---
        packet = bytearray()
        num_bytes = RS_BLOCK_SIZE
        bits_to_decode = bits[:num_bytes*8]
        for i in range(num_bytes):
            byte_str = "".join(map(str, bits_to_decode[i*8:(i+1)*8]))
            packet.append(int(byte_str, 2))
        
        logger.debug(f"[RS] 輸入數據包 (前20字節): {list(packet[:20])}")
        
        # --- 2. Reed-Solomon 解碼 ---
        # 這是魔法發生的地方。解碼器會嘗試修復數據包中的任何錯誤。
        # 由於我們使用了30個ECC符號，它最多可以修復15個字節的錯誤。
        try:
            decoded_data, _, errata = self.rsc.decode(packet)
            logger.info(f"[RS] 解碼成功, 校正了 {len(errata)} 個錯誤")
            logger.debug(f"[RS] 解碼後的數據 (前20字節): {list(decoded_data[:20])}")
            # 如果解碼成功，解析負載以獲取最終的訊息。
            return self._parse_payload(decoded_data)
        except ReedSolomonError as e:
            # 如果錯誤太多，解碼器會放棄並引發錯誤。
            logger.error(f"[RS] 解碼失敗: {str(e)}")
            return "未檢測到浮水印 (Reed-Solomon解碼失敗: 錯誤過多)"
        except Exception as e:
            logger.error(f"[RS] 未預期的錯誤: {type(e).__name__}: {str(e)}")
            return f"Reed-Solomon解碼錯誤: {type(e).__name__} - {str(e)}"

    def extract_watermark_dwt_qim(self, image: np.ndarray, alpha: float = 10.0) -> str:
        """使用DWT和QIM提取浮水印。"""
        # T031: 記錄參數以供調試
        logger.debug(f"[Extract] 參數: WAVELET={WAVELET}, LEVEL={LEVEL}, DELTA={DELTA}")
        
        # --- 1. 圖像預處理 ---
        # 與嵌入過程相同，我們只處理Y通道。
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
        
        # --- 2. 離散小波變換 (DWT) ---
        # 應用與嵌入時相同的DWT分解。
        coeffs = pywt.dwt2(y_channel, WAVELET)
        LL, _ = coeffs
        
        logger.debug(f"[Extract] LL子帶形狀: {LL.shape}, 位元數: {LL.shape[0] * LL.shape[1]}")
        
        ll_flat = LL.flatten()
        num_bits_to_extract = RS_BLOCK_SIZE * 8
        
        if num_bits_to_extract > len(ll_flat):
            return "圖像中的數據不足以提取浮水印。"
        
        # --- 3. 量化索引調變 (QIM) 提取 ---
        # 這是嵌入過程的逆過程。
        logger.debug(f"[Extract] 使用順序提取 (位置 0-{num_bits_to_extract-1})")
        extracted_bits = []
        
        for i in range(num_bits_to_extract):
            c = ll_flat[i]  # 獲取LL係數
            q = round(c / DELTA)  # 計算量化索引
            
            # 檢查q的奇偶性來確定嵌入的位元是0還是1。
            if q % 2 == 0:
                extracted_bits.append(0)
            else:
                extracted_bits.append(1)
        
        logger.debug(f"[Extract] 提取到位元數: {len(extracted_bits)}, 前50位: {extracted_bits[:50]}")
                
        # --- 4. 解碼位元流 ---
        # 使用Reed-Solomon解碼器處理提取出的位元流，修復錯誤並獲取原始訊息。
        return self._decode_rs_stream(extracted_bits)

    def extract_watermark_dct(self, image: np.ndarray) -> str:
        """Extract watermark from image using DCT."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        raw_extracted_bits = []
        packet_len_bits = RS_BLOCK_SIZE * 8
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if len(raw_extracted_bits) >= packet_len_bits: break
                block = y_channel[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                if c1 > c2:
                    raw_extracted_bits.append(1)
                else:
                    raw_extracted_bits.append(0)
            if len(raw_extracted_bits) >= packet_len_bits: break
        
        return self._decode_rs_stream(raw_extracted_bits)

    def extract_with_blind_alignment(self, image: np.ndarray) -> tuple[str, dict]:
        """
        Extract watermark with blind geometric correction.
        NOTE: Sync template is disabled, so this method assumes no geometric transformation.
        """
        # SIMPLIFIED: Skip geometry detection since sync template is disabled
        # This is a trade-off: Extract works perfectly, but Verify won't handle rotated/scaled images
        logger.info("[Blind] Sync template disabled - extracting without geometry correction")
        logger.warning("[Blind] Limitation: Cannot detect/correct rotation or scaling")
        
        # Direct extraction assuming no geometric transformation
        text = self.extract_watermark_dwt_qim(image, alpha=10.0)
        
        metadata = {
            "rotation_detected": 0.0,
            "scale_detected": 1.0,
            "geometry_corrected": False,
            "method": "DWT+QIM (no sync template)",
            "note": "Sync template disabled to preserve DWT coefficients"
        }
        
        # Check if extraction was successful
        if "failed" in text.lower() or "invalid" in text.lower() or "not enough" in text.lower() or "no watermark" in text.lower():
            logger.warning(f"[Blind] DWT+QIM extraction failed: {text}")
            metadata["error"] = text
        else:
            logger.info(f"[Blind] Extraction successful: {text}")
        
        return text, metadata
        
        metadata = {
            "rotation_detected": rotation,
            "scale_detected": scale,
            "geometry_corrected": True,
            "method": "DWT+QIM"
        }
        
        # Check if extraction was successful
        if "failed" in text.lower() or "invalid" in text.lower() or "not enough" in text.lower() or "no watermark" in text.lower():
            logger.warning(f"[Blind] DWT+QIM extraction failed: {text}")
            # Fallback to DCT
            logger.info("[Blind] Trying fallback DCT method")
            text_dct = self.extract_watermark_dct(corrected_image)
            if not ("failed" in text_dct.lower() or "invalid" in text_dct.lower() or "not enough" in text_dct.lower()):
                logger.info(f"[Blind] DCT method successful: {text_dct}")
                text = text_dct
                metadata["method"] = "DCT (fallback)"
            else:
                logger.error(f"[Blind] Both methods failed. DWT: {text}, DCT: {text_dct}")
                metadata["error"] = "Both DWT and DCT methods failed"
        else:
            logger.info(f"[Blind] Extraction successful: {text}")

        return text, metadata
