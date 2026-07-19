"""Unit tests for authoritative GEMM launch manifests."""

from dataclasses import FrozenInstanceError, replace
from importlib import import_module
from types import MappingProxyType, SimpleNamespace

import pytest

from event_simulator import (
    CacheAccess,
    CacheBlock,
    CacheConfig,
    InitialCacheState,
    ResourceConfig,
)


def _api() -> SimpleNamespace:
    try:
        module = import_module("event_simulator.gemm_manifest")
    except ModuleNotFoundError as error:
        pytest.fail(f"GEMM manifest module is missing: {error}")

    names = (
        "GemmLaunchManifest",
        "GemmReductionStep",
        "GemmWorkItem",
        "GemmWorker",
    )
    missing = tuple(name for name in names if not hasattr(module, name))
    if missing:
        pytest.fail(f"GEMM manifest API is missing: {missing}")
    return SimpleNamespace(**{name: getattr(module, name) for name in names})


def _resources(*, sm_count: int = 2) -> ResourceConfig:
    return ResourceConfig(
        global_capacities={
            "hbm_bandwidth": 1,
            "l2_bandwidth": 1,
            "launch": 1,
        },
        sm_count=sm_count,
        per_sm_capacities={
            "alu": 2,
            "cta_slots": 2,
            "tensor_core": 1,
        },
    )


def _block(object_id: str, index: int, size: int = 4) -> CacheBlock:
    return CacheBlock(object_id=object_id, block_index=index, size_bytes=size)


def _work_item(api, **overrides):
    values = {
        "work_item_id": "item-0",
        "output_m": 0,
        "output_n": 0,
        "logical_m": 4,
        "logical_n": 4,
        "k_start": 0,
        "k_end": 4,
        "issued_m": 4,
        "issued_n": 4,
        "issued_k": 4,
        "accumulator_id": "acc-0",
        "cache_access_indices": (0, 1, 2),
    }
    values.update(overrides)
    return api.GemmWorkItem(**values)


def _worker(api, **overrides):
    values = {
        "worker_id": "worker-0",
        "work_item_ids": ("item-0",),
        "per_sm_reservation": {"cta_slots": 1},
        "eligible_sms": frozenset({0, 1}),
    }
    values.update(overrides)
    return api.GemmWorker(**values)


def _reduction(api, **overrides):
    values = {
        "reduction_id": "reduce-0",
        "input_accumulator_ids": ("partial-0", "partial-1"),
        "output_accumulator_id": "final-0",
        "logical_elements": 16,
        "issued_elements": 16,
        "dependencies": (),
        "cache_access_indices": (6, 7, 8),
    }
    values.update(overrides)
    return api.GemmReductionStep(**values)


def _ordinary_manifest(api, **overrides):
    a0 = _block("A", 0)
    b0 = _block("B", 0)
    c0 = _block("C", 0)
    values = {
        "m": 4,
        "n": 4,
        "k": 4,
        "a_element_bytes": 2,
        "b_element_bytes": 2,
        "output_element_bytes": 2,
        "accumulator_bytes": 4,
        "tile_m": 4,
        "tile_n": 4,
        "tile_k": 4,
        "output_visibility": "L2",
        "resource_config": _resources(),
        "cache_config": CacheConfig(
            capacity_bytes=8,
            block_bytes=4,
            blocks=(a0, b0, c0),
        ),
        "workers": (_worker(api),),
        "work_items": (_work_item(api),),
        "reduction_steps": (),
        "cache_accesses": (
            CacheAccess(a0, "read"),
            CacheAccess(b0, "read"),
            CacheAccess(c0, "overwrite", is_output=True),
        ),
    }
    values.update(overrides)
    return api.GemmLaunchManifest(**values)


