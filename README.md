# InvisiGuard

InvisiGuard is an invisible watermarking system that embeds textual data into digital images. The system leverages a combination of Discrete Wavelet Transform (DWT), Quantization Index Modulation (QIM), and Reed-Solomon error correction codes to ensure the watermark is both imperceptible and robust against various image manipulations.

## Key Features

- **Invisible Embedding**: Utilizes the Haar wavelet for DWT to embed watermarks in the low-frequency domain of the Y-channel, ensuring minimal visual distortion (PSNR > 40 dB).
- **Robust Error Correction**: Implements Reed-Solomon coding with 30 ECC symbols, capable of correcting up to 15-byte errors, which provides a ~6% error tolerance.
- **Cropping Resilience**: The watermark is embedded sequentially in the upper region of the image, making it resistant to cropping from the bottom and right edges.
- **Format-Specific Robustness**: The watermark is designed to survive lossless PNG compression. It is not resilient to JPEG compression.
- **Extraction and Verification**: Supports two modes of extraction: one requiring the original image for high-accuracy extraction and a "blind" verification mode that attempts extraction without the original image.
- **Interactive User Interface**: A React-based frontend provides a user-friendly dashboard for embedding and verifying watermarks, with features like side-by-side image comparison and quality metric displays (PSNR, SSIM).

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, OpenCV, PyWavelets, NumPy, reedsolo
- **Frontend**: React 18 (Vite), Tailwind CSS, Axios
- **Core Algorithms**: Discrete Wavelet Transform (DWT), Quantization Index Modulation (QIM), Reed-Solomon Error Correction

## Getting Started

### Prerequisites
- Python 3.11 or later
- Node.js 18 or later

### Backend Setup

```bash
cd backend
# Create and activate a virtual environment
python -m venv .venv
# On Windows
# .venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
# Install dependencies
pip install -r requirements.txt
# Run the server
python main.py
# The backend will be available at http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
# Install dependencies
npm install
# Start the development server
npm run dev
# The frontend will be available at http://localhost:5173
```

## Usage

### Embed Watermark
1.  Navigate to the **Embed Watermark** tab.
2.  Upload an image (PNG or JPEG).
3.  Enter the text to embed (up to 221 characters).
4.  Click **Embed**.
5.  Download the watermarked image. **It must be saved as a PNG file.**

### Extract Watermark (with Original Image)
1.  Navigate to the **Extract (With Original)** tab.
2.  Upload the original, unwatermarked image.
3.  Upload the watermarked PNG image.
4.  Click **Extract Watermark** to retrieve the embedded text.

### Verify Watermark (Blind Verification)
1.  Navigate to the **Verify (Blind)** tab.
2.  Upload the watermarked PNG image.
3.  Click **Verify** to attempt extraction without the original image.
    *Note: This mode has limitations and is not guaranteed to succeed if the image has been altered.*

## API Documentation

Interactive API documentation is available via Swagger UI and ReDoc when the backend is running:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Endpoints
- `POST /api/v1/embed`: Embeds text into an image.
- `POST /api/v1/extract`: Extracts a watermark by comparing against the original image.
- `POST /api/v1/verify`: Attempts to extract a watermark without the original image.

## Core Algorithm Details

The InvisiGuard watermarking scheme is built upon a combination of Discrete Wavelet Transform (DWT), Quantization Index Modulation (QIM), and Reed-Solomon error correction. This section provides a detailed explanation of the pipeline.

### 1. Algorithm Parameters

The behavior of the algorithm is controlled by the following key parameters:

```python
WAVELET = 'haar'          # Wavelet type for DWT
LEVEL = 1                 # Number of DWT decomposition levels
DELTA = 10.0              # QIM quantization step size, controlling embedding strength
N_ECC_SYMBOLS = 30        # Number of Reed-Solomon error correction symbols
RS_BLOCK_SIZE = 255       # Total size of the Reed-Solomon block in bytes
```

