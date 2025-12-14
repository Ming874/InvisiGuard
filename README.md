# InvisiGuard

Invisible Watermarking & Geometric Correction System.

## Features
- **Invisible Watermarking**: Embed text into images using DCT and HVS masking.
- **Robust Extraction**: Recover watermarks even after rotation, scaling, and cropping.
- **Attack Simulation**: Test robustness with built-in attack tools.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Documentation
Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage
1. Open http://localhost:5173
2. Go to "Embed" tab to watermark an image.
3. Download the result.
4. Go to "Extract" tab (or use the simulator).
5. Upload Original and Suspect images to recover the watermark.

## Spec Kit Integration

- **Install `uv`**: Install Astral `uv` if not already installed.
- **Install Specify CLI**: Persistently install the CLI for easy reuse.
- **Initialize in this repo**: Bootstrap slash commands for your AI agent.
- **Use slash commands**: Drive spec-driven development from chat.

### Setup (Windows)

```powershell
# Install Specify CLI (persistent)
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# Verify tools
specify check

# Initialize Spec Kit artifacts in current directory
specify init --here --ai copilot --script ps
```

If your directory is non-empty and you want to merge without confirmation:

```powershell
specify init --here --force --ai copilot --script ps
```

### Use in Chat

- `/speckit.constitution` — establish project principles
- `/speckit.specify` — define requirements and user stories
- `/speckit.plan` — choose stack and architecture
- `/speckit.tasks` — generate actionable tasks
- `/speckit.implement` — execute tasks per plan

Example:

```text
/speckit.constitution Security-first, test coverage ≥ 85%, PR checks required.
/speckit.specify Build an app to organize photos into date-grouped albums with drag-and-drop reordering and tiled previews.
/speckit.plan Vite + vanilla JS/CSS, local SQLite for metadata.
/speckit.tasks
/speckit.implement
```

### Optional: One-time Initialization

```powershell
uvx --from git+https://github.com/github/spec-kit.git specify init --here --ai copilot --script ps
```

### VS Code

This repo includes Spec Kit at `spec-kit/`. To surface recommendations in VS Code chat, ensure `.vscode/settings.json` contains chat prompt recommendations and trusted script paths. This is configured below.

InvisiGuard 開發與工程規劃文檔：基於頻域與幾何校正的抗截圖數位浮水印系統

## 1. 執行摘要 (Executive Summary)

### 專案目標
開發一套基於 Web (React + Python) 的數位浮水印系統，旨在解決「螢幕攝取（Screen Capture）」造成的版權漏洞。本系統整合了人類視覺系統（HVS）、頻域處理與幾何校正演算法，能在圖片經過**截圖、手機翻拍、旋轉、縮放**後，依然準確還原版權資訊。

### 核心技術棧
*   **前端：** React.js (互動式介面、攻擊模擬)、Tailwind CSS (樣式)、Axios (API 串接)
*   **後端：** Python (FastAPI 為主，追求高效能非同步處理)
*   **視覺核心：** OpenCV (幾何變換、特徵匹配), NumPy (矩陣運算), SciPy (DCT變換), invisible-watermark (基底庫)

### 獨特價值主張 (Unique Value Proposition)
| 特性 | 一般開源專案 (如 blind-watermark) | **Project Aigis (本專案)** |
| :--- | :--- | :--- |
| **抵抗攻擊** | 僅抗輕微壓縮、裁切 | **抗螢幕翻拍、透視變形、旋轉、縮放** |
| **視覺模型** | 全局統一強度 (容易破壞畫質) | **基於 Laplacian 的自適應遮罩 (只在紋理處嵌入)** |
| **處理流程** | 直接讀取訊號 | **先進行幾何校正 (Alignment) -> 再讀取訊號** |
| **使用者介面** | 命令列 (CLI) 為主 | **React 視覺化儀表板 (即時 Diff、校正演示、攻擊模擬)** |

---

## 2. 理論框架與演算法整合 (Theoretical Framework)

本系統將計算機視覺的三大支柱進行串聯，形成一個完整的 Pipeline：

### A. 感知層：基於 Laplacian 的視覺遮罩 (HVS Masking)
*   **理論：** 人眼對平滑區域（如藍天）的雜訊敏感，對紋理複雜區域（如草地、毛髮）的雜訊不敏感。
*   **實作細節：**
    1.  對原始圖像 $I$ 進行 **Laplacian 濾波** 得到邊緣圖 $E$。
    2.  計算局部變異數，生成一個權重矩陣 $W$。
    3.  **動態強度調整：** 設定基礎強度 $\alpha_{base}$ 與增益因子 $k$。最終嵌入強度 $\alpha(x,y) = \alpha_{base} + k \cdot W(x,y)$。這確保了在邊緣處嵌入更強訊號以抵抗壓縮，而在平滑處保持隱形。

### B. 嵌入層：DCT 頻域變換 (Frequency Domain Embedding)
*   **理論：** 空間域（Spatial Domain）的修改容易因壓縮而丟失；頻域的中頻係數（Mid-frequency coefficients）對 JPEG 壓縮與濾波具有魯棒性。
*   **實作細節：**
    1.  **分塊 (Blocking)：** 將圖像切分為 $8 \times 8$ 的區塊。
    2.  **變換 (Transform)：** 對每個區塊進行 **DCT (離散餘弦變換)**。
    3.  **嵌入 (Embedding)：** 選擇中頻段係數（如 ZigZag 掃描順序的第 10-20 個係數），利用 QIM (Quantization Index Modulation) 或簡單的加法調變嵌入二進制資訊。
    4.  **逆變換 (Inverse Transform)：** 執行 IDCT 還原圖像。