def _split_k_manifest(api, **overrides):
    blocks = tuple(
        _block(object_id, index)
        for object_id, index in (
            ("A", 0),
            ("B", 0),
            ("partial", 0),
            ("A", 1),
            ("B", 1),
            ("partial", 1),
            ("partial", 0),
            ("partial", 1),
            ("C", 0),
        )
    )
    catalog = tuple(
        _block(object_id, index)
        for object_id, index in (
            ("A", 0),
            ("B", 0),
            ("partial", 0),
            ("A", 1),
            ("B", 1),
            ("partial", 1),
            ("C", 0),
        )
    )
    accesses = (
        CacheAccess(blocks[0], "read"),
        CacheAccess(blocks[1], "read"),
        CacheAccess(blocks[2], "overwrite"),
        CacheAccess(blocks[3], "read"),
        CacheAccess(blocks[4], "read"),
        CacheAccess(blocks[5], "overwrite"),
        CacheAccess(blocks[6], "read"),
        CacheAccess(blocks[7], "read"),
        CacheAccess(blocks[8], "overwrite", is_output=True),
    )
    item_0 = _work_item(
        api,
        work_item_id="item-0",
        k_start=0,
        k_end=4,
        accumulator_id="partial-0",
        cache_access_indices=(0, 1, 2),
    )
    item_1 = _work_item(
        api,
        work_item_id="item-1",
        k_start=4,
        k_end=8,
        accumulator_id="partial-1",
        cache_access_indices=(3, 4, 5),
    )
    values = {
        "m": 4,
        "n": 4,
        "k": 8,
        "a_element_bytes": 2,
        "b_element_bytes": 2,
        "output_element_bytes": 2,
        "accumulator_bytes": 4,
        "tile_m": 4,
        "tile_n": 4,
        "tile_k": 4,
        "output_visibility": "HBM",
        "resource_config": _resources(),
        "cache_config": CacheConfig(
            capacity_bytes=16,
            block_bytes=4,
            blocks=catalog,
        ),
        "workers": (
            _worker(
                api,
                worker_id="worker-0",
                work_item_ids=("item-0",),
            ),
            _worker(
                api,
                worker_id="worker-1",
                work_item_ids=("item-1",),
            ),
        ),
        "work_items": (item_0, item_1),
        "reduction_steps": (_reduction(api),),
        "cache_accesses": accesses,
    }
    values.update(overrides)
    return api.GemmLaunchManifest(**values)


def _grid_manifest(api, *, m: int, n: int, tile_m: int, tile_n: int):
    work_items = []
    workers = []
    blocks = []
    accesses = []
    index = 0
    for output_m in range(0, m, tile_m):
        logical_m = min(tile_m, m - output_m)
        for output_n in range(0, n, tile_n):
            logical_n = min(tile_n, n - output_n)
            item_id = f"item-{index}"
            block = _block("C", index)
            blocks.append(block)
            accesses.append(CacheAccess(block, "overwrite", is_output=True))
            work_items.append(
                _work_item(
                    api,
                    work_item_id=item_id,
                    output_m=output_m,
                    output_n=output_n,
                    logical_m=logical_m,
                    logical_n=logical_n,
                    accumulator_id=f"acc-{index}",
                    cache_access_indices=(index,),
                )
            )
            workers.append(
                _worker(
                    api,
                    worker_id=f"worker-{index}",
                    work_item_ids=(item_id,),
                )
            )
            index += 1
    return api.GemmLaunchManifest(
        m=m,
        n=n,
        k=4,
        a_element_bytes=2,
        b_element_bytes=2,
        output_element_bytes=2,
        accumulator_bytes=4,
        tile_m=tile_m,
        tile_n=tile_n,
        tile_k=4,
        output_visibility="L2",
        resource_config=_resources(),
        cache_config=CacheConfig(
            capacity_bytes=max(4, len(blocks) * 4),
            block_bytes=4,
            blocks=tuple(blocks),
        ),
        workers=tuple(workers),
        work_items=tuple(work_items),
        reduction_steps=(),
        cache_accesses=tuple(accesses),
    )


