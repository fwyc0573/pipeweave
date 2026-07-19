"""Deterministic manifest-order cache resolution for the DES model."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping


_ACCESS_KINDS = frozenset({"read", "overwrite"})
_OUTPUT_VISIBILITIES = frozenset({"L2", "HBM"})
_TRANSITION_ACTIONS = frozenset(
    {
        "read_hit",
        "read_miss",
        "overwrite_hit",
        "overwrite_miss",
        "evict_clean",
        "evict_dirty",
        "flush_dirty_output",
    }
)


@dataclass(frozen=True, order=True)
class CacheBlock:
    """One exact-sized modeled block in the manifest block catalog."""

    object_id: str
    block_index: int
    size_bytes: int

    def __post_init__(self) -> None:
        if not isinstance(self.object_id, str) or not self.object_id:
            raise ValueError("object_id must be a non-empty string")
        _require_non_negative_integer("block_index", self.block_index)
        _require_positive_integer("size_bytes", self.size_bytes)

    @property
    def identity(self) -> tuple[str, int]:
        return self.object_id, self.block_index


@dataclass(frozen=True)
class CacheConfig:
    """Capacity, modeled block width, and authoritative block catalog."""

    capacity_bytes: int
    block_bytes: int
    blocks: tuple[CacheBlock, ...] = ()
    block_by_identity: Mapping[tuple[str, int], CacheBlock] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        _require_positive_integer("capacity_bytes", self.capacity_bytes)
        _require_positive_integer("block_bytes", self.block_bytes)
        blocks = tuple(self.blocks)
        by_identity: dict[tuple[str, int], CacheBlock] = {}
        for block in blocks:
            if not isinstance(block, CacheBlock):
                raise ValueError("blocks must contain CacheBlock values")
            existing = by_identity.get(block.identity)
            if existing is not None:
                if existing.size_bytes != block.size_bytes:
                    raise ValueError("inconsistent block size")
                raise ValueError("duplicate cache block")
            if block.size_bytes > self.block_bytes:
                raise ValueError("cache block exceeds block_bytes")
            if block.size_bytes > self.capacity_bytes:
                raise ValueError("cache block exceeds capacity")
            by_identity[block.identity] = block
        object.__setattr__(
            self,
            "blocks",
            tuple(sorted(blocks, key=lambda block: block.identity)),
        )
        object.__setattr__(
            self,
            "block_by_identity",
            MappingProxyType(dict(sorted(by_identity.items()))),
        )

    def require_block(self, block: CacheBlock) -> CacheBlock:
        """Return the canonical catalog block for one exact reference."""

        if not isinstance(block, CacheBlock):
            raise ValueError("cache reference must be a CacheBlock")
        declared = self.block_by_identity.get(block.identity)
        if declared is None:
            raise ValueError(f"unknown cache block: {block.identity}")
        if declared.size_bytes != block.size_bytes:
            raise ValueError(f"inconsistent block size: {block.identity}")
        return declared


@dataclass(frozen=True)
class ResidentCacheBlock:
    """A resident block and its dirty state."""

    block: CacheBlock
    dirty: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.block, CacheBlock):
            raise ValueError("block must be a CacheBlock")
        if not isinstance(self.dirty, bool):
            raise ValueError("dirty must be a boolean")


@dataclass(frozen=True)
class InitialCacheState:
    """Resident blocks ordered from oldest to newest recency."""

    resident_blocks: tuple[ResidentCacheBlock, ...] = ()

    def __post_init__(self) -> None:
        resident_blocks = tuple(self.resident_blocks)
        identities: set[tuple[str, int]] = set()
        for entry in resident_blocks:
            if not isinstance(entry, ResidentCacheBlock):
                raise ValueError(
                    "resident_blocks must contain ResidentCacheBlock values"
                )
            if entry.block.identity in identities:
                raise ValueError("duplicate resident cache block")
            identities.add(entry.block.identity)
        object.__setattr__(self, "resident_blocks", resident_blocks)

    @property
    def resident_bytes(self) -> int:
        return sum(entry.block.size_bytes for entry in self.resident_blocks)


@dataclass(frozen=True)
class CacheAccess:
    """One whole modeled-block read or overwrite in manifest order."""

    block: CacheBlock
    kind: str
    is_output: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.block, CacheBlock):
            raise ValueError("block must be a CacheBlock")
        if self.kind not in _ACCESS_KINDS:
            raise ValueError("kind must be 'read' or 'overwrite'")
        if not isinstance(self.is_output, bool):
            raise ValueError("is_output must be a boolean")
        if self.is_output and self.kind != "overwrite":
            raise ValueError("output access must be an overwrite")


@dataclass(frozen=True)
class CacheTransition:
    """One immutable cache-state action and its exact traffic delta."""

    action: str
    block: CacheBlock
    access_index: int | None
    hbm_read_bytes: int = 0
    hbm_write_bytes: int = 0
    l2_read_bytes: int = 0
    l2_write_bytes: int = 0

    def __post_init__(self) -> None:
        if self.action not in _TRANSITION_ACTIONS:
            raise ValueError("unknown cache transition action")
        if not isinstance(self.block, CacheBlock):
            raise ValueError("block must be a CacheBlock")
        if self.action == "flush_dirty_output":
            if self.access_index is not None:
                raise ValueError("output flush cannot have an access index")
        else:
            _require_non_negative_integer("access_index", self.access_index)
        for name, value in (
            ("hbm_read_bytes", self.hbm_read_bytes),
            ("hbm_write_bytes", self.hbm_write_bytes),
            ("l2_read_bytes", self.l2_read_bytes),
            ("l2_write_bytes", self.l2_write_bytes),
        ):
            _require_non_negative_integer(name, value)
        if _transition_traffic(self.action, self.block.size_bytes) != (
            self.hbm_read_bytes,
            self.hbm_write_bytes,
            self.l2_read_bytes,
            self.l2_write_bytes,
        ):
            raise ValueError("cache transition traffic is inconsistent")


@dataclass(frozen=True)
class CacheResolution:
    """Immutable state and traffic evidence for one cache resolution."""

    initial_state: InitialCacheState
    transitions: tuple[CacheTransition, ...]
    final_state: InitialCacheState
    hits: int = 0
    misses: int = 0
    fills: int = 0
    evictions: int = 0
    dirty_writebacks: int = 0
    output_flushes: int = 0
    hbm_read_bytes: int = 0
    hbm_write_bytes: int = 0
    l2_read_bytes: int = 0
    l2_write_bytes: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.initial_state, InitialCacheState):
            raise ValueError("initial_state must be an InitialCacheState")
        if not isinstance(self.final_state, InitialCacheState):
            raise ValueError("final_state must be an InitialCacheState")
        transitions = tuple(self.transitions)
        if any(
            not isinstance(transition, CacheTransition)
            for transition in transitions
        ):
            raise ValueError("transitions must contain CacheTransition values")
        object.__setattr__(self, "transitions", transitions)
        for name in (
            "hits",
            "misses",
            "fills",
            "evictions",
            "dirty_writebacks",
            "output_flushes",
            "hbm_read_bytes",
            "hbm_write_bytes",
            "l2_read_bytes",
            "l2_write_bytes",
        ):
            _require_non_negative_integer(name, getattr(self, name))
        if _resolution_totals(transitions) != (
            self.hits,
            self.misses,
            self.fills,
            self.evictions,
            self.dirty_writebacks,
            self.output_flushes,
            self.hbm_read_bytes,
            self.hbm_write_bytes,
            self.l2_read_bytes,
            self.l2_write_bytes,
        ):
            raise ValueError("cache traffic totals are inconsistent with transitions")

    @property
    def initial_resident_bytes(self) -> int:
        return self.initial_state.resident_bytes

    @property
    def final_resident_bytes(self) -> int:
        return self.final_state.resident_bytes


def resolve_cache(
    config: CacheConfig,
    initial_state: InitialCacheState,
    accesses: tuple[CacheAccess, ...],
    *,
    output_visibility: str,
) -> CacheResolution:
    """Resolve one canonical manifest access order through shared abstract L2."""

    if not isinstance(config, CacheConfig):
        raise ValueError("config must be a CacheConfig")
    if not isinstance(initial_state, InitialCacheState):
        raise ValueError("initial_state must be an InitialCacheState")
    if output_visibility not in _OUTPUT_VISIBILITIES:
        raise ValueError("output_visibility must be 'L2' or 'HBM'")
    accesses = tuple(accesses)
    if any(not isinstance(access, CacheAccess) for access in accesses):
        raise ValueError("accesses must contain CacheAccess values")

    resident = list(initial_state.resident_blocks)
    for entry in resident:
        config.require_block(entry.block)
    if initial_state.resident_bytes > config.capacity_bytes:
        raise ValueError("initial cache state exceeds capacity")

    transitions: list[CacheTransition] = []
    output_blocks: set[tuple[str, int]] = set()
    for access_index, access in enumerate(accesses):
        block = config.require_block(access.block)
        if access.is_output:
            output_blocks.add(block.identity)

        resident_index = _resident_index(resident, block.identity)
        if resident_index is not None:
            entry = resident.pop(resident_index)
            if access.kind == "read":
                action = "read_hit"
                dirty = entry.dirty
            else:
                action = "overwrite_hit"
                dirty = True
            resident.append(ResidentCacheBlock(block=block, dirty=dirty))
            transitions.append(_transition(action, block, access_index))
            continue

        while _resident_bytes(resident) + block.size_bytes > config.capacity_bytes:
            victim = resident.pop(0)
            action = "evict_dirty" if victim.dirty else "evict_clean"
            transitions.append(_transition(action, victim.block, access_index))

        if access.kind == "read":
            action = "read_miss"
            dirty = False
        else:
            action = "overwrite_miss"
            dirty = True
        resident.append(ResidentCacheBlock(block=block, dirty=dirty))
        transitions.append(_transition(action, block, access_index))

    if output_visibility == "HBM":
        for index, entry in enumerate(resident):
            if entry.block.identity not in output_blocks or not entry.dirty:
                continue
            transitions.append(
                _transition("flush_dirty_output", entry.block, None)
            )
            resident[index] = ResidentCacheBlock(
                block=entry.block,
                dirty=False,
            )

    final_state = InitialCacheState(resident_blocks=tuple(resident))
    totals = _resolution_totals(tuple(transitions))
    return CacheResolution(
        initial_state=initial_state,
        transitions=tuple(transitions),
        final_state=final_state,
        hits=totals[0],
        misses=totals[1],
        fills=totals[2],
        evictions=totals[3],
        dirty_writebacks=totals[4],
        output_flushes=totals[5],
        hbm_read_bytes=totals[6],
        hbm_write_bytes=totals[7],
        l2_read_bytes=totals[8],
        l2_write_bytes=totals[9],
    )


def _resident_index(
    resident: list[ResidentCacheBlock],
    identity: tuple[str, int],
) -> int | None:
    for index, entry in enumerate(resident):
        if entry.block.identity == identity:
            return index
    return None


def _resident_bytes(resident: list[ResidentCacheBlock]) -> int:
    return sum(entry.block.size_bytes for entry in resident)


def _transition(
    action: str,
    block: CacheBlock,
    access_index: int | None,
) -> CacheTransition:
    traffic = _transition_traffic(action, block.size_bytes)
    return CacheTransition(
        action=action,
        block=block,
        access_index=access_index,
        hbm_read_bytes=traffic[0],
        hbm_write_bytes=traffic[1],
        l2_read_bytes=traffic[2],
        l2_write_bytes=traffic[3],
    )


def _transition_traffic(
    action: str,
    size_bytes: int,
) -> tuple[int, int, int, int]:
    if action == "read_hit":
        return 0, 0, size_bytes, 0
    if action == "read_miss":
        return size_bytes, 0, size_bytes, size_bytes
    if action in {"overwrite_hit", "overwrite_miss"}:
        return 0, 0, 0, size_bytes
    if action == "evict_clean":
        return 0, 0, 0, 0
    if action in {"evict_dirty", "flush_dirty_output"}:
        return 0, size_bytes, size_bytes, 0
    raise ValueError("unknown cache transition action")


def _resolution_totals(
    transitions: tuple[CacheTransition, ...],
) -> tuple[int, int, int, int, int, int, int, int, int, int]:
    actions = tuple(transition.action for transition in transitions)
    return (
        sum(action in {"read_hit", "overwrite_hit"} for action in actions),
        sum(action in {"read_miss", "overwrite_miss"} for action in actions),
        actions.count("read_miss"),
        sum(action in {"evict_clean", "evict_dirty"} for action in actions),
        sum(
            action in {"evict_dirty", "flush_dirty_output"}
            for action in actions
        ),
        actions.count("flush_dirty_output"),
        sum(transition.hbm_read_bytes for transition in transitions),
        sum(transition.hbm_write_bytes for transition in transitions),
        sum(transition.l2_read_bytes for transition in transitions),
        sum(transition.l2_write_bytes for transition in transitions),
    )


def _require_positive_integer(name: str, value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_non_negative_integer(name: str, value: int | None) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


__all__ = [
    "CacheAccess",
    "CacheBlock",
    "CacheConfig",
    "CacheResolution",
    "CacheTransition",
    "InitialCacheState",
    "ResidentCacheBlock",
    "resolve_cache",
]