### C. 防禦層：幾何校正與透視變換 (Geometric Correction) —— **核心殺手鐧**
*   **痛點：** 手機拍螢幕時，圖片是梯形的（透視變形），座標系統全亂，DCT 區塊無法對齊。
*   **解決方案流程：**
    1.  **特徵提取 (Feature Extraction):** 使用 **ORB (Oriented FAST and Rotated BRIEF)** 算法，同時在「原圖」與「上傳的截圖」中尋找關鍵特徵點。ORB 比 SIFT/SURF 快且不受專利限制。
    2.  **特徵匹配 (Feature Matching):** 使用 `BFMatcher` (Brute-Force Matcher) 搭配 Hamming Distance 找出兩張圖對應的點。
    3.  **誤匹配剔除 (Outlier Rejection):** 利用 **RANSAC (Random Sample Consensus)** 算法排除錯誤匹配，計算出最佳的 $3 \times 3$ 單應性矩陣 $H$。
    4.  **逆向變換 (Un-warping):** 使用 `cv2.warpPerspective` 將截圖「拉正」，使其與原圖像素對齊。
    5.  **裁切與填充 (Crop & Pad):** 校正後的圖像可能包含黑邊，需進行裁切或填充以符合原圖尺寸，確保 DCT 分塊對齊。

---

## 3. 系統架構設計 (System Architecture)

### 前端 (React)
*   **核心組件：**
    *   `ImageUploader`: 支援 Drag & Drop，預覽縮圖。
    *   `WatermarkConfig`: 滑桿調整強度（Alpha）、輸入浮水印文字。
    *   `ResultViewer`: 
        *   **Side-by-Side View:** 左右對照原圖與浮水印圖。
        *   **Difference Map:** 利用 Canvas Pixel Manipulation 計算 `|Original - Watermarked| * Scale`，視覺化浮水印分佈。
    *   `AttackSimulator`: 利用 CSS `transform` 屬性（`rotate`, `scale`, `perspective`）在瀏覽器端即時模擬截圖效果，並提供「下載受損圖片」功能。

### 後端 (Python API - FastAPI)
*   **API 規格：**
    *   **`POST /api/v1/embed`**
        *   **Input:** `file` (Image), `text` (String), `alpha` (Float)
        *   **Process:** Resize -> Laplacian Mask -> DCT Embedding
        *   **Output:** `image_url` (Watermarked), `psnr` (Float - 畫質指標)
    *   **`POST /api/v1/extract`**
        *   **Input:** `original_file` (Image - for alignment), `suspect_file` (Image - Screenshot)
        *   **Process:** ORB Alignment -> Perspective Warp -> DCT Extraction
        *   **Output:** `decoded_text` (String), `confidence` (Float), `aligned_image_url` (Debug use)

---

## 4. 實施藍圖 (Implementation Roadmap)

### Phase 1: 基礎整合 (Foundation)
*   **目標：** 打通 React -> Python -> React 的完整數據流。
*   **任務：**
    1.  搭建 FastAPI 專案結構。
    2.  整合 `invisible-watermark` 庫，實作基本的 `/embed` 與 `/extract` (無幾何校正)。
    3.  React 前端實作圖片上傳與結果顯示。
*   **產出：** 可用的 Web 浮水印工具，抗壓縮但不抗截圖。

### Phase 2: 視覺優化 (Visual Quality)
*   **目標：** 提升隱蔽性，引入 HVS 模型。
*   **任務：**
    1.  實作 `Laplacian Mask` 生成邏輯。
    2.  修改嵌入邏輯，使嵌入強度 $\alpha$ 隨 Mask 動態變化。
    3.  前端實作 `Difference Map` 視覺化功能，展示「智慧嵌入」的效果。
*   **產出：** 高畫質、低感知的浮水印系統。

### Phase 3: 抗截圖戰神 (Robustness)
*   **目標：** 實現幾何校正，抵抗物理攻擊。
*   **任務：**
    1.  開發 `alignment.py` 模組，實作 ORB + RANSAC + WarpPerspective 流程。
    2.  整合至 `/extract` API：先校正，再解碼。
    3.  前端開發 `AttackSimulator`，驗證旋轉與透視後的解碼能力。
*   **產出：** 完整的抗截圖浮水印系統。

---

## 5. 技術挑戰與風險管理 (Risk Management)

| 挑戰 | 描述 | 應對策略 |
| :--- | :--- | :--- |
| **莫列波紋 (Moiré Patterns)** | 翻拍螢幕時產生的波紋干擾頻域訊號。 | **頻段選擇：** 避開易受波紋影響的高頻段，專注於中低頻嵌入。<br>**冗餘編碼：** 使用重複碼 (Repetition Code) 或 BCH 碼增加容錯率。 |
| **極端裁切** | 截圖過小導致特徵點不足，無法計算 Homography。 | **特徵點密度：** 調低 ORB 的 `fastThreshold` 以偵測更多特徵點。<br>**局部校正：** 若全域匹配失敗，退化為局部仿射變換 (Affine)。 |
| **計算效能** | 特徵匹配與幾何變換耗時較長。 | **非同步處理：** FastAPI `BackgroundTasks` 處理耗時運算。<br>**圖像縮放：** 在低解析度下計算 Homography 矩陣，再映射回高解析度原圖。 |

---

## 6. 專案亮點檢核表 (Project Highlights)

*   [ ] **視覺化幾何修復：** 在網頁上展示「截圖原本歪的樣子」vs「系統修復後正的樣子」。
*   [ ] **互動式差異圖：** 展示 Laplacian 邊緣圖，證明算法懂得「挑選適合嵌入的區域」。
*   [ ] **極限測試 Demo：** 現場手機拍攝螢幕，上傳後成功解碼，展示真實場景應用能力。

