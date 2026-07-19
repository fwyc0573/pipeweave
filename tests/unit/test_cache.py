"""Unit tests for manifest-order static L2/HBM cache resolution."""

from dataclasses import FrozenInstanceError
from importlib import import_module
from types import SimpleNamespace

import pytest


def _api() -> SimpleNamespace:
    try:
        module = import_module("event_simulator.cache")
    except ModuleNotFoundError as error:
        pytest.fail(f"cache module is missing: {error}")

    names = (
        "CacheAccess",
        "CacheBlock",
        "CacheConfig",
        "CacheResolution",
        "CacheTransition",
        "InitialCacheState",
        "ResidentCacheBlock",
        "resolve_cache",
    )
    missing = tuple(name for name in names if not hasattr(module, name))
    if missing:
        pytest.fail(f"cache API is missing: {missing}")
    return SimpleNamespace(**{name: getattr(module, name) for name in names})


def _block(api, object_id: str, block_index: int, size_bytes: int):
    return api.CacheBlock(
        object_id=object_id,
        block_index=block_index,
        size_bytes=size_bytes,
    )


def _config(api, *blocks, capacity_bytes: int = 8, block_bytes: int = 4):
    return api.CacheConfig(
        capacity_bytes=capacity_bytes,
        block_bytes=block_bytes,
        blocks=blocks,
    )


def _resident(api, block, *, dirty: bool = False):
    return api.ResidentCacheBlock(block=block, dirty=dirty)


def _access(api, block, kind: str = "read", *, is_output: bool = False):
    return api.CacheAccess(block=block, kind=kind, is_output=is_output)


def _resolve(
    api,
    config,
    accesses,
    *,
    initial_state=None,
    output_visibility: str = "L2",
):
    if initial_state is None:
        initial_state = api.InitialCacheState()
    return api.resolve_cache(
        config,
        initial_state,
        accesses,
        output_visibility=output_visibility,
    )


def _resident_ids(state):
    return tuple(
        (entry.block.object_id, entry.block.block_index)
        for entry in state.resident_blocks
    )


def test_cold_read_miss_records_fill_and_exact_traffic():
    api = _api()
    a0 = _block(api, "A", 0, 4)

    result = _resolve(api, _config(api, a0), (_access(api, a0),))

    assert result.hits == 0
    assert result.misses == 1
    assert result.fills == 1
    assert result.evictions == 0
    assert result.dirty_writebacks == 0
    assert result.hbm_read_bytes == 4
    assert result.hbm_write_bytes == 0
    assert result.l2_read_bytes == 4
    assert result.l2_write_bytes == 4
    assert result.initial_resident_bytes == 0
    assert result.final_resident_bytes == 4
    assert _resident_ids(result.final_state) == (("A", 0),)
    assert result.final_state.resident_blocks[0].dirty is False
    assert tuple(item.action for item in result.transitions) == ("read_miss",)


def test_warm_read_hit_updates_oldest_to_newest_recency():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    b0 = _block(api, "B", 0, 4)
    initial = api.InitialCacheState(
        resident_blocks=(
            _resident(api, a0),
            _resident(api, b0),
        )
    )

    result = _resolve(
        api,
        _config(api, a0, b0),
        (_access(api, a0),),
        initial_state=initial,
    )

    assert result.hits == 1
    assert result.misses == 0
    assert result.hbm_read_bytes == 0
    assert result.l2_read_bytes == 4
    assert _resident_ids(result.final_state) == (("B", 0), ("A", 0))
    assert tuple(item.action for item in result.transitions) == ("read_hit",)


def test_read_hit_preserves_existing_dirty_state():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    initial = api.InitialCacheState(
        resident_blocks=(_resident(api, a0, dirty=True),)
    )

    result = _resolve(
        api,
        _config(api, a0),
        (_access(api, a0),),
        initial_state=initial,
    )

    assert result.hits == 1
    assert result.final_state.resident_blocks[0].dirty is True
    assert result.transitions[0].action == "read_hit"


def test_overwrite_hit_marks_block_dirty_without_hbm_traffic():
    api = _api()
    c0 = _block(api, "C", 0, 4)
    initial = api.InitialCacheState(
        resident_blocks=(_resident(api, c0),)
    )

    result = _resolve(
        api,
        _config(api, c0),
        (_access(api, c0, "overwrite"),),
        initial_state=initial,
    )

    assert result.hits == 1
    assert result.hbm_read_bytes == 0
    assert result.hbm_write_bytes == 0
    assert result.l2_read_bytes == 0
    assert result.l2_write_bytes == 4
    assert result.final_state.resident_blocks[0].dirty is True
    assert result.transitions[0].action == "overwrite_hit"


def test_overwrite_miss_allocates_dirty_block_without_hbm_read():
    api = _api()
    c0 = _block(api, "C", 0, 4)

    result = _resolve(
        api,
        _config(api, c0),
        (_access(api, c0, "overwrite"),),
    )

    assert result.hits == 0
    assert result.misses == 1
    assert result.fills == 0
    assert result.hbm_read_bytes == 0
    assert result.l2_write_bytes == 4
    assert result.final_state.resident_blocks[0].dirty is True
    assert result.transitions[0].action == "overwrite_miss"


