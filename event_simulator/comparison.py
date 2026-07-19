"""Validated metrics for comparing an accepted DES bound with actual latency."""

from dataclasses import dataclass, field
from math import isfinite
from numbers import Real


@dataclass(frozen=True)
class BoundComparison:
    """Validated time-domain metrics for one caller-accepted DES bound."""

    actual_time: float
    des_bound: float
    optimization_gap: float = field(init=False)
    hardware_efficiency: float = field(init=False)

    def __post_init__(self) -> None:
        actual = _require_positive_finite("actual_time", self.actual_time)
        bound = _require_positive_finite("des_bound", self.des_bound)
        if bound > actual:
            raise ValueError("des_bound must not exceed actual_time")

        object.__setattr__(self, "actual_time", actual)
        object.__setattr__(self, "des_bound", bound)
        object.__setattr__(self, "optimization_gap", (actual - bound) / actual)
        object.__setattr__(self, "hardware_efficiency", bound / actual)


def compare_des_bound(actual_time: Real, des_bound: Real) -> BoundComparison:
    """Compare a positive DES lower bound with a positive actual latency."""
    return BoundComparison(actual_time=actual_time, des_bound=des_bound)


def _require_positive_finite(name: str, value: Real) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not isfinite(value)
        or value <= 0
    ):
        raise ValueError(f"{name} must be finite and positive")
    return float(value)
