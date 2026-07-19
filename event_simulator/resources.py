from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from numbers import Real
from types import MappingProxyType
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from .events import EventGraph


@dataclass(frozen=True)
class ResourceConfig:
    """Chip-wide and replicated per-SM renewable resource capacities."""

    global_capacities: Mapping[str, int]
    sm_count: int
    per_sm_capacities: Mapping[str, int]

    def __post_init__(self) -> None:
        global_capacities = _freeze_capacities(
            self.global_capacities, "global resource"
        )
        per_sm_capacities = _freeze_capacities(
            self.per_sm_capacities, "per-SM resource"
        )
        if (
            isinstance(self.sm_count, bool)
            or not isinstance(self.sm_count, int)
            or self.sm_count <= 0
        ):
            raise ValueError("sm_count must be a positive integer")
        if set(global_capacities) & set(per_sm_capacities):
            raise ValueError("resource cannot be both global and per-SM")
        object.__setattr__(self, "global_capacities", global_capacities)
        object.__setattr__(self, "per_sm_capacities", per_sm_capacities)

    def validate_graph(self, graph: EventGraph) -> None:
        for event in graph.events:
            for resource, demand in event.global_demand.items():
                if resource not in self.global_capacities:
                    raise ValueError(f"unknown global resource: {resource}")
                if demand > self.global_capacities[resource]:
                    raise ValueError(f"global demand exceeds capacity: {resource}")
            for resource, demand in event.per_sm_demand.items():
                if resource not in self.per_sm_capacities:
                    raise ValueError(f"unknown per-SM resource: {resource}")
                if demand > self.per_sm_capacities[resource]:
                    raise ValueError(f"per-SM demand exceeds capacity: {resource}")
            if (
                event.eligible_sms is not None
                and max(event.eligible_sms) >= self.sm_count
            ):
                raise ValueError("eligible SM id is outside ResourceConfig")

        for lifetime in graph.lifetimes:
            for resource, reservation in lifetime.per_sm_reservation.items():
                if resource not in self.per_sm_capacities:
                    raise ValueError(f"unknown reservation resource: {resource}")
                if reservation > self.per_sm_capacities[resource]:
                    raise ValueError(
                        f"lifetime reservation exceeds per-SM capacity: {resource}"
                    )
            if (
                lifetime.eligible_sms is not None
                and max(lifetime.eligible_sms) >= self.sm_count
            ):
                raise ValueError("lifetime eligible SM id is outside ResourceConfig")


@dataclass(frozen=True)
class ResourceLifetime:
    """A per-SM occupancy reservation held across multiple Events."""

    lifetime_id: str
    acquire_event_id: str
    release_event_id: str
    per_sm_reservation: Mapping[str, int]
    eligible_sms: frozenset[int] | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("lifetime_id", self.lifetime_id),
            ("acquire_event_id", self.acquire_event_id),
            ("release_event_id", self.release_event_id),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"{name} must be a non-empty string")
        if self.acquire_event_id == self.release_event_id:
            raise ValueError("lifetime endpoints must be distinct")

        reservation = dict(self.per_sm_reservation)
        if not reservation:
            raise ValueError("per_sm_reservation must not be empty")
        for resource, quantity in reservation.items():
            if not isinstance(resource, str) or not resource:
                raise ValueError("resource names must be non-empty strings")
            if (
                isinstance(quantity, bool)
                or not isinstance(quantity, int)
                or quantity <= 0
            ):
                raise ValueError("reservation must be a positive integer")
        object.__setattr__(
            self,
            "per_sm_reservation",
            MappingProxyType(dict(sorted(reservation.items()))),
        )

        if self.eligible_sms is not None:
            eligible_sms = frozenset(self.eligible_sms)
            if not eligible_sms:
                raise ValueError("eligible_sms must not be empty")
            if any(
                isinstance(sm_id, bool)
                or not isinstance(sm_id, int)
                or sm_id < 0
                for sm_id in eligible_sms
            ):
                raise ValueError("eligible SM ids must be non-negative integers")
            object.__setattr__(self, "eligible_sms", eligible_sms)

    def transient_per_sm_demand(
        self, demand: Mapping[str, int]
    ) -> dict[str, int]:
        """Return demand not served by this lifetime's reservation."""

        return {
            resource: quantity
            for resource, quantity in demand.items()
            if resource not in self.per_sm_reservation
        }


def _freeze_capacities(
    capacities: Mapping[str, int], label: str
) -> Mapping[str, int]:
    normalized = dict(capacities)
    for resource, capacity in normalized.items():
        if not isinstance(resource, str) or not resource:
            raise ValueError("resource names must be non-empty strings")
        if (
            isinstance(capacity, bool)
            or not isinstance(capacity, int)
            or capacity <= 0
        ):
            raise ValueError(f"{label} capacity must be a positive integer: {resource}")
    return MappingProxyType(dict(sorted(normalized.items())))


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
