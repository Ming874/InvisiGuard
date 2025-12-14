# Research: Blind Verification & Visualization

**Feature**: Blind Watermark Verification
**Date**: 2025-12-14
**Status**: Approved

## 1. Blind Alignment Strategy

### Problem
To verify a watermark in a screenshot or resized image without the original, we need to correct geometric distortions (Rotation, Scale) blindly. The previous ORB-based approach required the original image for feature matching.

### Options Considered
1.  **Synchronization Templates (DFT Peaks)**: Embedding strong peaks in the frequency domain (DFT) that act as "guide stars" for alignment.
2.  **Log-Polar Transform (Fourier-Mellin)**: Converting rotation/scale to translation in a log-polar domain.
3.  **Autocorrelation Function (ACF)**: Using the periodic nature of the watermark grid to detect geometric changes.

### Decision: Synchronization Templates (DFT Peaks)
We will embed a "constellation" of 4 symmetric peaks in the mid-frequency band of the DFT magnitude spectrum.

**Rationale**:
-   **Efficiency**: FFT is fast ($O(N \log N)$), suitable for web APIs.
-   **Robustness**: Frequency peaks survive compression and noise better than spatial features.
-   **Simplicity**: Easier to implement and debug than Fourier-Mellin.
-   **Compatibility**: Can be layered on top of the existing DCT payload embedding (Template handles geometry, DCT handles data).

**Implementation Details**:
-   **Embedding**: Add energy to 4 symmetric points in the DFT magnitude spectrum (e.g., at 45°, 135°, 225°, 315° with radius $R$).
-   **Detection**: Compute DFT of suspect image -> Find local maxima -> Calculate rotation angle $\theta$ and scale factor $s$ based on the shift of these peaks.
-   **Correction**: Inverse rotate/scale the image before passing it to the DCT extractor.

## 2. High-Contrast Visualization

### Problem
Users need to understand "where" the watermark is hidden. The current "Diff Map" (pixel difference) is often too subtle (mostly black) because the changes are invisible by design.

### Decision: HVS Heatmap
We will visualize the **Human Visual System (HVS) Mask** (the `alpha_map`) rather than the raw pixel difference.

**Rationale**:
-   **Meaningful**: Shows the *potential* embedding strength, which correlates with image texture.
-   **Visibility**: The mask has a wider dynamic range than the subtle pixel differences.
-   **Feedback**: Directly shows the effect of the "Strength" slider.

**Implementation Details**:
-   Normalize the `alpha_map` (float) to 0-255.
-   Apply a false-color map (e.g., `cv2.COLORMAP_JET` or `cv2.COLORMAP_HOT`).
-   Overlay on the original image with transparency (e.g., 30% heatmap, 70% original).

## 3. Verification Endpoint

### Decision: `/api/v1/verify`
A new endpoint dedicated to blind verification.

**Contract**:
-   **Input**: Single file (`suspect_file`).
-   **Process**:
    1.  Load image.
    2.  **Blind Alignment**: Detect DFT peaks -> Correct Geometry.
    3.  **Extraction**: Run DCT extraction on corrected image.
-   **Output**: Boolean `verified`, `decoded_text`, and `confidence`.

## 4. Technical Stack Updates
-   **Backend**: No new libraries needed (OpenCV/NumPy suffice).
-   **Frontend**: New "Verify" tab and "Signal Map" toggle in Embed tab.