### 2. Watermark Embedding Pipeline

The embedding process, implemented in `backend.src.core.embedding.embed_watermark_dwt_qim`, follows these steps:

#### a. Payload Construction
A 255-byte data payload is constructed with the following structure:
- **Header (3 bytes)**: A magic string "INV" to identify the watermark.
- **Length (1 byte)**: The length of the embedded message.
- **Message (Variable)**: The user-provided text, with a maximum capacity of 221 characters.
- **Padding**: Null bytes to fill the remaining space.
- **ECC (30 bytes)**: Reed-Solomon error correction codes.

The payload is then encoded using the Reed-Solomon algorithm, making it resilient to bit-level errors.

#### b. Color Space Conversion
To minimize visual distortion, the watermark is embedded only in the luminance (brightness) component of the image. The input image is converted from the BGR color space to YUV. The Y channel is used for embedding, while the U and V (chrominance) channels are preserved.

#### c. Discrete Wavelet Transform (DWT)
A single-level DWT using the Haar wavelet is applied to the Y-channel. This decomposes the image into four sub-bands:
- **LL (Approximation)**: Low-frequency components, representing the main energy and structure of the image.
- **LH (Horizontal)**, **HL (Vertical)**, **HH (Diagonal)**: High-frequency components, representing edges and textures.

The watermark is embedded in the LL sub-band due to its perceptual significance and robustness to compression and noise.

#### d. Quantization Index Modulation (QIM)
QIM embeds the binary watermark data by modulating the quantization of the DWT coefficients. For each bit in the payload:
1.  A coefficient `c` is selected from the flattened LL sub-band.
2.  It is quantized to an index `q` using the formula: `q = round(c / DELTA)`.
3.  The parity of `q` is adjusted to match the bit to be embedded (0 for even, 1 for odd). If the parity does not match, `q` is adjusted by `+1` or `-1`.
4.  The modified coefficient is de-quantized: `c_new = q * DELTA`.

This process is repeated for all 2040 bits of the payload, embedding them sequentially into the first 2040 coefficients of the LL sub-band. This sequential placement enhances resistance to cropping from the image's bottom or right edges.

#### e. Reconstruction and Output
The modified Y-channel is reconstructed using an Inverse DWT (IDWT) with the modified LL sub-band and the original high-frequency sub-bands. The reconstructed Y-channel is then merged with the original U and V channels and converted back to BGR. The final watermarked image is saved in PNG format to preserve the integrity of the embedded data.

### 3. Watermark Extraction Pipeline

The extraction process, implemented in `backend.src.core.extraction.extract_watermark_dwt_qim`, reverses the embedding steps:

1.  **DWT Decomposition**: The watermarked image is processed identically to the embedding stage, applying a DWT to the Y-channel to obtain the LL sub-band.
2.  **QIM Extraction**: The first 2040 coefficients of the LL sub-band are processed. Each coefficient is quantized, and the embedded bit is determined from the parity of the quantization index (0 for even, 1 for odd).
3.  **Reed-Solomon Decoding**: The extracted bits are assembled into a 255-byte block and decoded using the Reed-Solomon algorithm, which can correct up to 15 bytes of errors.
4.  **Payload Parsing**: The corrected data is parsed to validate the "INV" header, read the message length, and extract the original text.

## Performance Metrics

- **Visual Quality**: PSNR is typically above 40 dB, and SSIM is greater than 0.98, indicating that the watermark is imperceptible.
- **Capacity**: The maximum message length is 221 characters.
- **Reliability**: Extraction is 100% successful for PNG images that have not undergone geometric transformations. The system can correct up to 15 bytes of errors.

## Limitations

- **Format Sensitivity**: The watermark does not survive JPEG compression.
- **Geometric Transformations**: The system does not support rotated or scaled images.
- **Cropping**: Significant cropping of the top or left sides of the image will result in extraction failure.

## License

This project is licensed under the MIT License.
