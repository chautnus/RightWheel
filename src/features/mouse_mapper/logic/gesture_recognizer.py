"""Streaming Incremental Vector Quantizer for 8-direction mouse gestures."""
from collections import deque
import math
from typing import Any

SECTORS = ["R", "DR", "D", "DL", "L", "UL", "U", "UR"]


class GestureRecognizer:
    """Recognizes 8-direction mouse gestures using streaming vector quantization.

    Directions: U, D, L, R, UR, DR, DL, UL (quantized into 45-degree sectors).
    Consecutive duplicate directions are compressed.
    """

    def __init__(self, threshold: int = 18, maxlen: int = 200) -> None:
        self.threshold = threshold
        self.maxlen = maxlen
        self._points: deque[tuple[int, int]] = deque(maxlen=maxlen)
        self._directions: list[str] = []
        self._anchor: tuple[int, int] | None = None

    def reset(self) -> None:
        """Clear coordinates buffer and accumulated directions."""
        self._points.clear()
        self._directions.clear()
        self._anchor = None

    def feed_point(self, x: int, y: int) -> dict[str, Any]:
        """Feed a new coordinate point.

        Returns contract:
            {ok: True, data: {"points_count": int, "stroke_added": bool}}
            | {ok: False, error: {code: "INVALID_COORDS", file, line, helper}}
        """
        if type(x) is not int or type(y) is not int:
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_COORDS",
                    "file": __file__,
                    "line": 39,
                    "helper": "Coordinates x and y must be integers",
                },
            }

        self._points.append((x, y))
        stroke_added = False

        if self._anchor is None:
            self._anchor = (x, y)
        else:
            dx = x - self._anchor[0]
            dy = y - self._anchor[1]
            dist = math.hypot(dx, dy)
            if dist >= self.threshold:
                deg = math.degrees(math.atan2(dy, dx))
                idx = int(((deg + 22.5) % 360) // 45) % 8
                direction = SECTORS[idx]
                if not self._directions or self._directions[-1] != direction:
                    self._directions.append(direction)
                    stroke_added = True
                self._anchor = (x, y)

        return {
            "ok": True,
            "data": {
                "points_count": len(self._points),
                "stroke_added": stroke_added,
            },
        }

    def finish(self, presets: list[dict[str, Any]]) -> dict[str, Any]:
        """Match accumulated directions against enabled presets.

        Returns contract:
            {ok: True, data: {"matched": bool, "keys": str, "directions": list[str]}}
            | {ok: False, error: {code, ...}}
        """
        if not isinstance(presets, list):
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_PRESETS",
                    "file": __file__,
                    "line": 78,
                    "helper": "Presets must be a list of dictionaries",
                },
            }

        current_dirs = list(self._directions)
        for preset in presets:
            if not isinstance(preset, dict):
                continue
            if preset.get("enabled", True) and preset.get("directions") == current_dirs:
                return {
                    "ok": True,
                    "data": {
                        "matched": True,
                        "keys": str(preset.get("keys", "")),
                        "directions": current_dirs,
                    },
                }

        return {
            "ok": True,
            "data": {
                "matched": False,
                "keys": "",
                "directions": current_dirs,
            },
        }