def test_ordinary_cta_manifest_has_one_final_accumulator_and_exact_work():
    api = _api()

    manifest = _ordinary_manifest(api)

    assert manifest.logical_work == 2 * 4 * 4 * 4
    assert manifest.physical_issued_work == 2 * 4 * 4 * 4
    assert manifest.reduction_logical_work == 0
    assert manifest.reduction_physical_work == 0
    assert manifest.total_physical_work == 2 * 4 * 4 * 4
    assert dict(manifest.final_accumulator_by_tile) == {(0, 0): "acc-0"}
    assert tuple(manifest.work_item_by_id) == ("item-0",)


def test_worker_with_multiple_ordered_items_expresses_persistent_execution():
    api = _api()
    base = _grid_manifest(api, m=4, n=8, tile_m=4, tile_n=4)
    persistent_worker = _worker(
        api,
        worker_id="worker-persistent",
        work_item_ids=("item-0", "item-1"),
    )

    manifest = replace(base, workers=(persistent_worker,))

    assert manifest.workers[0].work_item_ids == ("item-0", "item-1")
    assert "persistent" not in manifest.workers[0].__dataclass_fields__
    assert len(manifest.workers) == 1


def test_worker_without_affinity_accepts_all_configured_sms():
    api = _api()
    base = _ordinary_manifest(api)

    manifest = replace(
        base,
        workers=(replace(base.workers[0], eligible_sms=None),),
    )

    assert manifest.workers[0].eligible_sms is None


def test_partial_tiles_separate_logical_and_physically_issued_work():
    api = _api()

    manifest = _grid_manifest(api, m=5, n=6, tile_m=4, tile_n=4)

    assert tuple(
        (item.output_m, item.output_n, item.logical_m, item.logical_n)
        for item in manifest.work_items
    ) == (
        (0, 0, 4, 4),
        (0, 4, 4, 2),
        (4, 0, 1, 4),
        (4, 4, 1, 2),
    )
    assert manifest.logical_work == 2 * 5 * 6 * 4
    assert manifest.physical_issued_work == 4 * (2 * 4 * 4 * 4)
    assert manifest.physical_issued_work > manifest.logical_work


def test_split_k_partitions_and_reduction_conserve_work_and_traffic():
    api = _api()

    manifest = _split_k_manifest(api)

    assert tuple(item.logical_k for item in manifest.work_items) == (4, 4)
    assert manifest.logical_work == 2 * 4 * 4 * 8
    assert manifest.physical_issued_work == 2 * (2 * 4 * 4 * 4)
    assert manifest.reduction_logical_work == 16
    assert manifest.reduction_physical_work == 16
    assert manifest.reduction_read_bytes == 2 * 16 * 4
    assert manifest.reduction_write_bytes == 16 * 4
    assert manifest.total_physical_work == 2 * (2 * 4 * 4 * 4) + 16
    assert dict(manifest.final_accumulator_by_tile) == {(0, 0): "final-0"}


def test_split_k_supports_explicit_chained_reduction_dependencies():
    api = _api()
    base = _split_k_manifest(api)
    blocks = tuple(_block("chain", index) for index in range(4))
    work_items = tuple(
        _work_item(
            api,
            work_item_id=f"item-{index}",
            k_start=2 * index,
            k_end=2 * (index + 1),
            issued_k=2,
            accumulator_id=f"partial-{index}",
            cache_access_indices=(index,),
        )
        for index in range(4)
    )
    reductions = (
        _reduction(
            api,
            reduction_id="reduce-left",
            input_accumulator_ids=("partial-0", "partial-1"),
            output_accumulator_id="middle-left",
            dependencies=(),
            cache_access_indices=(),
        ),
        _reduction(
            api,
            reduction_id="reduce-right",
            input_accumulator_ids=("partial-2", "partial-3"),
            output_accumulator_id="middle-right",
            dependencies=(),
            cache_access_indices=(),
        ),
        _reduction(
            api,
            reduction_id="reduce-final",
            input_accumulator_ids=("middle-left", "middle-right"),
            output_accumulator_id="final",
            dependencies=("reduce-left", "reduce-right"),
            cache_access_indices=(),
        ),
    )

    manifest = replace(
        base,
        cache_config=CacheConfig(
            capacity_bytes=16,
            block_bytes=4,
            blocks=blocks,
        ),
        workers=(
            _worker(
                api,
                worker_id="worker-chain",
                work_item_ids=tuple(
                    item.work_item_id for item in work_items
                ),
            ),
        ),
        work_items=work_items,
        reduction_steps=reductions,
        cache_accesses=tuple(
            CacheAccess(block, "read") for block in blocks
        ),
    )

    assert manifest.reduction_by_id["reduce-final"].dependencies == (
        "reduce-left",
        "reduce-right",
    )
    assert dict(manifest.final_accumulator_by_tile) == {(0, 0): "final"}
    assert manifest.reduction_logical_work == 3 * 16
    assert manifest.reduction_physical_work == 3 * 16


