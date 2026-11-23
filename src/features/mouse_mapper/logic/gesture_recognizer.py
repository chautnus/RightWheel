"""Streaming Incremental Vector Quantizer for 8-direction mouse gestures (Touchpad Gesture Parity)."""
from __future__ import annotations

from collections import deque
import itertools
import math
from typing import Any

SECTORS = ["R", "DR", "D", "DL", "L", "UL", "U", "UR"]
CARDINALS = {"R", "D", "L", "U"}
DIAGONALS = {"DR", "DL", "UL", "UR"}
OPPOSITE_CARDINALS = {
    "R": "L",
    "L": "R",
    "U": "D",
    "D": "U",
}

_COLLAPSE_TRIPLETS: set[tuple[str, str, str]] = {
    # 90° Orthogonal corners (corner rounding)
    ("R", "DR", "D"),
    ("D", "DR", "R"),
    ("D", "DL", "L"),
    ("L", "DL", "D"),
    ("L", "UL", "U"),
    ("U", "UL", "L"),
    ("U", "UR", "R"),
    ("R", "UR", "U"),
    # 180° Turnaround arcs (U-turn looping)
    ("R", "UL", "L"),
    ("R", "UR", "L"),
    ("R", "DL", "L"),
    ("R", "DR", "L"),
    ("L", "UL", "R"),
    ("L", "UR", "R"),
    ("L", "DL", "R"),
    ("L", "DR", "R"),
    ("U", "UL", "D"),
    ("U", "UR", "D"),
    ("U", "DL", "D"),
    ("U", "DR", "D"),
    ("D", "UL", "U"),
    ("D", "UR", "U"),
    ("D", "DL", "U"),
    ("D", "DR", "U"),
}


def _are_adjacent_45(a: str, b: str) -> bool:
    """Return True if sectors a and b are exactly 45° apart on the 8-sector wheel."""
    if a not in SECTORS or b not in SECTORS:
        return False
    ia, ib = SECTORS.index(a), SECTORS.index(b)
    n = len(SECTORS)
    return min((ia - ib) % n, (ib - ia) % n) == 1


def _is_effectively_single_stroke(directions: list[str]) -> bool:
    """True when every consecutive pair in `directions` is an ADJACENT sector (45° apart).

    Real human strokes rarely travel in a mathematically straight line — natural hand
    curvature during a single stroke often crosses a 45°-sector boundary (e.g. D -> DR,
    or UL -> U), producing 2+ distinct entries even though only ONE simple stroke was intended.
    Only a REAL direction change (>=90° turn between consecutive segments) indicates a genuine
    compound/drawn shape.
    """
    if len(directions) < 2:
        return True
    n = len(SECTORS)
    for a, b in zip(directions, directions[1:]):
        ia, ib = SECTORS.index(a), SECTORS.index(b)
        circular_dist = min((ia - ib) % n, (ib - ia) % n)
        if circular_dist >= 2:
            return False
    return True


def normalize_directions(directions: list[str]) -> list[str]:
    """Collapse intermediate diagonal noise at orthogonal corners, U-turns, and stroke entry/exit.

    5-Layer Filtering adopted from Touchpad Gesture:
    1. Touchdown entry wobble (e.g. ['DR', 'R'] -> ['R'])
    2. Lift-off trailing wobble (e.g. ['R', 'DL'] -> ['R'])
    3. Multi-segment U-turn arcs between opposite cardinal directions
    4. 24 orthogonal 90° corner & 180° turnaround templates
    5. Sandwiched wobble between identical cardinals (e.g. ['D', 'DR', 'D'] -> ['D'])
    """
    if len(directions) < 2:
        return list(directions)

    res = [k for k, _ in itertools.groupby(directions)]

    # 1. Strip leading entry diagonal noise if immediately followed by adjacent cardinal
    if len(res) >= 2 and res[0] in DIAGONALS and res[1] in CARDINALS and _are_adjacent_45(res[0], res[1]):
        res.pop(0)

    # 2. Strip trailing lift-off diagonal noise if immediately preceded by adjacent cardinal
    if len(res) >= 2 and res[-1] in DIAGONALS and res[-2] in CARDINALS and _are_adjacent_45(res[-1], res[-2]):
        res.pop()

    # 3. Collapse multi-segment U-turn arcs between opposite cardinal directions
    # (e.g. ['R', 'UR', 'UL', 'L'] -> ['R', 'L'] or ['D', 'DR', 'DL', 'U'] -> ['D', 'U'])
    i = 0
    while i <= len(res) - 4:
        start_sec = res[i]
        if start_sec in OPPOSITE_CARDINALS:
            target_sec = OPPOSITE_CARDINALS[start_sec]
            if res[i + 3] == target_sec and res[i + 1] in DIAGONALS and res[i + 2] in DIAGONALS:
                del res[i + 1:i + 3]
                continue
        i += 1

    # 4. Collapse intermediate diagonal noise at orthogonal corners & U-turns (24 templates)
    changed = True
    while changed:
        changed = False
        i = 0
        while i <= len(res) - 3:
            triplet = (res[i], res[i + 1], res[i + 2])
            # Check 24 templates OR sandwiched diagonal between identical cardinals
            if triplet in _COLLAPSE_TRIPLETS or (res[i] == res[i + 2] and res[i + 1] in DIAGONALS):
                res.pop(i + 1)
                changed = True
            else:
                i += 1

    # 5. Final check for trailing/leading diagonal after collapse
    if len(res) >= 2 and res[-1] in DIAGONALS and res[-2] in CARDINALS and _are_adjacent_45(res[-1], res[-2]):
        res.pop()
    if len(res) >= 2 and res[0] in DIAGONALS and res[1] in CARDINALS and _are_adjacent_45(res[0], res[1]):
        res.pop(0)

    return [k for k, _ in itertools.groupby(res)]


