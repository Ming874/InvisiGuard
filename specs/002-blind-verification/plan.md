# Implementation Plan: Blind Verification

**Branch**: `feature/002-blind-verification` | **Date**: 2025-12-14 | **Spec**: [specs/002-blind-verification/spec.md](specs/002-blind-verification/spec.md)
**Input**: Feature specification from `/specs/002-blind-verification/spec.md`

## Summary

Implement blind watermark verification (no original image required) using DFT Synchronization Templates for geometric alignment. Add a "Signal Map" visualization to the frontend to show embedding strength.

## Technical Context

**Language/Version**: Python 3.10+ (Backend), TypeScript/React (Frontend)
**Primary Dependencies**: FastAPI, OpenCV (headless), NumPy, SciPy
**Storage**: N/A (Stateless processing)
**Testing**: pytest (Backend), Jest/Vitest (Frontend)
**Target Platform**: Web Browser (Client), Linux/Container (Server)
**Project Type**: Web application
**Performance Goals**: Verification < 2 seconds for 1080p images.
**Constraints**: Must handle rotation (+/- 180 deg) and scale (0.5x - 2.0x).

## Constitution Check

*GATE: Passed.*

1.  **No Breaking Changes**: New endpoint `/verify` is additive. Existing `/embed` and `/extract` remain unchanged (though `/embed` will now inject the template).
2.  **Performance**: DFT is $O(N \log N)$, suitable for real-time use.
3.  **Privacy**: No data persistence.

## Project Structure

### Documentation (this feature)

```text
specs/002-blind-verification/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── verify-endpoint.yaml
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   └── routes.py        # Add /verify endpoint
│   ├── core/
│   │   ├── embedding.py     # Update to inject Synch Template
│   │   ├── extraction.py    # Update to use blind alignment
│   │   ├── geometry.py      # NEW: DFT alignment logic
│   │   └── visualization.py # NEW: Heatmap generation
│   └── main.py
└── tests/
    └── test_blind_verify.py

frontend/
├── src/
│   ├── components/
│   │   ├── EmbedTab.tsx     # Add "Show Signal Map" toggle
│   │   ├── VerifyTab.tsx    # NEW: Blind verification UI
│   ├── services/
│   │   └── api.ts           # Add verify() method
│   └── App.tsx
```

**Structure Decision**: Standard Web Application (Backend/Frontend split).

## Complexity Tracking

*No violations.*
