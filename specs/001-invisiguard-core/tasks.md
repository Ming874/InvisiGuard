# Implementation Tasks: InvisiGuard Core

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Status**: `24/24` Tasks Completed

## Phase 1: Foundation & API Skeleton
**Goal**: Establish the project structure and ensure frontend-backend communication.

- [x] T001 Setup FastAPI backend structure with `src/api`, `src/core`, `src/services` in `backend/`
- [x] T002 Setup React frontend with Vite and Tailwind CSS in `frontend/`
- [x] T003 [P] Define Pydantic models for `WatermarkRequest` and `ExtractionRequest` in `backend/src/api/schemas.py`
- [x] T004 [P] Implement `ImageProcessor` class for loading and resizing images in `backend/src/core/processor.py`
- [x] T005 Create basic `/health` endpoint to verify API status in `backend/src/api/routes.py`
- [x] T006 [P] Create `APIClient` service wrapper in `frontend/src/services/api.js`
- [x] T007 Verify end-to-end communication by displaying backend health status on frontend

## Phase 2: Core Watermarking (Embedding)
**Goal**: Implement the embedding pipeline with HVS masking and DCT.

- [x] T008 [US1] Implement `generate_log_mask` function using Laplacian filter in `backend/src/core/embedding.py`
- [x] T009 [US1] Implement `embed_watermark_dct` function with block-based DCT in `backend/src/core/embedding.py`
- [x] T010 [US1] Create `WatermarkService.embed` to orchestrate masking and embedding in `backend/src/services/watermark.py`
- [x] T011 [US1] Implement `POST /api/v1/embed` endpoint handling file upload and response in `backend/src/api/routes.py`
- [x] T012 [P] [US1] Create `Dropzone` component for image upload in `frontend/src/components/Dropzone.jsx`
- [x] T013 [P] [US1] Create `ConfigPanel` component for text and alpha input in `frontend/src/components/ConfigPanel.jsx`
- [x] T014 [US1] Implement `ComparisonView` to show original vs watermarked image in `frontend/src/components/ComparisonView.jsx`
- [x] T015 [US1] Implement `DiffMap` visualization using HTML5 Canvas pixel manipulation in `frontend/src/components/ComparisonView.jsx`

## Phase 3: Geometric Correction (The "God of War" Module)
**Goal**: Implement robust extraction with geometric alignment.

- [x] T016 [US2] Implement `extract_features_orb` using OpenCV ORB in `backend/src/core/geometry.py`
- [x] T017 [US2] Implement `align_image` using BFMatcher and RANSAC Homography in `backend/src/core/geometry.py`
- [x] T018 [US2] Implement `extract_watermark_dct` to recover bits from aligned image in `backend/src/core/extraction.py`
- [x] T019 [US2] Implement `POST /api/v1/extract` endpoint with alignment pipeline in `backend/src/api/routes.py`
- [x] T020 [P] [US2] Create `AttackSimulator` component with CSS transforms (rotate, scale) in `frontend/src/components/AttackSimulator.jsx`
- [x] T021 [US2] Implement extraction UI to upload original and suspect images in `frontend/src/App.jsx`

## Phase 4: Optimization & Polish
**Goal**: Tune algorithms for robustness and finalize documentation.

- [x] T022 Tune ORB parameters (`nfeatures`, `scaleFactor`) for better matching in `backend/src/core/geometry.py`
- [x] T023 Add error handling for invalid file types and processing errors in `backend/src/api/routes.py`
- [x] T024 Generate API documentation (Swagger/OpenAPI) and update `README.md` usage guide

## Dependencies
- Phase 2 requires Phase 1 (Basic structure)
- Phase 3 requires Phase 2 (Embedding logic needed to test extraction)
- Phase 4 requires Phase 3 (Optimization needs working pipeline)

## Implementation Strategy
- **MVP**: Complete Phase 1 & 2 to have a working "blind" watermarking tool.
- **Robustness**: Phase 3 is the critical differentiator; prioritize `align_image` accuracy.
- **Parallelism**: Frontend components (T012-T015, T020) can be built alongside backend logic.
