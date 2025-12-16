import cv2
import numpy as np
import pywt
from scipy.fftpack import dct, idct
from .geometry import embed_synch_template, SynchTemplate
from reedsolo import RSCodec
from src.utils.logger import get_logger

# T027: 演算法參數常數 - 必須與 extraction.py 中的參數一致
WAVELET = 'haar'  # DWT使用的小波類型
LEVEL = 1  # DWT分解層級
DELTA = 10.0  # QIM量化步長 - 對於嵌入和提取的一致性至關重要

# Reed-Solomon 參數 - 為抗裁切而增強
N_ECC_SYMBOLS = 30  # ECC（錯誤校正碼）符號的數量（可校正 N_ECC_SYMBOLS / 2 = 15 個錯誤）
# 權衡：更多的ECC意味著更好的錯誤校正能力，但訊息容量會減少

logger = get_logger(__name__)


class WatermarkEmbedder:
    def __init__(self, block_size: int = 8):
        self.block_size = block_size
        
        # 初始化Reed-Solomon編碼器
        self.rsc = RSCodec(N_ECC_SYMBOLS)

    def generate_log_mask(self, image_gray: np.ndarray, base_alpha: float = 1.0) -> np.ndarray:
        # (原始方法未變)
        blurred = cv2.GaussianBlur(image_gray, (3, 3), 0)
        laplacian = cv2.Laplacian(blurred, cv2.CV_64F)
        laplacian = np.abs(laplacian)
        mask = cv2.normalize(laplacian, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
        k = 2.0
        alpha_map = base_alpha * (1 + k * mask)
        return alpha_map

    def _dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def _idct2(self, block):
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def text_to_bits(self, text: str) -> list[int]:
        """將字串轉換為位元列表，包含標頭、長度、和Reed-Solomon錯誤校正碼。"""
        # --- 1. 構建負載 ---
        # 負載是用戶訊息和一些額外資訊的組合，以確保可以正確提取它。

        # "INV" 是一個 "魔法" 標頭，用於識別我們的浮水印。
        header = "INV"
        length = len(text)
        
        # Reed-Solomon編碼器處理固定大小的數據塊。我們的是255字節。
        # 一部分塊用於錯誤校正，剩下的是數據。
        max_data_len = 255 - N_ECC_SYMBOLS
        
        # 我們需要3個字節放標頭("INV")和1個字節放長度。
        max_text_len = max_data_len - 4
        if length > max_text_len:
            raise ValueError(f"文本太長 (當前Reed-Solomon配置最大支持 {max_text_len} 個字符)")
            
        # 組合負載：標頭 + 長度 + 文本
        payload_str = header + chr(length) + text
        data = bytearray(payload_str, 'utf-8')
        
        # --- 2. 填充和編碼 ---
        # 用空字節填充數據，使其達到固定大小 (225 字節)。
        # 這確保了即使訊息很短，整個數據塊的大小也是一致的。
        padded_data = data + b'\0' * (max_data_len - len(data))

        # 使用Reed-Solomon對數據進行編碼。
        # 這會將30個ECC字節附加到數據的末尾，總共產生255字節的數據包。
        # 這些ECC字節就像一個安全網，可以修復在提取過程中可能發生的錯誤。
        packet = self.rsc.encode(padded_data)
        
        logger.debug(f"[Embed] 原始文本: '{text}', 長度: {length}")
        logger.debug(f"[Embed] 負載 (前20字節): {list(packet[:20])}")
        
        # --- 3. 轉換為位元 ---
        # 將255字節的數據包轉換為位元流 (255 * 8 = 2040 位元)。
        # 每個位元都將嵌入到圖像的一個係數中。
        encoded_bits = []
        for byte in packet:
            binval = bin(byte)[2:].rjust(8, '0')
            encoded_bits.extend([int(b) for b in binval])
        return encoded_bits

    def embed_watermark_dwt_qim(self, image: np.ndarray, text: str, alpha: float = 10.0) -> np.ndarray:
        """使用DWT和QIM嵌入浮水印。"""
        # T030: 記錄參數以供調試
        logger.debug(f"[Embed] 參數: WAVELET={WAVELET}, LEVEL={LEVEL}, DELTA={DELTA}, alpha={alpha}")
        
        # --- 1. 圖像預處理 ---
        # 如果圖像有顏色，我們將其轉換為YUV色彩空間。
        # Y通道代表亮度（黑白），U和V代表色度。
        # 我們只在Y通道中嵌入浮水印，以避免影響顏色。
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else: # 如果圖像已經是灰階
            y_channel = image.astype(float)
        
        original_y_shape = y_channel.shape
        
        # --- 2. 準備位元流 ---
        # 將要嵌入的文本轉換為包含錯誤校正碼的位元流。
        bits = self.text_to_bits(text)
        
        # --- 3. 離散小波變換 (DWT) ---
        # DWT將圖像分解為不同的頻率分量。
        # 我們使用'haar'小波，因為它簡單且高效。
        # 分解產生四個子帶：
        # LL: 低頻（圖像的主要結構）
        # LH, HL, HH: 高頻（邊緣和紋理）
        # 我們將浮水印嵌入到LL子帶中，因為它對圖像質量的影響最小，並且對壓縮等攻擊最不敏感。
        coeffs = pywt.dwt2(y_channel, WAVELET)
        LL, (LH, HL, HH) = coeffs
        
        logger.debug(f"[Embed] LL子帶形狀: {LL.shape}, 總容量: {LL.shape[0] * LL.shape[1]} 位元")
        logger.debug(f"[Embed] QIM前LL子帶的最小/最大值: {LL.min():.2f}/{LL.max():.2f}")
        logger.debug(f"[Embed] 嵌入 {len(bits)} 位元, 前50位: {bits[:50]}")
        
        ll_flat = LL.flatten()
        
        if len(bits) > len(ll_flat):
            raise ValueError("圖像空間不足以嵌入浮水印。")
        
        # --- 4. 量化索引調變 (QIM) ---
        # QIM是一種通過修改係數的量化值來嵌入數據的技術。
        # 這裡，我們使用係數的奇偶性來代表0或1。
        # 我們將浮水印順序嵌入到圖像的左上角區域。
        # 這種策略有助於抵抗從圖像底部或右側的裁切。
        logger.debug(f"[Embed] 使用順序嵌入 (位置 0-{len(bits)-1})")
        for i in range(len(bits)):
            c = ll_flat[i]  # 獲取一個LL係數
            b = bits[i]     # 獲取要嵌入的位元 (0 或 1)
            
            # 將係數除以DELTA並四捨五入，得到量化索引q。
            q = round(c / DELTA)
            
            # 根據要嵌入的位元調整q的奇偶性。
            # 如果位元是0，q必須是偶數。
            # 如果位元是1，q必須是奇數。
            if b == 0 and q % 2 != 0:
                q -= 1
            elif b == 1 and q % 2 == 0:
                q += 1
            
            # 用新的q重新計算係數，從而嵌入位元。
            ll_flat[i] = q * DELTA
            
        LL_w = ll_flat.reshape(LL.shape)
        
        logger.debug(f"[Embed] QIM後LL_w的最小/最大值: {LL_w.min():.2f}/{LL_w.max():.2f}")
        
        # --- 5. 重建圖像 ---
        # 使用修改後的LL子帶和原始的LH, HL, HH子帶進行逆DWT，
        # 重建帶有浮水印的Y通道。
        coeffs_w = (LL_w, (LH, HL, HH))
        y_channel_w = pywt.idwt2(coeffs_w, WAVELET)
        
        # 有時IDWT後的尺寸會因舍入而有1個像素的差異。
        # 我們需要確保其尺寸與原始Y通道完全相同。
        if y_channel_w.shape != original_y_shape:
            logger.warning(f"[Embed] IDWT尺寸不匹配！得到 {y_channel_w.shape}, 期望 {original_y_shape}")
            y_channel_w = y_channel_w[:original_y_shape[0], :original_y_shape[1]]
        
        # 將Y通道的值裁剪到0-255範圍並轉換為8位無符號整數。
        processed_y = np.clip(y_channel_w, 0, 255).astype(np.uint8)
        
        # 如果原始圖像是彩色的，將修改後的Y通道與原始U, V通道合併。
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else: # 否則，直接使用修改後的Y通道。
            watermarked = processed_y
        
        logger.info(f"[Embed] 成功嵌入 {len(bits)} 位元到圖像中")
            
        return watermarked

    def embed_watermark_dct(self, image: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
        """Original DCT-based embedding method."""
        h, w = image.shape[:2]
        
        if len(image.shape) == 3:
            yuv = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
            y_channel = yuv[:, :, 0].astype(float)
        else:
            y_channel = image.astype(float)
            
        mask = self.generate_log_mask(y_channel, base_alpha=alpha)
        bits = self.text_to_bits(text)
        num_bits = len(bits)
        bit_idx = 0
        processed_y = y_channel.copy()
        
        for i in range(0, h - self.block_size + 1, self.block_size):
            for j in range(0, w - self.block_size + 1, self.block_size):
                if bit_idx >= num_bits: break
                block = processed_y[i:i+self.block_size, j:j+self.block_size]
                dct_block = self._dct2(block)
                local_alpha = mask[i + self.block_size//2, j + self.block_size//2]
                c1_idx, c2_idx = (3, 1), (1, 3)
                c1, c2 = dct_block[c1_idx], dct_block[c2_idx]
                base_strength = 2.0
                gap = (base_strength * alpha) + (local_alpha * 5.0 * alpha)
                bit = bits[bit_idx]
                if bit == 1:
                    if c1 <= c2 + gap:
                        diff = (c2 + gap - c1) / 2.0
                        dct_block[c1_idx] += diff
                        dct_block[c2_idx] -= diff
                else:
                    if c2 <= c1 + gap:
                        diff = (c1 + gap - c2) / 2.0
                        dct_block[c2_idx] += diff
                        dct_block[c1_idx] -= diff
                processed_y[i:i+self.block_size, j:j+self.block_size] = self._idct2(dct_block)
                bit_idx += 1
            if bit_idx >= num_bits: break

        processed_y = np.clip(processed_y, 0, 255).astype(np.uint8)
        if len(image.shape) == 3:
            yuv[:, :, 0] = processed_y
            watermarked = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
        else:
            watermarked = processed_y
            
        template = SynchTemplate()
        watermarked = embed_synch_template(watermarked, template)
        return watermarked