def test_size_aware_lru_evicts_only_the_oldest_required_bytes():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    b1 = _block(api, "B", 1, 3)
    c0 = _block(api, "C", 0, 4)
    config = _config(
        api,
        a0,
        b1,
        c0,
        capacity_bytes=7,
        block_bytes=4,
    )
    initial = api.InitialCacheState(
        resident_blocks=(
            _resident(api, a0),
            _resident(api, b1),
        )
    )

    result = _resolve(
        api,
        config,
        (_access(api, c0),),
        initial_state=initial,
    )

    assert result.evictions == 1
    assert _resident_ids(result.final_state) == (("B", 1), ("C", 0))
    assert result.final_resident_bytes == 7
    assert tuple(item.action for item in result.transitions) == (
        "evict_clean",
        "read_miss",
    )


def test_size_aware_lru_repeats_eviction_until_incoming_block_fits():
    api = _api()
    a0 = _block(api, "A", 0, 2)
    b0 = _block(api, "B", 0, 2)
    d0 = _block(api, "D", 0, 4)
    config = _config(
        api,
        a0,
        b0,
        d0,
        capacity_bytes=5,
        block_bytes=4,
    )
    initial = api.InitialCacheState(
        resident_blocks=(_resident(api, a0), _resident(api, b0))
    )

    result = _resolve(
        api,
        config,
        (_access(api, d0),),
        initial_state=initial,
    )

    assert result.evictions == 2
    assert result.final_resident_bytes == 4
    assert _resident_ids(result.final_state) == (("D", 0),)
    assert tuple(item.action for item in result.transitions) == (
        "evict_clean",
        "evict_clean",
        "read_miss",
    )


def test_dirty_eviction_writes_exact_modeled_block_size_to_hbm():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    b1 = _block(api, "B", 1, 3)
    c0 = _block(api, "C", 0, 4)
    config = _config(
        api,
        a0,
        b1,
        c0,
        capacity_bytes=7,
        block_bytes=4,
    )
    initial = api.InitialCacheState(
        resident_blocks=(
            _resident(api, a0, dirty=True),
            _resident(api, b1),
        )
    )

    result = _resolve(
        api,
        config,
        (_access(api, c0),),
        initial_state=initial,
    )

    assert result.evictions == 1
    assert result.dirty_writebacks == 1
    assert result.hbm_read_bytes == 4
    assert result.hbm_write_bytes == 4
    assert result.l2_read_bytes == 8
    assert result.l2_write_bytes == 4
    assert tuple(item.action for item in result.transitions) == (
        "evict_dirty",
        "read_miss",
    )


def test_short_final_block_uses_exact_remaining_size():
    api = _api()
    final_block = _block(api, "A", 2, 2)

    result = _resolve(
        api,
        _config(api, final_block),
        (_access(api, final_block),),
    )

    assert result.hbm_read_bytes == 2
    assert result.l2_read_bytes == 2
    assert result.l2_write_bytes == 2
    assert result.final_resident_bytes == 2


def test_l2_output_visibility_retains_dirty_output_without_flush():
    api = _api()
    c0 = _block(api, "C", 0, 4)

    result = _resolve(
        api,
        _config(api, c0),
        (_access(api, c0, "overwrite", is_output=True),),
        output_visibility="L2",
    )

    assert result.output_flushes == 0
    assert result.dirty_writebacks == 0
    assert result.hbm_write_bytes == 0
    assert result.final_state.resident_blocks[0].dirty is True


def test_hbm_output_visibility_flushes_declared_dirty_output_only():
    api = _api()
    scratch = _block(api, "scratch", 0, 4)
    output = _block(api, "C", 0, 4)
    accesses = (
        _access(api, scratch, "overwrite"),
        _access(api, output, "overwrite", is_output=True),
    )

    result = _resolve(
        api,
        _config(api, scratch, output),
        accesses,
        output_visibility="HBM",
    )

    assert result.output_flushes == 1
    assert result.dirty_writebacks == 1
    assert result.hbm_write_bytes == 4
    assert result.l2_read_bytes == 4
    assert tuple(item.action for item in result.transitions)[-1] == (
        "flush_dirty_output"
    )
    by_object = {
        entry.block.object_id: entry.dirty
        for entry in result.final_state.resident_blocks
    }
    assert by_object == {"scratch": True, "C": False}


def test_empty_access_trace_preserves_explicit_initial_state():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    initial = api.InitialCacheState(
        resident_blocks=(_resident(api, a0, dirty=True),)
    )

    result = _resolve(
        api,
        _config(api, a0),
        (),
        initial_state=initial,
    )

    assert result.initial_state == initial
    assert result.final_state == initial
    assert result.transitions == ()
    assert result.hits == result.misses == 0
    assert result.initial_resident_bytes == 4
    assert result.final_resident_bytes == 4


