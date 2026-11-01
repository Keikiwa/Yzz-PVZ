# -*- coding: utf-8 -*-
"""Pure domain mathematical utilities without third-party dependencies."""

from typing import Tuple


def clamp(value: float, low: float, high: float) -> float:
    """Clamp value within [low, high] bounds."""
    return max(low, min(high, value))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * clamp(t, 0.0, 1.0)


def lerp_color(
    c1: Tuple[int, int, int], c2: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    """Linear interpolation between two RGB color tuples."""
    factor = clamp(t, 0.0, 1.0)
    return (
        int(c1[0] + (c2[0] - c1[0]) * factor),
        int(c1[1] + (c2[1] - c1[1]) * factor),
        int(c1[2] + (c2[2] - c1[2]) * factor),
    )
