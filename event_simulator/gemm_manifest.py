"""Authoritative GEMM launch policy and work-conservation manifest."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from .cache import (
    CacheAccess,
    CacheConfig,
    CacheResolution,
    InitialCacheState,
    resolve_cache,
)
from .resources import ResourceConfig


@dataclass(frozen=True)
class GemmWorker:
    """One CTA worker and its ordered work assignment."""

    worker_id: str
    work_item_ids: tuple[str, ...]
    per_sm_reservation: Mapping[str, int]
    eligible_sms: frozenset[int] | None = None

    def __post_init__(self) -> None:
        _require_identifier("worker_id", self.worker_id)
        work_item_ids = _identifier_tuple(
            "work_item_ids",
            self.work_item_ids,
            allow_empty=False,
        )
        if len(set(work_item_ids)) != len(work_item_ids):
            raise ValueError("work_item_ids must not contain duplicates")
        object.__setattr__(self, "work_item_ids", work_item_ids)

        reservation = dict(self.per_sm_reservation)
        if not reservation:
            raise ValueError("per_sm_reservation must not be empty")
        for resource, quantity in reservation.items():
            _require_identifier("reservation resource", resource)
            _require_positive_integer("reservation", quantity)
        object.__setattr__(
            self,
            "per_sm_reservation",
            MappingProxyType(dict(sorted(reservation.items()))),
        )

        if self.eligible_sms is not None:
            eligible_sms = frozenset(self.eligible_sms)
            if not eligible_sms:
                raise ValueError("eligible_sms must not be empty")
            for sm_id in eligible_sms:
                _require_non_negative_integer("eligible SM", sm_id)
            object.__setattr__(self, "eligible_sms", eligible_sms)


@dataclass(frozen=True)
class GemmWorkItem:
    """One explicit output-tile and logical-K work partition."""

    work_item_id: str
    output_m: int
    output_n: int
    logical_m: int
    logical_n: int
    k_start: int
    k_end: int
    issued_m: int
    issued_n: int
    issued_k: int
    accumulator_id: str
    cache_access_indices: tuple[int, ...]

    def __post_init__(self) -> None:
        _require_identifier("work_item_id", self.work_item_id)
        _require_identifier("accumulator_id", self.accumulator_id)
        _require_non_negative_integer("output_m", self.output_m)
        _require_non_negative_integer("output_n", self.output_n)
        _require_positive_integer("logical_m", self.logical_m)
        _require_positive_integer("logical_n", self.logical_n)
        _require_non_negative_integer("k_start", self.k_start)
        _require_positive_integer("k_end", self.k_end)
        if self.k_end <= self.k_start:
            raise ValueError("logical K range must be non-empty")
        _require_positive_integer("issued_m", self.issued_m)
        _require_positive_integer("issued_n", self.issued_n)
        _require_positive_integer("issued_k", self.issued_k)
        if (
            self.issued_m < self.logical_m
            or self.issued_n < self.logical_n
            or self.issued_k < self.logical_k
        ):
            raise ValueError("issued extents must cover logical extents")
        access_indices = _access_index_tuple(self.cache_access_indices)
        if not access_indices:
            raise ValueError("cache_access_indices must not be empty")
        object.__setattr__(self, "cache_access_indices", access_indices)

    @property
    def logical_k(self) -> int:
        return self.k_end - self.k_start

    @property
    def logical_work(self) -> int:
        return 2 * self.logical_m * self.logical_n * self.logical_k

    @property
    def physical_issued_work(self) -> int:
        return 2 * self.issued_m * self.issued_n * self.issued_k

    @property
    def logical_elements(self) -> int:
        return self.logical_m * self.logical_n

    @property
    def issued_elements(self) -> int:
        return self.issued_m * self.issued_n


@dataclass(frozen=True)
class GemmReductionStep:
    """One explicit accumulator reduction node."""

    reduction_id: str
    input_accumulator_ids: tuple[str, ...]
    output_accumulator_id: str
    logical_elements: int
    issued_elements: int
    dependencies: tuple[str, ...] = ()
    cache_access_indices: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        _require_identifier("reduction_id", self.reduction_id)
        _require_identifier("output_accumulator_id", self.output_accumulator_id)
        inputs = _identifier_tuple(
            "input_accumulator_ids",
            self.input_accumulator_ids,
            allow_empty=False,
        )
        if len(inputs) < 2:
            raise ValueError("reduction requires at least two inputs")
        if len(set(inputs)) != len(inputs):
            raise ValueError("reduction inputs must not contain duplicates")
        if self.output_accumulator_id in inputs:
            raise ValueError("reduction output cannot also be an input")
        object.__setattr__(self, "input_accumulator_ids", inputs)

        _require_positive_integer("logical_elements", self.logical_elements)
        _require_positive_integer("issued_elements", self.issued_elements)
        if self.issued_elements < self.logical_elements:
            raise ValueError("issued_elements must cover logical_elements")

        dependencies = _identifier_tuple(
            "dependencies",
            self.dependencies,
            allow_empty=True,
        )
        if len(set(dependencies)) != len(dependencies):
            raise ValueError("reduction dependencies must not contain duplicates")
        object.__setattr__(self, "dependencies", tuple(sorted(dependencies)))
        object.__setattr__(
            self,
            "cache_access_indices",
            _access_index_tuple(self.cache_access_indices),
        )

    @property
    def logical_work(self) -> int:
        return (len(self.input_accumulator_ids) - 1) * self.logical_elements

    @property
    def physical_issued_work(self) -> int:
        return (len(self.input_accumulator_ids) - 1) * self.issued_elements


@dataclass(frozen=True)
class GemmLaunchManifest:
    """One complete, authoritative GEMM launch and cache-access manifest."""

    m: int
    n: int
    k: int
    a_element_bytes: int
    b_element_bytes: int
    output_element_bytes: int
    accumulator_bytes: int
    tile_m: int
    tile_n: int
    tile_k: int
    output_visibility: str
    resource_config: ResourceConfig
    cache_config: CacheConfig
    workers: tuple[GemmWorker, ...]
    work_items: tuple[GemmWorkItem, ...]
    reduction_steps: tuple[GemmReductionStep, ...]
    cache_accesses: tuple[CacheAccess, ...]
    worker_by_id: Mapping[str, GemmWorker] = field(
        init=False,
        repr=False,
    )
    work_item_by_id: Mapping[str, GemmWorkItem] = field(
        init=False,
        repr=False,
    )
    reduction_by_id: Mapping[str, GemmReductionStep] = field(
        init=False,
        repr=False,
    )
    final_accumulator_by_tile: Mapping[tuple[int, int], str] = field(
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        for name in (
            "m",
            "n",
            "k",
            "a_element_bytes",
            "b_element_bytes",
            "output_element_bytes",
            "accumulator_bytes",
            "tile_m",
            "tile_n",
            "tile_k",
        ):
            _require_positive_integer(name, getattr(self, name))
        if self.output_visibility not in {"L2", "HBM"}:
            raise ValueError("output_visibility must be 'L2' or 'HBM'")
        if not isinstance(self.resource_config, ResourceConfig):
            raise ValueError("resource_config must be a ResourceConfig")
        if not isinstance(self.cache_config, CacheConfig):
            raise ValueError("cache_config must be a CacheConfig")

        workers = _typed_tuple("workers", self.workers, GemmWorker)
        work_items = _typed_tuple("work_items", self.work_items, GemmWorkItem)
        reductions = _typed_tuple(
            "reduction_steps",
            self.reduction_steps,
            GemmReductionStep,
        )
        cache_accesses = _typed_tuple(
            "cache_accesses",
            self.cache_accesses,
            CacheAccess,
        )
        if not cache_accesses:
            raise ValueError("cache_accesses must not be empty")
        object.__setattr__(self, "workers", workers)
        object.__setattr__(self, "work_items", work_items)
        object.__setattr__(self, "reduction_steps", reductions)
        object.__setattr__(self, "cache_accesses", cache_accesses)

        worker_by_id = _unique_by_identifier(
            workers,
            "worker_id",
            "duplicate worker id",
        )
        work_item_by_id = _unique_by_identifier(
            work_items,
            "work_item_id",
            "duplicate work item id",
        )
        reduction_by_id = _unique_by_identifier(
            reductions,
            "reduction_id",
            "duplicate reduction id",
        )

        tile_items = self._validate_output_and_k_coverage(work_items)
        self._validate_worker_assignments(workers, work_item_by_id)
        final_accumulators = self._validate_accumulators(
            tile_items,
            reductions,
        )
        self._validate_cache_accesses(
            work_items,
            reductions,
            cache_accesses,
        )

        object.__setattr__(
            self,
            "worker_by_id",
            MappingProxyType(worker_by_id),
        )
        object.__setattr__(
            self,
            "work_item_by_id",
            MappingProxyType(work_item_by_id),
        )
        object.__setattr__(
            self,
            "reduction_by_id",
            MappingProxyType(reduction_by_id),
        )
        object.__setattr__(
            self,
            "final_accumulator_by_tile",
            MappingProxyType(dict(sorted(final_accumulators.items()))),
        )

    @property
    def logical_work(self) -> int:
        return sum(item.logical_work for item in self.work_items)

    @property
    def physical_issued_work(self) -> int:
        return sum(item.physical_issued_work for item in self.work_items)

    @property
    def reduction_logical_work(self) -> int:
        return sum(step.logical_work for step in self.reduction_steps)

    @property
    def reduction_physical_work(self) -> int:
        return sum(step.physical_issued_work for step in self.reduction_steps)

    @property
    def total_physical_work(self) -> int:
        return self.physical_issued_work + self.reduction_physical_work

    @property
    def reduction_read_bytes(self) -> int:
        return sum(
            len(step.input_accumulator_ids)
            * step.issued_elements
            * self.accumulator_bytes
            for step in self.reduction_steps
        )

    @property
    def reduction_write_bytes(self) -> int:
        return sum(
            step.issued_elements * self.accumulator_bytes
            for step in self.reduction_steps
        )

    def resolve_cache(
        self,
        initial_state: InitialCacheState,
    ) -> CacheResolution:
        """Resolve this manifest's one canonical cache-access order."""

        return resolve_cache(
            self.cache_config,
            initial_state,
            self.cache_accesses,
            output_visibility=self.output_visibility,
        )

    def _validate_output_and_k_coverage(
        self,
        work_items: tuple[GemmWorkItem, ...],
    ) -> dict[tuple[int, int], tuple[GemmWorkItem, ...]]:
        grouped: dict[tuple[int, int], list[GemmWorkItem]] = {}
        for item in work_items:
            if item.output_m >= self.m or item.output_n >= self.n:
                raise ValueError("output tile is outside the GEMM problem")
            if item.output_m % self.tile_m or item.output_n % self.tile_n:
                raise ValueError("output tile origin does not match tile policy")
            expected_m = min(self.tile_m, self.m - item.output_m)
            expected_n = min(self.tile_n, self.n - item.output_n)
            if item.logical_m != expected_m or item.logical_n != expected_n:
                raise ValueError("output tile extents do not match tile policy")
            if item.k_end > self.k:
                raise ValueError("logical K range outside problem")
            grouped.setdefault((item.output_m, item.output_n), []).append(item)

        expected_tiles = {
            (output_m, output_n)
            for output_m in range(0, self.m, self.tile_m)
            for output_n in range(0, self.n, self.tile_n)
        }
        if set(grouped) != expected_tiles:
            raise ValueError("output tile coverage is incomplete")

        frozen_groups = {}
        for tile, items in grouped.items():
            ordered = tuple(sorted(items, key=lambda item: item.k_start))
            cursor = 0
            for item in ordered:
                if item.k_start > cursor:
                    raise ValueError("logical K coverage gap")
                if item.k_start < cursor:
                    raise ValueError("overlapping K ranges")
                cursor = item.k_end
            if cursor != self.k:
                raise ValueError("logical K coverage gap")
            frozen_groups[tile] = ordered
        return frozen_groups

    def _validate_worker_assignments(
        self,
        workers: tuple[GemmWorker, ...],
        work_item_by_id: dict[str, GemmWorkItem],
    ) -> None:
        assigned: set[str] = set()
        for worker in workers:
            for resource, reservation in worker.per_sm_reservation.items():
                capacity = self.resource_config.per_sm_capacities.get(resource)
                if capacity is None:
                    raise ValueError(
                        f"unknown reservation resource: {resource}"
                    )
                if reservation > capacity:
                    raise ValueError(f"reservation exceeds capacity: {resource}")
            if (
                worker.eligible_sms is not None
                and max(worker.eligible_sms) >= self.resource_config.sm_count
            ):
                raise ValueError("eligible SM is outside ResourceConfig")

            for work_item_id in worker.work_item_ids:
                if work_item_id not in work_item_by_id:
                    raise ValueError(f"unknown work item: {work_item_id}")
                if work_item_id in assigned:
                    raise ValueError(
                        f"duplicate worker assignment: {work_item_id}"
                    )
                assigned.add(work_item_id)
        missing = set(work_item_by_id) - assigned
        if missing:
            raise ValueError(f"unassigned work item: {min(missing)}")

    def _validate_accumulators(
        self,
        tile_items: dict[tuple[int, int], tuple[GemmWorkItem, ...]],
        reductions: tuple[GemmReductionStep, ...],
    ) -> dict[tuple[int, int], str]:
        producers: dict[str, tuple[tuple[int, int], int, int, str | None]] = {}
        consumers: Counter[str] = Counter()
        for tile, items in tile_items.items():
            for item in items:
                if item.accumulator_id in producers:
                    raise ValueError("duplicate accumulator producer")
                producers[item.accumulator_id] = (
                    tile,
                    item.logical_elements,
                    item.issued_elements,
                    None,
                )

        reductions_by_tile: Counter[tuple[int, int]] = Counter()
        for step in reductions:
            input_info = []
            for accumulator_id in step.input_accumulator_ids:
                info = producers.get(accumulator_id)
                if info is None:
                    raise ValueError(
                        f"unknown reduction input: {accumulator_id}"
                    )
                input_info.append(info)
            first = input_info[0]
            if any(info[:3] != first[:3] for info in input_info[1:]) or (
                step.logical_elements != first[1]
                or step.issued_elements != first[2]
            ):
                raise ValueError("incompatible reduction inputs")
            expected_dependencies = tuple(
                sorted(
                    info[3]
                    for info in input_info
                    if info[3] is not None
                )
            )
            if step.dependencies != expected_dependencies:
                raise ValueError("reduction dependencies do not match inputs")
            if step.output_accumulator_id in producers:
                raise ValueError("duplicate accumulator producer")
            for accumulator_id in step.input_accumulator_ids:
                consumers[accumulator_id] += 1
                if consumers[accumulator_id] > 1:
                    raise ValueError("accumulator consumed more than once")
            producers[step.output_accumulator_id] = (
                first[0],
                step.logical_elements,
                step.issued_elements,
                step.reduction_id,
            )
            reductions_by_tile[first[0]] += 1

        final_by_tile = {}
        for tile, items in tile_items.items():
            tile_accumulators = tuple(
                accumulator_id
                for accumulator_id, info in producers.items()
                if info[0] == tile
            )
            finals = tuple(
                accumulator_id
                for accumulator_id in tile_accumulators
                if consumers[accumulator_id] == 0
            )
            if len(finals) != 1:
                if len(items) > 1 and reductions_by_tile[tile] == 0:
                    raise ValueError("missing final reduction")
                raise ValueError("orphan accumulator")
            final = finals[0]
            if len(items) > 1 and producers[final][3] is None:
                raise ValueError("missing final reduction")
            for accumulator_id in tile_accumulators:
                if accumulator_id != final and consumers[accumulator_id] != 1:
                    raise ValueError("orphan accumulator")
            final_by_tile[tile] = final
        return final_by_tile

    def _validate_cache_accesses(
        self,
        work_items: tuple[GemmWorkItem, ...],
        reductions: tuple[GemmReductionStep, ...],
        cache_accesses: tuple[CacheAccess, ...],
    ) -> None:
        for access in cache_accesses:
            self.cache_config.require_block(access.block)

        assigned: set[int] = set()
        for owner in (*work_items, *reductions):
            for access_index in owner.cache_access_indices:
                if access_index >= len(cache_accesses):
                    raise ValueError(
                        f"unknown cache access reference: {access_index}"
                    )
                if access_index in assigned:
                    raise ValueError(
                        f"duplicate cache access assignment: {access_index}"
                    )
                assigned.add(access_index)
        missing = set(range(len(cache_accesses))) - assigned
        if missing:
            raise ValueError(f"unassigned cache access: {min(missing)}")


