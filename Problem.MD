# 問題分析與優化建議

本文件旨在分析現有浮水印算法的弱點，並提供具體的代碼級優化方案以增強其穩健性。

## 第二部分：為什麼現在不容易偵測出來？

目前的代碼有三個「脆弱點」，導致只要稍微有一點雜訊（例如 JPG 存檔、Line 傳輸壓縮），浮水印就會消失。

- **頻率選太高 (High Frequency)**：您使用的 `(4,3)` 在 8×8 的 DCT 矩陣中屬於中高頻。JPEG 壓縮會優先捨棄這部分的資訊。

- **沒有容錯 (Zero Error Correction)**：目前的邏輯是「1 個 Block 藏 1 個 Bit」。假設訊息有 40 bits，只要圖片上有任何一個區塊因為反光、壓縮等原因讀取錯誤，導致 Header `INV` 無法匹配，整個解碼過程就會失敗。

- **平坦區訊號太弱 (Weak Signal in Flat Areas)**：在天空或白牆等顏色平坦的區域，Laplacian 濾波後的結果趨近於 0，這使得嵌入強度 `gap` 同樣趨近於 0。在這種情況下，浮水印幾乎沒有被寫入。

## 第三部分：建議優化方案 (附修改代碼)

請依序修改以下三點，完成後您的系統將會變得非常強健。

### 優化 1：更換 DCT 嵌入位置 (抗壓縮)

**目標**：將浮水印資訊嵌入到中低頻的 DCT 係數中，這個頻段在壓縮過程中較不容易遺失。

**修改檔案**： `embedding.py` 和 `extraction.py`

**位置**： 找到 `c1_idx` 和 `c2_idx` 的定義。

```python
# --- 修改前 (太高頻，容易遺失) ---
# c1_idx = (4, 3)
# c2_idx = (3, 4)

# --- 修改後 (中低頻，抗壓縮與抗模糊能力強) ---
# 我們選 Zig-Zag 掃描順序中比較前面的位置
c1_idx = (3, 1)
c2_idx = (1, 3)
```

### 優化 2：增加「重複編碼」(Repetition Code) —— 最關鍵的修改

**目標**：實現容錯能力。即使有高達 30% 的影像區塊讀取錯誤，仍能成功還原原始訊息。我們將每個 bit 重複寫入 5 次，並在讀取時採用「五戰三勝」 (Majority Vote) 的策略。

**修改 `embedding.py` (寫入端):**

```python
def text_to_bits(self, text: str) -> list[int]:
    # ... (原有的 header/payload 處理保持不變) ...
    # 假設最後產生了 raw_bits (例如 [1, 0, 1, ...])
    
    # === 新增這段：重複編碼 ===
    redundancy = 5  # 每個 bit 重複 5 次
    encoded_bits = []
    for b in raw_bits:
        encoded_bits.extend([b] * redundancy)
        
    return encoded_bits
```

**修改 `extraction.py` (讀取端):**

```python
def extract_watermark_dct(self, image: np.ndarray) -> str:
    # ... (前面的 DCT 讀取邏輯不變) ...
    # 假設您把讀到的所有 bits 存成了 raw_extracted_bits 列表
    
    # === 新增這段：多數決解碼 (Majority Vote) ===
    redundancy = 5
    final_bits = []
    
    # 每 5 個一組進行切分
    for i in range(0, len(raw_extracted_bits), redundancy):
        chunk = raw_extracted_bits[i : i+redundancy]
        if not chunk: break
        
        # 統計 1 的數量
        count_ones = sum(chunk)
        # 如果 1 的數量超過半數 (例如 5 次裡出現 3 次)，就判定原始 bit 為 1
        if count_ones > redundancy / 2:
            final_bits.append(1)
        else:
            final_bits.append(0)
            
    return self.bits_to_text(final_bits)
```

### 優化 3：設定最小嵌入強度 (Minimum Strength)

**目標**：確保即使在顏色單純的背景下，浮水印也能被以一個最低的強度嵌入。

**修改 `embedding.py`:**

```python
def embed_watermark_dct(self, image: np.ndarray, text: str, alpha: float = 1.0) -> np.ndarray:
    # ... (中間省略) ...
    
    # 找到計算 gap 的地方
    local_alpha = mask[i + self.block_size//2, j + self.block_size//2]
    
    # --- 修改前 ---
    # gap = local_alpha * 5.0 
    
    # --- 修改後 ---
    # 給一個基礎強度 (base_strength)，例如 2.0
    # 這樣就算 local_alpha 是 0，gap 至少還有 2.0
    base_strength = 2.0
    gap = (base_strength * alpha) + (local_alpha * 5.0 * alpha)
    
    # ... (後面不變)
```

## 總結與下一步

1.  **立即執行**：先修改 **優化 1 (座標)** 和 **優化 3 (最小強度)**。這兩處修改只需改動少量代碼，但能立即且顯著地增強浮水印的強度與可見性。
2.  **關鍵升級**：接著完成 **優化 2 (重複編碼)**。這部分的修改雖然需要調整迴圈邏輯，但它是將系統從「概念驗證」提升至「具備實用價值」的決定性步驟。
