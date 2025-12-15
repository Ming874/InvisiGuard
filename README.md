# InvisiGuard

**InvisiGuard** is a robust invisible watermarking system designed to protect digital images against screen capture ("analog hole"), rotation, scaling, and cropping attacks. It combines **Frequency Domain (DCT)** embedding with **Human Visual System (HVS)** masking and **Geometric Correction (ORB+RANSAC)** to ensure watermark survivability and invisibility.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)

## 🌟 Key Features

- **Invisible Embedding**: Uses Discrete Cosine Transform (DCT) and Laplacian-based HVS masking to hide text in image textures, minimizing visual distortion.
- **Robust Extraction (With Original)**: Recovers watermarks from distorted images (screenshots, photos of screens) by aligning them with the original image using ORB feature matching and RANSAC homography.
- **Blind Verification**: Detects and reads watermarks without the original image (using a structured payload with `[INV]` header), supporting basic rotation/scaling correction.
- **Attack Simulation**: Built-in frontend tools to simulate attacks (Rotation, Scaling, Perspective Warp) and verify robustness instantly.
- **Interactive UI**: React-based dashboard with real-time difference maps, side-by-side comparison, and detailed signal analysis (PSNR, SSIM).

## 🛠️ Tech Stack

- **Backend**: Python 3.11+, FastAPI, OpenCV, NumPy, SciPy.
- **Frontend**: React 18 (Vite), Tailwind CSS, Axios.
- **Algorithms**: DCT (Discrete Cosine Transform), ORB (Oriented FAST and Rotated BRIEF), RANSAC, Laplacian of Gaussian (LoG).

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher

### 1. Backend Setup

```bash
cd backend
# Create virtual environment (optional but recommended)
python -m venv .venv

Windows: 
.venv\Scripts\activate

Mac/Linux: 
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
# Server will start at http://localhost:8000
```

### 2. Frontend Setup

```bash
cd frontend
# Install dependencies
npm install

# Start development server
npm run dev
# App will open at http://localhost:5173
```

## 📖 Usage Guide

### 1. Embed Watermark
1.  Navigate to the **Embed Watermark** tab.
2.  Upload an image (JPEG/PNG).
3.  Enter the text to embed (e.g., "Copyright 2025").
4.  Adjust **Strength (Alpha)** if needed (Higher = more robust but more visible).
5.  Click **Embed** and wait for processing.
6.  Click "Download" to directly download the watermarked image (no new tab).

### 2. Extract (With Original)
*Use this mode for maximum robustness against severe geometric distortion (e.g., angled photos).*
1.  Navigate to the **Extract (With Original)** tab.
2.  Upload the **Original Image** (Reference).
3.  Upload the **Suspect Image** (Screenshot or distorted version).
4.  Click **Extract Watermark**.
5.  The system will align the images and decode the text.

### 3. Verify (Blind)
*Use this mode for quick checks when the original image is not available.*
1.  Navigate to the **Verify (Blind)** tab.
2.  Upload the **Suspect Image**.
3.  Click **Verify**.
4.  The system attempts to detect the `[INV]` header and decode the payload.

## 📚 API Documentation

Once the backend is running, interactive documentation is available at:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Core Endpoints
- `POST /api/v1/embed`: Embed text into an image.
- `POST /api/v1/extract`: Extract watermark using an original reference image (Alignment enabled).
- `POST /api/v1/verify`: Blind extraction without reference image.

## 🤖 Spec Kit Integration

This project uses **Spec Kit** for AI-driven development.

- **`/speckit.specify`**: Define new requirements.
- **`/speckit.plan`**: Generate technical plans.
- **`/speckit.tasks`**: Create implementation checklists.
- **`/speckit.implement`**: Execute code changes.

---

## 🇹🇼 專案架構與設計 (Project Architecture)

### 核心流程 (Pipeline)

1.  **感知層 (Perceptual Layer)**:
    -   利用 **Laplacian Filter** 計算圖像的紋理複雜度。
    -   生成 **HVS Mask**，在紋理複雜區域增強嵌入強度，平滑區域減弱強度，平衡隱蔽性與魯棒性。

2.  **嵌入層 (Embedding Layer)**:
    -   將圖像轉換為 YUV 色彩空間（僅處理 Y 通道）。
    -   進行 $8 \times 8$ 分塊 **DCT 變換**。
    -   將浮水印資訊（含 `[INV]` 標頭與長度位元）調變至中頻係數。

3.  **防禦層 (Defense Layer)**:
    -   **幾何校正 (Alignment)**: 使用 **ORB** 特徵點匹配與 **RANSAC** 算法計算單應性矩陣 (Homography)。
    -   **逆透視變換 (Un-warping)**: 將變形的截圖還原為正視圖，確保 DCT 網格對齊。

