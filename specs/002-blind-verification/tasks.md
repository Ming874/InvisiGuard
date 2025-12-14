# Tasks: Blind Verification

**Feature**: Blind Verification (v002)
**Status**: Planned
**Spec**: [specs/002-blind-verification/spec.md](specs/002-blind-verification/spec.md)

## Phase 1: Setup
*Goal: Initialize new files and structures.*

- [x] T001 Create geometry module in [backend/src/core/geometry.py](backend/src/core/geometry.py)
- [x] T002 Create visualization module in [backend/src/core/visualization.py](backend/src/core/visualization.py)
- [x] T003 Create VerifyTab component in [frontend/src/components/VerifyTab.tsx](frontend/src/components/VerifyTab.tsx)

## Phase 2: Foundational
*Goal: Implement core algorithms for DFT alignment and visualization.*

- [x] T004 [P] Implement `SynchTemplate` class in [backend/src/core/geometry.py](backend/src/core/geometry.py)
- [x] T005 [P] Implement `embed_synch_template` function in [backend/src/core/geometry.py](backend/src/core/geometry.py)
- [x] T006 [P] Implement `detect_rotation_scale` function in [backend/src/core/geometry.py](backend/src/core/geometry.py)
- [x] T007 [P] Implement `correct_geometry` function in [backend/src/core/geometry.py](backend/src/core/geometry.py)
- [x] T008 [P] Implement `generate_signal_heatmap` in [backend/src/core/visualization.py](backend/src/core/visualization.py)

## Phase 3: User Story 1 - Blind Verification
*Goal: Enable verification of watermarks without the original image.*

- [x] T009 [US1] Update embedding logic to inject sync template in [backend/src/core/embedding.py](backend/src/core/embedding.py)
- [x] T010 [US1] Update extraction logic to use blind alignment in [backend/src/core/extraction.py](backend/src/core/extraction.py)
- [x] T011 [US1] Define `VerificationResult` model in [backend/src/api/routes.py](backend/src/api/routes.py)
- [x] T012 [US1] Implement `/verify` endpoint in [backend/src/api/routes.py](backend/src/api/routes.py)
- [x] T013 [US1] Add `verify` method to API service in [frontend/src/services/api.ts](frontend/src/services/api.ts)
- [x] T014 [US1] Implement `VerifyTab` UI logic in [frontend/src/components/VerifyTab.tsx](frontend/src/components/VerifyTab.tsx)
- [x] T015 [US1] Integrate `VerifyTab` into main app in [frontend/src/App.tsx](frontend/src/App.tsx)

## Phase 4: User Story 2 - Signal Map Visualization
*Goal: Visualize the watermark strength for the user.*

- [x] T016 [US2] Update `/embed` response to include signal map in [backend/src/api/routes.py](backend/src/api/routes.py)
- [x] T017 [US2] Add "Show Signal Map" toggle to [frontend/src/components/EmbedTab.tsx](frontend/src/components/EmbedTab.tsx)
- [x] T018 [US2] Implement heatmap overlay rendering in [frontend/src/components/EmbedTab.tsx](frontend/src/components/EmbedTab.tsx)

## Phase 5: Polish
*Goal: Error handling and UX improvements.*

- [x] T019 Add error handling for failed alignment in [backend/src/api/routes.py](backend/src/api/routes.py)
- [x] T020 Add loading states for verification in [frontend/src/components/VerifyTab.tsx](frontend/src/components/VerifyTab.tsx)

## Dependencies

1.  **US1 (Blind Verification)** depends on **Foundational** (Geometry logic).
2.  **US2 (Signal Map)** depends on **Foundational** (Visualization logic).

## Implementation Strategy

1.  **MVP**: Complete Phases 1, 2, and 3 to get the core blind verification working.
2.  **Enhancement**: Complete Phase 4 to add the visualization.
3.  **Polish**: Complete Phase 5.
