# Data Model: Blind Verification

## In-Memory Structures

### Synchronization Template
Used for blind geometric alignment.

```python
class SynchTemplate:
    radius: int = 50          # Radius in frequency domain
    angle: float = 45.0       # Base angle in degrees
    strength: float = 5.0     # Magnitude multiplier for peaks
    peak_width: int = 3       # Size of the peak in pixels
```

### Verification Result
Return object for the verification endpoint.

```python
class VerificationResult:
    verified: bool
    watermark_text: str | None
    confidence: float         # 0.0 to 1.0
    geometry_corrected: bool  # True if rotation/scale was fixed
    detected_rotation: float  # Degrees
    detected_scale: float     # Scale factor
```

## Database Schema
*No changes required.*