def test_manifest_resolves_its_canonical_cache_access_order():
    api = _api()
    manifest = _ordinary_manifest(api)

    resolution = manifest.resolve_cache(InitialCacheState())

    assert tuple(
        transition.block.object_id for transition in resolution.transitions
    ) == (
        "A",
        "B",
        "A",
        "C",
    )
    assert tuple(transition.action for transition in resolution.transitions) == (
        "read_miss",
        "read_miss",
        "evict_clean",
        "overwrite_miss",
    )
    assert resolution.hbm_read_bytes == 8
    assert resolution.hbm_write_bytes == 0


def test_manifest_records_are_immutable_and_detached_from_input_containers():
    api = _api()
    reservation = {"cta_slots": 1}
    work_item_ids = ["item-0"]
    worker = _worker(
        api,
        work_item_ids=work_item_ids,
        per_sm_reservation=reservation,
    )
    manifest = _ordinary_manifest(api, workers=(worker,))

    reservation["cta_slots"] = 2
    work_item_ids.append("unknown")

    assert worker.per_sm_reservation == {"cta_slots": 1}
    assert isinstance(worker.per_sm_reservation, MappingProxyType)
    assert worker.work_item_ids == ("item-0",)
    with pytest.raises(FrozenInstanceError):
        manifest.m = 8
    with pytest.raises(TypeError):
        manifest.work_item_by_id["other"] = manifest.work_items[0]


@pytest.mark.parametrize(
    ("ranges", "message"),
    [
        (((0, 3), (4, 8)), "K coverage gap"),
        (((0, 5), (4, 8)), "overlapping K ranges"),
        (((1, 4), (4, 8)), "K coverage gap"),
        (((0, 4), (4, 9)), "K range outside problem"),
    ],
)
def test_manifest_rejects_invalid_split_k_coverage(ranges, message):
    api = _api()
    base = _split_k_manifest(api)
    items = tuple(
        replace(item, k_start=start, k_end=end, issued_k=end - start)
        for item, (start, end) in zip(base.work_items, ranges, strict=True)
    )

    with pytest.raises(ValueError, match=message):
        replace(base, work_items=items)


def test_manifest_rejects_duplicate_accumulator_producers():
    api = _api()
    base = _split_k_manifest(api)
    items = (
        base.work_items[0],
        replace(base.work_items[1], accumulator_id="partial-0"),
    )

    with pytest.raises(ValueError, match="duplicate accumulator producer"):
        replace(base, work_items=items)


def test_manifest_rejects_orphan_partial_accumulator():
    api = _api()
    base = _split_k_manifest(api)
    item_2 = replace(
        base.work_items[1],
        work_item_id="item-2",
        k_start=6,
        k_end=8,
        issued_k=2,
        accumulator_id="partial-2",
    )
    items = (
        replace(base.work_items[0], k_end=3, issued_k=3),
        replace(base.work_items[1], k_start=3, k_end=6, issued_k=3),
        item_2,
    )
    worker_2 = _worker(
        api,
        worker_id="worker-2",
        work_item_ids=("item-2",),
    )

    with pytest.raises(ValueError, match="orphan accumulator"):
        replace(
            base,
            work_items=items,
            workers=base.workers + (worker_2,),
        )


