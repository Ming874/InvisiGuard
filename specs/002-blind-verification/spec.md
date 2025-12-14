# Feature Specification: Blind Watermark Verification

**Feature Branch**: `002-blind-verification`
**Created**: 2025-12-14
**Status**: Draft
**Input**: User request for blind verification and enhanced UI.

## User Scenarios & Testing

### User Story 1 - Blind Verification (Priority: P1)

As a content creator or platform administrator, I want to verify if a suspicious image (screenshot or resized) contains my watermark by uploading *only* the suspicious image, so that I can detect infringement without needing to locate the exact original source file.

**Why this priority**: This removes a major friction point (needing the original) and enables automated crawling/detection scenarios.

**Independent Test**:
1.  Embed watermark in Image A.
2.  Take a screenshot of Image A (Image A').
3.  Upload *only* Image A' to the `/verify` endpoint.
4.  System returns "Verified: True" and the extracted payload.

**Acceptance Scenarios**:
1.  **Given** a watermarked image that has been resized to 50%, **When** I upload it to the verification page, **Then** the system detects the watermark and extracts the text.
2.  **Given** a non-watermarked image, **When** I upload it, **Then** the system returns "No watermark detected".

### User Story 2 - High-Contrast Watermark Visualization (Priority: P2)

As a user embedding a watermark, I want to see a high-contrast "heat map" of where the watermark signal is being added, so that I can understand how the "Strength" ($\alpha$) parameter affects the image and ensure it's concentrated in textured areas (HVS).

**Why this priority**: Improves trust and usability. Users can "see" the invisible protection.

**Independent Test**:
1.  Upload image to Embed page.
2.  Adjust $\alpha$ slider.
3.  See a "Watermark Signal" view that shows bright pixels where the embedding is strong and black where it is zero.

**Acceptance Scenarios**:
1.  **Given** an image with smooth sky and textured ground, **When** I view the signal map, **Then** the ground area should be bright (high signal) and the sky should be dark (low signal).

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a `/api/v1/verify` endpoint that accepts a single image file.
- **FR-002**: System MUST implement a blind alignment or robust extraction algorithm that does not require the original image.
    - *Note*: This may involve embedding a synchronization template (e.g., FFT peaks) or using a rotation-invariant domain (e.g., Log-Polar DCT).
- **FR-003**: Frontend MUST provide a "Verify" tab that allows single-image upload.
- **FR-004**: Frontend MUST provide a "Signal Map" visualization in the Embed tab (distinct from the simple Diff Map, potentially normalized for visibility).
- **FR-005**: System MUST support downloading the processed image (already implemented, but ensure it's robust).

### Technical Constraints & Decisions

- **Blind Alignment**: Implementing full blind geometric correction is complex.
    - *Strategy*: We will investigate embedding a **Synchronization Signal** (e.g., 4 peaks in the DFT magnitude spectrum) during the embedding phase.
    - *Detection*: During verification, we detect these peaks to estimate rotation/scale *before* extracting the DCT payload.
- **Fallback**: If blind alignment is too unreliable for the MVP, we may focus on **Scale Invariance** (using Log-Polar or multi-scale search) and **Rotation Invariance** (brute-force search or Radon transform) if performance permits.
- **Library**: We may leverage `invisible-watermark`'s `dwtDct` method if it offers better blind robustness than our custom DCT, or enhance our custom DCT with a sync template.

### Key Entities

- **VerificationResult**: `{ is_watermarked: bool, payload: str, confidence: float, metadata: dict }`