### 專案結構

```text
InvisiGuard/
├── backend/
│   ├── src/
│   │   ├── api/            # FastAPI Routes
│   │   ├── core/           # Core Algorithms
│   │   │   ├── embedding.py    # DCT & HVS Logic
│   │   │   ├── extraction.py   # Decoding Logic
│   │   │   └── geometry.py     # ORB & RANSAC Alignment
│   │   └── main.py         # App Entry Point
│   └── tests/              # Pytest Suites
├── frontend/
│   ├── src/
│   │   ├── components/     # React Components (Dropzone, ComparisonView)
│   │   ├── services/       # API Client
│   │   └── App.jsx         # Main UI Logic
│   └── index.html
└── specs/                  # Spec Kit Documentation
```

## 💡 核心演算法詳解 (Core Algorithm Details)

本節深入探討 InvisiGuard 的核心演算法，旨在提供一份清晰的技術文件，方便開發者學習與理解。

### 1. 浮水印嵌入 (Watermark Embedding / 加密流程)

嵌入過程的核心是將文字資訊轉換為位元流，並利用離散餘弦變換 (DCT) 將其隱藏在圖像的頻率中頻區域。此過程經過精心設計，以抵抗視覺偵測和常見的圖像處理攻擊。

**主要函式:** `backend.src.core.embedding.embed_watermark_dct`

**流程概覽:**

1.  **資訊預處理 (Payload Preparation)**:
    *   將使用者輸入的文字訊息轉換為位元流 (`text_to_bits`)。
    *   在訊息前方加入一個固定的標頭 `b'INV'` (InvisiGuard) 和訊息長度資訊。這個結構化的 Payload 使得在沒有原始圖像的情況下（盲驗證）也能夠定位和解碼浮水印。
    *   Payload 結構: `[Header: 3*8 bits][Length: 16 bits][Message: N bits]`

2.  **HVS 遮罩生成 (Human Visual System Mask)**:
    -   將圖像從 RGB 轉換為 YUV 色彩空間，僅對亮度 (Y) 通道進行操作，因為人眼對亮度的變化比色度更敏感。
    -   使用 **拉普拉斯濾波器 (Laplacian Filter)** 偵測圖像的邊緣和紋理。紋理複雜的區域（高頻）可以容納更強的浮水印而不易被察覺。
    -   生成一個與原圖大小相同的 HVS 遮罩，其值與紋理複雜度成正比。

3.  **分塊 DCT 變換 (Block-based DCT)**:
    -   將 Y 通道分割成 $8 \times 8$ 的小區塊。
    -   對每個區塊獨立執行 DCT，將其從空間域轉換為頻率域。DCT 係數表示了不同頻率的能量分佈，左上角為低頻（代表區塊的整體亮度），右下角為高頻（代表細節和噪點）。

4.  **係數調變 (Coefficient Modulation)**:
    -   遍歷每個 $8 \times 8$ 區塊的 **中頻 (mid-frequency)** DCT 係數。
    -   根據 Payload 的位元（0 或 1）和 HVS 遮罩的強度，對一對中頻係數進行微調，使其滿足特定的大小關係（例如，`coeff[i] > coeff[j]` 代表位元 1）。
    -   嵌入強度由基礎強度 `alpha` 和該區塊對應的 HVS 遮罩值共同決定，實現了**自適應強度嵌入 (Adaptive Strength Embedding)**。

5.  **同步模板嵌入 (Synchronization Template Embedding)**:
    -   為了實現盲驗證中的旋轉和縮放校正，系統會對整個圖像進行 **離散傅立葉變換 (DFT)**。
    -   在頻譜的特定位置生成多個峰值（Peaks），形成一個固定的幾何圖案。這個圖案在圖像被旋轉或縮放時會產生可預測的變化，從而在驗證階段可以反算出幾何變換的參數。
    -   此步驟是 **盲驗證 (Blind Verification)** 功能的基礎。

6.  **逆變換與儲存 (Inverse Transform & Save)**:
    -   對所有修改後的 $8 \times 8$ 區塊執行逆 DCT (IDCT)，將其從頻率域轉回空間域。
    -   將處理後的 Y 通道與原始的 UV 通道合併，轉換回 RGB 色彩空間，生成最終的浮水印圖像。

**主要參數詳解 (`embed` 服務):**