def test_manifest_rejects_incompatible_reduction_inputs():
    api = _api()
    base = _grid_manifest(api, m=4, n=8, tile_m=4, tile_n=4)
    reduction = _reduction(
        api,
        input_accumulator_ids=("acc-0", "acc-1"),
        output_accumulator_id="final",
        cache_access_indices=(),
    )

    with pytest.raises(ValueError, match="incompatible reduction inputs"):
        replace(base, reduction_steps=(reduction,))


def test_manifest_rejects_missing_final_split_k_reduction():
    api = _api()
    base = _split_k_manifest(api)

    with pytest.raises(ValueError, match="missing final reduction"):
        replace(base, reduction_steps=())


def test_manifest_rejects_invalid_output_tile_coverage():
    api = _api()
    base = _grid_manifest(api, m=4, n=8, tile_m=4, tile_n=4)

    with pytest.raises(ValueError, match="output tile coverage"):
        replace(base, work_items=base.work_items[:1], workers=base.workers[:1])
    with pytest.raises(ValueError, match="output tile"):
        replace(
            base,
            work_items=(
                base.work_items[0],
                replace(base.work_items[1], output_n=2),
            ),
        )


def test_manifest_rejects_duplicate_and_missing_worker_assignment():
    api = _api()
    base = _ordinary_manifest(api)
    duplicate = _worker(
        api,
        worker_id="worker-1",
        work_item_ids=("item-0",),
    )

    with pytest.raises(ValueError, match="duplicate worker assignment"):
        replace(base, workers=base.workers + (duplicate,))
    with pytest.raises(ValueError, match="unassigned work item"):
        replace(base, workers=())
    with pytest.raises(ValueError, match="unknown work item"):
        replace(
            base,
            workers=(replace(base.workers[0], work_item_ids=("unknown",)),),
        )


def test_manifest_rejects_invalid_worker_reservation_and_affinity():
    api = _api()
    base = _ordinary_manifest(api)

    with pytest.raises(ValueError, match="unknown reservation resource"):
        replace(
            base,
            workers=(
                replace(
                    base.workers[0],
                    per_sm_reservation={"unknown": 1},
                ),
            ),
        )
    with pytest.raises(ValueError, match="reservation exceeds"):
        replace(
            base,
            workers=(
                replace(
                    base.workers[0],
                    per_sm_reservation={"cta_slots": 3},
                ),
            ),
        )
    with pytest.raises(ValueError, match="eligible SM"):
        replace(
            base,
            workers=(replace(base.workers[0], eligible_sms={2}),),
        )


def test_manifest_rejects_unknown_duplicate_and_orphan_cache_accesses():
    api = _api()
    base = _ordinary_manifest(api)
    split_k = _split_k_manifest(api)

    with pytest.raises(ValueError, match="unknown cache access reference"):
        replace(
            base,
            work_items=(
                replace(base.work_items[0], cache_access_indices=(0, 1, 3)),
            ),
        )
    with pytest.raises(ValueError, match="duplicate cache access assignment"):
        replace(
            split_k,
            reduction_steps=(
                replace(
                    split_k.reduction_steps[0],
                    cache_access_indices=(2,),
                ),
            ),
        )
    with pytest.raises(ValueError, match="unassigned cache access"):
        replace(
            base,
            work_items=(
                replace(base.work_items[0], cache_access_indices=(0, 1)),
            ),
        )


