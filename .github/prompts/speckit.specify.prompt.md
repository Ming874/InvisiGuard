---
agent: speckit.specify
---

# /speckit.specify Prompt (InvisiGuard)

## Objective
以規格驅動方式定義 InvisiGuard 的核心功能：基於頻域與幾何校正的抗截圖數位浮水印系統。聚焦於強韌性（Robustness）、幾何校正能力與 Web 互動體驗，為後續 `/speckit.plan` 與 `/speckit.implement` 奠定基礎。

## Actors
- 一般使用者（內容創作者、測試人員）
- 系統管理者（維運人員）

## Feature: Core Watermarking & Geometric Correction Pipeline（核心浮水印與幾何校正管線）
### Goals
- 實作抗截圖、抗翻拍的數位浮水印嵌入與提取。
- 透過幾何校正還原經過旋轉、縮放、透視變形的圖像。
- 提供直觀的 Web 介面進行操作與攻擊模擬。

### Functional Requirements（可測試）
1.  **圖像上傳與預處理**：
    -   前端支援 Drag & Drop 上傳原始圖像。
    -   後端 Preprocessor 進行尺寸標準化與格式轉換。
2.  **浮水印嵌入 (Embedding)**：
    -   **視覺感知遮罩 (HVS)**：利用 LoG (Laplacian of Gaussian) 計算圖像紋理，動態調整嵌入強度 $\alpha$。
    -   **頻域嵌入 (DCT)**：將圖像分塊 (8x8) 進行 DCT 變換，於中頻係數嵌入二進制資訊。
    -   提供 API `/embed` 接收圖像與參數，回傳嵌入後圖像。
3.  **幾何校正 (Geometric Correction)**：
    -   **特徵匹配**：使用 ORB 演算法提取特徵點，匹配截圖與原圖。
    -   **透視變換**：利用 RANSAC 計算單應性矩陣 (Homography)，使用 `cv2.warpPerspective` 逆向還原圖像幾何。
4.  **浮水印提取 (Extraction)**：
    -   對校正後的圖像進行 DCT 變換，提取中頻係數資訊。
    -   計算 NCC (Normalized Cross-Correlation) 驗證浮水印正確性。
    -   提供 API `/extract` 接收原圖與待測圖，回傳解碼結果與信心分數。
5.  **前端互動與模擬**：
    -   **Diff View**：視覺化展示原圖與浮水印圖的差異（放大顯示嵌入區域）。
    -   **攻擊模擬器**：前端 CSS 模擬旋轉、縮放、透視變形，並可下載變形後的「截圖」。

### Non-Goals（此階段不涵蓋）
- 影片與音訊浮水印。
- 即時串流處理。
- 大規模併發處理優化（先求功能驗證）。
- 複雜的權限管理系統。

## User Scenarios & Testing
- **場景一：嵌入與視覺確認**
    -   使用者上傳圖片 -> 調整強度滑桿 -> 系統回傳圖片 -> Diff View 顯示僅在紋理處有變動 -> 肉眼無法察覺浮水印。
- **場景二：模擬截圖攻擊**
    -   使用者在前端旋轉圖片 15 度 -> 下載截圖 -> 上傳至提取區 -> 系統自動校正並成功解碼浮水印。
- **場景三：真實翻拍測試**
    -   使用者用手機拍攝螢幕上的圖片 -> 上傳照片 -> 系統經由 ORB 匹配與透視變換 -> 成功提取浮水印。

## Success Criteria（技術無關，可驗證）
- **抗幾何攻擊**：支援旋轉 $\pm 45^\circ$、縮放 $50\% \sim 150\%$ 的截圖還原。
- **抗壓縮**：支援 JPEG 品質因子 $Q=50$ 以上的壓縮後提取。
- **效能**：1080p 圖像嵌入時間 $\le 2$ 秒；提取（含幾何校正）時間 $\le 5$ 秒。
- **準確度**：在定義的攻擊範圍內，浮水印提取成功率（NCC > 0.8）達 90% 以上。

## Assumptions
- 使用者擁有原始圖像（用於幾何校正的基準）。
- 拍攝或截圖保有足夠的特徵點供 ORB 識別。

## Dependencies & Constraints
- **核心庫**：OpenCV (Python), NumPy, SciPy, `invisible-watermark` (作為基底或參考)。
- **前端**：React, Tailwind CSS。
- **後端**：Python (Flask/FastAPI)。
- 遵循 `.specify/memory/constitution.md` 的架構與代碼規範。

## Notes
- 幾何校正為本專案核心亮點，需優先驗證 `findHomography` 與 `warpPerspective` 的穩定性。
- 需注意莫列波紋（Moiré Patterns）對頻域訊號的干擾，可能需調整頻段選擇。