| 參數        | 類型    | 描述                                                                                                                             |
| :---------- | :------ | :------------------------------------------------------------------------------------------------------------------------------- |
| `image`     | `file`  | 上傳的原始圖像檔案 (PNG, JPEG)。                                                                                                 |
| `message`   | `string`| 要嵌入的秘密文字訊息。                                                                                                           |
| `alpha`     | `float` | 基礎嵌入強度。數值越高，浮水印越穩健，但視覺上可能越明顯。系統會結合 HVS 遮罩對其進行自適應調整。                |
| `password`  | `string`| (可選) 用於未來加密擴展的保留參數，目前未使用。                                                                                        |

---

### 2. 浮水印提取與驗證 (Watermark Extraction & Verification / 解密流程)

提取過程分為兩種模式，以應對不同的應用場景。

#### 模式一：非盲提取 (Non-Blind Extraction - 使用原始圖像)

此模式適用於可以拿到原始圖像作為參考的場景，例如驗證螢幕截圖或手機翻拍。它透過幾何校正來實現極高的提取精度和魯棒性。

**主要函式:** `backend.src.services.watermark.extract`, `backend.src.core.geometry.align_image`

**流程概覽:**

1.  **特徵匹配 (Feature Matching)**:
    -   使用 **ORB (Oriented FAST and Rotated BRIEF)** 演算法在原始圖像和待驗證圖像上分別偵測數百個關鍵特徵點及其描述符。ORB 演算法對旋轉和光照變化具有良好的不變性。

2.  **幾何校正 (Geometric Correction)**:
    -   使用 **RANSAC (Random Sample Consensus)** 演算法來匹配兩組特徵點，並從中計算出一個最優的 **單應性矩陣 (Homography Matrix)**。這個 $3 \times 3$ 的矩陣描述了從原始圖像到待驗證圖像的 **透視變換 (Perspective Transformation)**。
    -   RANSAC 能夠有效過濾掉特徵匹配中的錯誤匹配點，確保計算出的變換矩陣非常準確。

3.  **圖像對齊 (Image Alignment)**:
    -   應用計算出的單應性矩陣的**逆矩陣**，對待驗證圖像執行 **逆透視變換 (Inverse Perspective Transform / Un-warping)**。
    -   這一步會將被扭曲、旋轉或縮放的圖像「還原」到與原始圖像完全對齊的狀態。

4.  **浮水印提取 (Watermark Extraction)**:
    -   圖像對齊後，直接從校正後的圖像中提取浮水印。提取邏輯與嵌入相反，遍歷 $8 \times 8$ DCT 區塊，比較之前被調變過的中頻係數對的大小關係，從而還原出 Payload 的位元流。
    -   最後，將位元流轉換回文字 (`bits_to_text`) 並驗證 `[INV]` 標頭。

**主要參數詳解 (`extract` 服務):**

| 參數             | 類型   | 描述                                           |
| :--------------- | :----- | :--------------------------------------------- |
| `original_image` | `file` | 用於幾何校正參考的原始圖像檔案。               |
| `suspect_image`  | `file` | 待驗證的圖像檔案（例如螢幕截圖、翻拍照片等）。 |

#### 模式二：盲驗證 (Blind Verification - 無原始圖像)

此模式適用於無法取得原始圖像的場景，它依賴在嵌入階段加入的同步模板來校正幾何變換。

**主要函式:** `backend.src.services.watermark.verify`, `backend.src.core.geometry.detect_rotation_scale`

**流程概覽:**

1.  **同步模板偵測 (Sync Template Detection)**:
    -   對待驗證圖像執行 **DFT (離散傅立葉變換)**，得到其頻譜。
    -   在頻譜中搜尋嵌入階段加入的**同步模板峰值 (Sync Peaks)**。

2.  **幾何參數估算 (Geometry Parameter Estimation)**:
    -   比較偵測到的峰值位置與預設的模板位置，可以計算出圖像經歷的 **旋轉角度 (Rotation Angle)** 和 **縮放比例 (Scaling Factor)**。
    -   此方法對透視變換的校正能力有限，但對平面內的旋轉和縮放非常有效。

3.  **幾何校正 (Geometry Correction)**:
    -   根據估算出的旋轉角度和縮放比例，對待驗證圖像執行逆向的幾何變換，將其恢復到接近原始的狀態。

4.  **浮水印提取 (Watermark Extraction)**:
    -   在校正後的圖像上執行與非盲提取相同的 DCT 係數比較邏輯，還原出 Payload。
    -   由於沒有原始圖像，提取成功與否高度依賴 `[INV]` 標頭和長度資訊是否能被正確解碼。如果 Payload 結構不符，則驗證失敗。

**主要參數詳解 (`verify` 服務):**

| 參數            | 類型   | 描述                       |
| :-------------- | :----- | :------------------------- |
| `suspect_image` | `file` | 待驗證的圖像檔案。         |