def test_resolution_and_nested_records_are_immutable():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    result = _resolve(api, _config(api, a0), (_access(api, a0),))

    with pytest.raises(FrozenInstanceError):
        result.hits = 2
    with pytest.raises(FrozenInstanceError):
        result.final_state.resident_blocks = ()
    with pytest.raises(FrozenInstanceError):
        result.transitions[0].action = "read_hit"


def test_resolution_is_deterministic_and_detached_from_input_lists():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    b0 = _block(api, "B", 0, 4)
    blocks = [a0, b0]
    accesses = [_access(api, a0), _access(api, b0)]
    config = api.CacheConfig(
        capacity_bytes=8,
        block_bytes=4,
        blocks=blocks,
    )

    first = _resolve(api, config, accesses)
    blocks.reverse()
    accesses.reverse()
    second = _resolve(
        api,
        config,
        (_access(api, a0), _access(api, b0)),
    )

    assert first == second
    assert tuple(block.object_id for block in config.blocks) == ("A", "B")


def test_config_rejects_duplicate_and_inconsistent_block_definitions():
    api = _api()
    a0 = _block(api, "A", 0, 4)

    with pytest.raises(ValueError, match="duplicate cache block"):
        _config(api, a0, a0)
    with pytest.raises(ValueError, match="inconsistent block size"):
        _config(api, a0, _block(api, "A", 0, 3))


def test_resolution_rejects_unknown_and_inconsistent_references():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    config = _config(api, a0)

    with pytest.raises(ValueError, match="unknown cache block"):
        _resolve(
            api,
            config,
            (_access(api, _block(api, "B", 0, 4)),),
        )
    with pytest.raises(ValueError, match="inconsistent block size"):
        _resolve(
            api,
            config,
            (_access(api, _block(api, "A", 0, 3)),),
        )


def test_resolution_rejects_over_capacity_initial_state():
    api = _api()
    a0 = _block(api, "A", 0, 4)
    b0 = _block(api, "B", 0, 4)
    initial = api.InitialCacheState(
        resident_blocks=(_resident(api, a0), _resident(api, b0))
    )

    with pytest.raises(ValueError, match="initial cache state exceeds capacity"):
        _resolve(
            api,
            _config(
                api,
                a0,
                b0,
                capacity_bytes=7,
                block_bytes=4,
            ),
            (),
            initial_state=initial,
        )


def test_config_rejects_a_block_larger_than_total_capacity():
    api = _api()
    block = _block(api, "A", 0, 5)

    with pytest.raises(ValueError, match="cache block exceeds capacity"):
        _config(
            api,
            block,
            capacity_bytes=4,
            block_bytes=8,
        )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda api: api.CacheConfig(0, 4, ()), "capacity_bytes"),
        (lambda api: api.CacheConfig(4, 0, ()), "block_bytes"),
        (lambda api: _block(api, "", 0, 4), "object_id"),
        (lambda api: _block(api, "A", -1, 4), "block_index"),
        (lambda api: _block(api, "A", 0, 0), "size_bytes"),
        (
            lambda api: api.ResidentCacheBlock(
                block=_block(api, "A", 0, 4), dirty=1
            ),
            "dirty",
        ),
        (
            lambda api: api.CacheAccess(
                block=_block(api, "A", 0, 4), kind="fetch"
            ),
            "kind",
        ),
        (
            lambda api: api.CacheAccess(
                block=_block(api, "A", 0, 4),
                kind="read",
                is_output=True,
            ),
            "output",
        ),
    ],
)
def test_cache_value_objects_reject_invalid_inputs(factory, message):
    api = _api()

    with pytest.raises(ValueError, match=message):
        factory(api)


def test_initial_state_rejects_duplicate_resident_blocks():
    api = _api()
    a0 = _block(api, "A", 0, 4)

    with pytest.raises(ValueError, match="duplicate resident cache block"):
        api.InitialCacheState(
            resident_blocks=(_resident(api, a0), _resident(api, a0))
        )


@pytest.mark.parametrize("visibility", ["", "l2", "DRAM", None])
def test_resolution_rejects_invalid_output_visibility(visibility):
    api = _api()

    with pytest.raises(ValueError, match="output_visibility"):
        _resolve(
            api,
            _config(api),
            (),
            output_visibility=visibility,
        )


def test_cache_resolution_rejects_traffic_totals_inconsistent_with_transitions():
    api = _api()
    empty = api.InitialCacheState()

    with pytest.raises(ValueError, match="traffic totals"):
        api.CacheResolution(
            initial_state=empty,
            transitions=(),
            final_state=empty,
            hbm_read_bytes=1,
        )


def test_cache_contract_is_exported_from_the_public_package():
    package = import_module("event_simulator")
    expected = {
        "CacheAccess",
        "CacheBlock",
        "CacheConfig",
        "CacheResolution",
        "CacheTransition",
        "InitialCacheState",
        "ResidentCacheBlock",
        "resolve_cache",
    }

    assert expected <= set(package.__all__)
    assert all(hasattr(package, name) for name in expected)