def _unique_by_identifier(values, attribute: str, message: str) -> dict:
    result = {}
    for value in values:
        identifier = getattr(value, attribute)
        if identifier in result:
            raise ValueError(message)
        result[identifier] = value
    return result


def _typed_tuple(name: str, values, expected_type: type) -> tuple:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a sequence")
    values = tuple(values)
    if any(not isinstance(value, expected_type) for value in values):
        raise ValueError(f"{name} contains an invalid value")
    return values


def _identifier_tuple(
    name: str,
    values,
    *,
    allow_empty: bool,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a sequence of identifiers")
    values = tuple(values)
    if not allow_empty and not values:
        raise ValueError(f"{name} must not be empty")
    for value in values:
        _require_identifier(name, value)
    return values


def _access_index_tuple(values) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError("cache_access_indices must be a sequence")
    values = tuple(values)
    for value in values:
        _require_non_negative_integer("cache access index", value)
    if len(set(values)) != len(values):
        raise ValueError("cache access indices must not contain duplicates")
    if any(left >= right for left, right in zip(values, values[1:])):
        raise ValueError("cache access order must be strictly increasing")
    return values


def _require_identifier(name: str, value: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")


def _require_positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_non_negative_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


__all__ = [
    "GemmLaunchManifest",
    "GemmReductionStep",
    "GemmWorkItem",
    "GemmWorker",
]