def test_manifest_rejects_unknown_and_inconsistent_cache_blocks():
    api = _api()
    base = _ordinary_manifest(api)
    unknown = CacheAccess(_block("unknown", 0), "read")
    inconsistent = CacheAccess(_block("A", 0, size=3), "read")

    with pytest.raises(ValueError, match="unknown cache block"):
        replace(base, cache_accesses=(unknown,) + base.cache_accesses[1:])
    with pytest.raises(ValueError, match="inconsistent block size"):
        replace(base, cache_accesses=(inconsistent,) + base.cache_accesses[1:])


def test_manifest_rejects_non_canonical_local_cache_access_order():
    api = _api()
    base = _ordinary_manifest(api)

    with pytest.raises(ValueError, match="cache access order"):
        replace(
            base,
            work_items=(
                replace(base.work_items[0], cache_access_indices=(1, 0, 2)),
            ),
        )


def test_manifest_rejects_invalid_reduction_dependency_topology():
    api = _api()
    base = _split_k_manifest(api)

    with pytest.raises(ValueError, match="reduction dependencies"):
        replace(
            base,
            reduction_steps=(
                replace(base.reduction_steps[0], dependencies=("unknown",)),
            ),
        )
    with pytest.raises(ValueError, match="unknown reduction input"):
        replace(
            base,
            reduction_steps=(
                replace(
                    base.reduction_steps[0],
                    input_accumulator_ids=("partial-0", "unknown"),
                ),
            ),
        )


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda api: replace(_work_item(api), work_item_id=""), "work_item_id"),
        (lambda api: replace(_work_item(api), logical_m=0), "logical_m"),
        (
            lambda api: replace(_work_item(api), issued_m=3),
            "issued extents",
        ),
        (
            lambda api: replace(_work_item(api), k_start=4, k_end=4),
            "K range",
        ),
        (
            lambda api: replace(_worker(api), work_item_ids=()),
            "work_item_ids",
        ),
        (
            lambda api: replace(_worker(api), per_sm_reservation={}),
            "reservation",
        ),
        (
            lambda api: replace(
                _reduction(api), input_accumulator_ids=("partial-0",)
            ),
            "at least two",
        ),
        (
            lambda api: replace(
                _reduction(api),
                input_accumulator_ids=("partial-0", "partial-0"),
            ),
            "duplicate",
        ),
        (
            lambda api: replace(_reduction(api), issued_elements=15),
            "issued_elements",
        ),
    ],
)
def test_manifest_value_objects_reject_invalid_fields(factory, message):
    api = _api()

    with pytest.raises(ValueError, match=message):
        factory(api)


@pytest.mark.parametrize(
    ("updates", "message"),
    [
        ({"m": 0}, "m"),
        ({"a_element_bytes": 0}, "a_element_bytes"),
        ({"tile_k": 0}, "tile_k"),
        ({"output_visibility": "DRAM"}, "output_visibility"),
        ({"workers": ()}, "unassigned work item"),
        ({"work_items": ()}, "output tile coverage"),
        ({"cache_accesses": ()}, "cache_accesses"),
    ],
)
def test_manifest_rejects_invalid_problem_and_topology_fields(updates, message):
    api = _api()
    base = _ordinary_manifest(api)

    with pytest.raises(ValueError, match=message):
        replace(base, **updates)


def test_manifest_rejects_duplicate_identifiers():
    api = _api()
    base = _ordinary_manifest(api)

    with pytest.raises(ValueError, match="duplicate worker id"):
        replace(base, workers=base.workers + base.workers)
    with pytest.raises(ValueError, match="duplicate work item id"):
        replace(base, work_items=base.work_items + base.work_items)

    split = _split_k_manifest(api)
    with pytest.raises(ValueError, match="duplicate reduction id"):
        replace(
            split,
            reduction_steps=split.reduction_steps + split.reduction_steps,
        )


def test_manifest_contract_is_exported_from_the_public_package():
    package = import_module("event_simulator")
    expected = {
        "GemmLaunchManifest",
        "GemmReductionStep",
        "GemmWorkItem",
        "GemmWorker",
    }

    assert expected <= set(package.__all__)
    assert all(hasattr(package, name) for name in expected)