class GestureRecognizer:
    """Recognizes mouse gestures using streaming vector quantization with Touchpad Gesture parity.

    Directions: U, D, L, R, UR, DR, DL, UL (quantized into 45-degree sectors).
    Consecutive duplicate directions are compressed and smoothed.
    """

    def __init__(self, threshold: int = 22, maxlen: int = 300) -> None:
        self.threshold = threshold
        self.maxlen = maxlen
        self._points: deque[tuple[int, int]] = deque(maxlen=maxlen)
        self._directions: list[str] = []
        self._direction_steps: list[int] = []
        self._anchor: tuple[int, int] | None = None

    def reset(self) -> None:
        """Clear coordinates buffer and accumulated directions."""
        self._points.clear()
        self._directions.clear()
        self._direction_steps.clear()
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
                    "line": 139,
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
                    self._direction_steps.append(1)
                    stroke_added = True
                else:
                    if self._direction_steps:
                        self._direction_steps[-1] += 1
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

        Applies Touchpad Gesture parity:
        - Lead-in and lift-off single-step wobble pruning
        - 5-layer normalize_directions
        - Single-stroke Euclidean geometry & dominant displacement axis fallback
        - Multi-stroke compound matching
        """
        if not isinstance(presets, list):
            return {
                "ok": False,
                "error": {
                    "code": "INVALID_PRESETS",
                    "file": __file__,
                    "line": 185,
                    "helper": "Presets must be a list of dictionaries",
                },
            }

        # ── 0. Lead-in and lift-off single-step tremor pruning ─────────────────
        # When a user clicks and holds RMB, the mechanical pressure often nudges the
        # cursor 1 step (<25px) in an arbitrary direction before the intended stroke starts.
        # If the first segment is only 1 step and the following segment is >= 2 steps,
        # prune the leading tremor. Same for trailing lift-off wobble upon button release.
        dirs_to_norm = list(self._directions)
        steps = list(self._direction_steps)
        if len(dirs_to_norm) >= 2 and len(steps) >= 2 and steps[0] == 1 and steps[1] >= 2:
            dirs_to_norm.pop(0)
            steps.pop(0)
        if len(dirs_to_norm) >= 2 and len(steps) >= 2 and steps[-1] == 1 and steps[-2] >= 2:
            dirs_to_norm.pop(-1)
            steps.pop(-1)

        current_dirs = normalize_directions(dirs_to_norm)

        # ── Dominant Displacement Axis & Euclidean Geometry Fallback ──────────
        # When gesture is a single straight stroke (or natural hand slant crossing 45° sectors),
        # use the net displacement vector from start point to end point so human gestures 100% trigger.
        tot_dx = 0
        tot_dy = 0
        tot_dist = 0.0
        path_len = 0.0
        if len(self._points) >= 2:
            p0 = self._points[0]
            pn = self._points[-1]
            tot_dx = pn[0] - p0[0]
            tot_dy = pn[1] - p0[1]
            tot_dist = math.hypot(tot_dx, tot_dy)
            pts_list = list(self._points)
            for p_a, p_b in zip(pts_list, pts_list[1:]):
                path_len += math.hypot(p_b[0] - p_a[0], p_b[1] - p_a[1])

        disp_ratio = (tot_dist / path_len) if path_len > 0 else 0.0

        single_stroke_dir: str | None = None
        # Geometrically, in an orthogonal 90° corner (L-shape), the ratio of displacement
        # to path length is at most sqrt(2)/2 ≈ 0.707. Therefore, any path with ratio >= 0.70
        # is mathematically proven to be a single straight stroke with minor tremor.
        if tot_dist >= self.threshold and (
            len(current_dirs) <= 1
            or _is_effectively_single_stroke(current_dirs)
            or disp_ratio >= 0.70
        ):
            if abs(tot_dy) >= abs(tot_dx):
                single_stroke_dir = "D" if tot_dy > 0 else "U"
            else:
                single_stroke_dir = "R" if tot_dx > 0 else "L"

        # Match presets
        for preset in presets:
            if not isinstance(preset, dict) or not preset.get("enabled", True):
                continue

            preset_dirs = preset.get("directions")
            if not preset_dirs:
                shape = str(preset.get("shape") or preset.get("direction") or "").strip()
                if shape:
                    if "_" in shape:
                        preset_dirs = [d.strip().upper() for d in shape.split("_") if d.strip()]
                    elif len(shape) <= 2 and shape.upper() in SECTORS:
                        preset_dirs = [shape.upper()]
                    else:
                        preset_dirs = list(shape.upper())

            if not preset_dirs:
                continue

            norm_preset = normalize_directions(preset_dirs)

            # Check 1: exact normalized sector match
            matched = (norm_preset == current_dirs)

            # Check 2: single stroke dominant displacement fallback
            if not matched and single_stroke_dir and norm_preset == [single_stroke_dir]:
                matched = True

            if matched:
                keys = str(preset.get("keys") or preset.get("target") or "")
                return {
                    "ok": True,
                    "data": {
                        "matched": True,
                        "keys": keys,
                        "preset": preset,
                        "directions": norm_preset,
                        "raw_directions": list(self._directions),
                    },
                }

        return {
            "ok": True,
            "data": {
                "matched": False,
                "keys": "",
                "directions": current_dirs,
                "raw_directions": list(self._directions),
            },
        }
