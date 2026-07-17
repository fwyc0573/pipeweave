from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class ResourceConfig:
    """Parallel lane capacity for each explicitly modeled resource."""

    capacities: Mapping[str, int]

    def __post_init__(self) -> None:
        normalized = dict(self.capacities)
        for resource, capacity in normalized.items():
            if not isinstance(resource, str) or not resource:
                raise ValueError("resource names must be non-empty strings")
            if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
                raise ValueError(
                    f"resource capacity must be a positive integer: {resource}"
                )
        object.__setattr__(self, "capacities", MappingProxyType(normalized))


@dataclass(frozen=True)
class PrimitiveCalibration:
    """Measured or analytical duration per primitive work unit.

    Each coefficient is multiplied by the explicit work quantity supplied by an
    operator lowering. No learned model or implicit default is used.
    """

    duration_per_unit: Mapping[str, float]

    def __post_init__(self) -> None:
        normalized = dict(self.duration_per_unit)
        for event_type, duration in normalized.items():
            if not isinstance(event_type, str) or not event_type:
                raise ValueError("calibration keys must be non-empty strings")
            if (
                isinstance(duration, bool)
                or not isinstance(duration, Real)
                or not isfinite(duration)
                or duration < 0.0
            ):
                raise ValueError(
                    f"primitive duration must be finite and non-negative: {event_type}"
                )
        object.__setattr__(
            self, "duration_per_unit", MappingProxyType(normalized)
        )

    def duration(self, event_type: str, quantity: int | float = 1) -> float:
        if event_type not in self.duration_per_unit:
            raise ValueError(f"missing primitive calibration: {event_type}")
        if isinstance(quantity, bool) or not isinstance(quantity, (int, float)):
            raise ValueError("calibration quantity must be numeric")
        if not isfinite(quantity) or quantity < 0:
            raise ValueError("calibration quantity must be finite and non-negative")
        return self.duration_per_unit[event_type] * quantity
