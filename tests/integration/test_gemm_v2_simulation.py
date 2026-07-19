"""Integration tests for authoritative GEMM manifest lowering."""

from inspect import Parameter, signature

import pytest

from event_simulator import (
    CacheAccess,
    CacheBlock,
    CacheConfig,
    EventGraph,
    GemmLaunchManifest,
    GemmReductionStep,
    GemmWorkItem,
    GemmWorker,
    InitialCacheState,
    ResidentCacheBlock,
    ResourceConfig,
    build_report,
    derive_calibration,
    load_hardware_config,
    lower_gemm_v2,
    schedule,
)


@pytest.fixture
def h100_calibration():
    return derive_calibration(load_hardware_config("hardware/H100.json"))


def _resources() -> ResourceConfig:
    return ResourceConfig(
        global_capacities={
            "hbm_bandwidth": 1,
            "l2_bandwidth": 1,
            "launch": 1,
        },
        sm_count=2,
        per_sm_capacities={
            "alu": 1,
            "cta_slots": 1,
            "tensor_core": 1,
        },
    )


def _block(object_id: str, index: int) -> CacheBlock:
    return CacheBlock(object_id=object_id, block_index=index, size_bytes=4)


def _ordinary_manifest() -> GemmLaunchManifest:
    a = _block("A", 0)
    b = _block("B", 0)
    c = _block("C", 0)
    return GemmLaunchManifest(
        m=4,
        n=4,
        k=4,
        a_element_bytes=2,
        b_element_bytes=2,
        output_element_bytes=2,
        accumulator_bytes=4,
        tile_m=4,
        tile_n=4,
        tile_k=4,
        output_visibility="L2",
        resource_config=_resources(),
        cache_config=CacheConfig(
            capacity_bytes=8,
            block_bytes=4,
            blocks=(a, b, c),
        ),
        workers=(
            GemmWorker(
                worker_id="worker-0",
                work_item_ids=("item-0",),
                per_sm_reservation={"cta_slots": 1},
                eligible_sms=frozenset({0}),
            ),
        ),
        work_items=(
            GemmWorkItem(
                work_item_id="item-0",
                output_m=0,
                output_n=0,
                logical_m=4,
                logical_n=4,
                k_start=0,
                k_end=4,
                issued_m=8,
                issued_n=8,
                issued_k=8,
                accumulator_id="acc-0",
                cache_access_indices=(0, 1, 2),
            ),
        ),
        reduction_steps=(),
        cache_accesses=(
            CacheAccess(a, "read"),
            CacheAccess(b, "read"),
            CacheAccess(c, "overwrite", is_output=True),
        ),
    )


def _persistent_manifest() -> GemmLaunchManifest:
    blocks = tuple(
        _block(object_id, index)
        for object_id, index in (
            ("A", 0),
            ("B", 0),
            ("C", 0),
            ("A", 1),
            ("B", 1),
            ("C", 1),
        )
    )
    return GemmLaunchManifest(
        m=4,
        n=8,
        k=4,
        a_element_bytes=2,
        b_element_bytes=2,
        output_element_bytes=2,
        accumulator_bytes=4,
        tile_m=4,
        tile_n=4,
        tile_k=4,
        output_visibility="L2",
        resource_config=_resources(),
        cache_config=CacheConfig(
            capacity_bytes=24,
            block_bytes=4,
            blocks=blocks,
        ),
        workers=(
            GemmWorker(
                worker_id="worker-0",
                work_item_ids=("item-0", "item-1"),
                per_sm_reservation={"cta_slots": 1},
                eligible_sms=frozenset({1}),
            ),
        ),
        work_items=(
            GemmWorkItem(
                work_item_id="item-0",
                output_m=0,
                output_n=0,
                logical_m=4,
                logical_n=4,
                k_start=0,
                k_end=4,
                issued_m=4,
                issued_n=4,
                issued_k=4,
                accumulator_id="acc-0",
                cache_access_indices=(0, 1, 2),
            ),
            GemmWorkItem(
                work_item_id="item-1",
                output_m=0,
                output_n=4,
                logical_m=4,
                logical_n=4,
                k_start=0,
                k_end=4,
                issued_m=4,
                issued_n=4,
                issued_k=4,
                accumulator_id="acc-1",
                cache_access_indices=(3, 4, 5),
            ),
        ),
        reduction_steps=(),
        cache_accesses=(
            CacheAccess(blocks[0], "read"),
            CacheAccess(blocks[1], "read"),
            CacheAccess(blocks[2], "overwrite", is_output=True),
            CacheAccess(blocks[3], "read"),
            CacheAccess(blocks[4], "read"),
            CacheAccess(blocks[5], "overwrite", is_output=True),
        ),
    )


def _split_k_manifest() -> GemmLaunchManifest:
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
    by_identity = {block.identity: block for block in catalog}
    accesses = (
        CacheAccess(by_identity[("A", 0)], "read"),
        CacheAccess(by_identity[("B", 0)], "read"),
        CacheAccess(by_identity[("partial", 0)], "overwrite"),
        CacheAccess(by_identity[("A", 1)], "read"),
        CacheAccess(by_identity[("B", 1)], "read"),
        CacheAccess(by_identity[("partial", 1)], "overwrite"),
        CacheAccess(by_identity[("partial", 0)], "read"),
        CacheAccess(by_identity[("partial", 1)], "read"),
        CacheAccess(by_identity[("C", 0)], "overwrite", is_output=True),
    )
    return GemmLaunchManifest(
        m=4,
        n=4,
        k=8,
        a_element_bytes=2,
        b_element_bytes=2,
        output_element_bytes=2,
        accumulator_bytes=4,
        tile_m=4,
        tile_n=4,
        tile_k=4,
        output_visibility="HBM",
        resource_config=_resources(),
        cache_config=CacheConfig(
            capacity_bytes=16,
            block_bytes=4,
            blocks=catalog,
        ),
        workers=(
            GemmWorker(
                worker_id="worker-0",
                work_item_ids=("item-0",),
                per_sm_reservation={"cta_slots": 1},
                eligible_sms=frozenset({0}),
            ),
            GemmWorker(
                worker_id="worker-1",
                work_item_ids=("item-1",),
                per_sm_reservation={"cta_slots": 1},
                eligible_sms=frozenset({1}),
            ),
        ),
        work_items=(
            GemmWorkItem(
                work_item_id="item-0",
                output_m=0,
                output_n=0,
                logical_m=4,
                logical_n=4,
                k_start=0,
                k_end=4,
                issued_m=4,
                issued_n=4,
                issued_k=4,
                accumulator_id="partial-0",
                cache_access_indices=(0, 1, 2),
            ),
            GemmWorkItem(
                work_item_id="item-1",
                output_m=0,
                output_n=0,
                logical_m=4,
                logical_n=4,
                k_start=4,
                k_end=8,
                issued_m=4,
                issued_n=4,
                issued_k=4,
                accumulator_id="partial-1",
                cache_access_indices=(3, 4, 5),
            ),
        ),
        reduction_steps=(
            GemmReductionStep(
                reduction_id="reduce-0",
                input_accumulator_ids=("partial-0", "partial-1"),
                output_accumulator_id="final-0",
                logical_elements=16,
                issued_elements=16,
                cache_access_indices=(6, 7, 8),
            ),
        ),
        cache_accesses=accesses,
    )


def _lower(manifest, calibration):
    return lower_gemm_v2(
        "gemm",
        manifest=manifest,
        calibration=calibration,
        initial_cache_state=InitialCacheState(),
    )


def _is_ancestor(graph: EventGraph, source: str, target: str) -> bool:
    pending = [source]
    visited = set()
    while pending:
        event_id = pending.pop()
        if event_id == target:
            return True
        if event_id in visited:
            continue
        visited.add(event_id)
        pending.extend(graph.successors[event_id])
    return False


def test_lower_gemm_v2_has_only_the_manifest_signature(h100_calibration):
    parameters = signature(lower_gemm_v2).parameters

    assert tuple(parameters) == (
        "kernel_id",
        "manifest",
        "calibration",
        "initial_cache_state",
        "stream_id",
    )
    assert parameters["manifest"].kind is Parameter.KEYWORD_ONLY
    assert parameters["initial_cache_state"].default is Parameter.empty
    assert not {
        "m",
        "n",
        "k",
        "tile_m",
        "tile_n",
        "tile_k",
        "hardware",
        "max_ctas_per_sm",
        "element_bytes",
    } & set(parameters)

    with pytest.raises(TypeError):
        lower_gemm_v2(
            "gemm",
            manifest=_ordinary_manifest(),
            calibration=h100_calibration,
        )


def test_lower_gemm_v2_returns_normalized_event_graph(h100_calibration):
    graph = _lower(_ordinary_manifest(), h100_calibration)

    assert isinstance(graph, EventGraph)
    assert graph.events
    assert {event.stream_id for event in graph.events} == {"stream-0"}
    assert len(graph.lifetimes) == 1


def test_cache_traffic_bytes_match_the_single_resolution(h100_calibration):
    manifest = _split_k_manifest()
    resolution = manifest.resolve_cache(InitialCacheState())
    graph = _lower(manifest, h100_calibration)

    assert sum(
        event.bytes for event in graph.events if event.event_type == "HBMRead"
    ) == resolution.hbm_read_bytes
    assert sum(
        event.bytes for event in graph.events if event.event_type == "HBMWrite"
    ) == resolution.hbm_write_bytes
    assert sum(
        event.bytes for event in graph.events if event.event_type == "L2Read"
    ) == resolution.l2_read_bytes
    assert sum(
        event.bytes for event in graph.events if event.event_type == "L2Write"
    ) == resolution.l2_write_bytes


def test_warm_initial_state_is_preserved_through_cache_traffic_lowering(
    h100_calibration,
):
    manifest = _ordinary_manifest()
    initial_state = InitialCacheState(
        resident_blocks=(
            ResidentCacheBlock(
                manifest.cache_config.block_by_identity[("A", 0)]
            ),
            ResidentCacheBlock(
                manifest.cache_config.block_by_identity[("B", 0)]
            ),
        )
    )
    resolution = manifest.resolve_cache(initial_state)
    graph = lower_gemm_v2(
        "gemm-warm",
        manifest=manifest,
        calibration=h100_calibration,
        initial_cache_state=initial_state,
    )

    assert resolution.hbm_read_bytes == 0
    assert sum(
        event.bytes for event in graph.events if event.event_type == "HBMRead"
    ) == 0
    assert sum(
        event.bytes for event in graph.events if event.event_type == "L2Read"
    ) == resolution.l2_read_bytes


def test_l2_output_visibility_emits_no_final_hbm_flush(h100_calibration):
    graph = _lower(_ordinary_manifest(), h100_calibration)

    assert not any(
        event.event_type == "HBMWrite" and event.cta_id is None
        for event in graph.events
    )


def test_clean_eviction_emits_no_resource_time_event(h100_calibration):
    manifest = _ordinary_manifest()
    resolution = manifest.resolve_cache(InitialCacheState())
    assert any(
        transition.action == "evict_clean"
        for transition in resolution.transitions
    )

    graph = _lower(manifest, h100_calibration)
    cache_events = tuple(
        event
        for event in graph.events
        if event.event_type in {"HBMRead", "HBMWrite", "L2Read", "L2Write"}
    )
    expansion_size = {
        "read_hit": 1,
        "read_miss": 3,
        "overwrite_hit": 1,
        "overwrite_miss": 1,
        "evict_clean": 0,
        "evict_dirty": 2,
        "flush_dirty_output": 2,
    }

    assert len(cache_events) == sum(
        expansion_size[transition.action]
        for transition in resolution.transitions
    )
    assert all(event.bytes > 0 for event in cache_events)


def test_each_worker_owns_one_acquire_to_release_lifetime(h100_calibration):
    manifest = _split_k_manifest()
    graph = _lower(manifest, h100_calibration)
    launch = next(
        event for event in graph.events if event.event_type == "KernelLaunch"
    )

    assert len(graph.lifetimes) == len(manifest.workers)
    for worker in manifest.workers:
        lifetime = next(
            item
            for item in graph.lifetimes
            if item.lifetime_id.endswith(worker.worker_id)
        )
        acquire = graph.by_id[lifetime.acquire_event_id]
        release = graph.by_id[lifetime.release_event_id]
        assert lifetime.per_sm_reservation == worker.per_sm_reservation
        assert lifetime.eligible_sms == worker.eligible_sms
        assert acquire.duration == 0.0
        assert acquire.dependencies == (launch.event_id,)
        assert release.duration == 0.0
        assert release.dependencies
        assert all(
            event.eligible_sms is None
            for event in graph.events
            if event.lifetime_id == lifetime.lifetime_id
        )


def test_persistent_worker_preserves_work_item_order(h100_calibration):
    graph = _lower(_persistent_manifest(), h100_calibration)
    first = tuple(
        event for event in graph.events if event.cta_id == "item-0"
    )
    second = tuple(
        event for event in graph.events if event.cta_id == "item-1"
    )

    assert first
    assert second
    assert any(
        _is_ancestor(graph, source.event_id, target.event_id)
        for source in first
        for target in second
    )
    assert not any(
        _is_ancestor(graph, source.event_id, target.event_id)
        for source in second
        for target in first
    )


def test_mma_count_uses_physical_issued_work(h100_calibration):
    manifest = _ordinary_manifest()
    graph = _lower(manifest, h100_calibration)
    mma = next(event for event in graph.events if event.event_type == "MMA")
    work_item = manifest.work_items[0]

    assert work_item.logical_work == 128
    assert work_item.physical_issued_work == 1024
    assert mma.instruction_count == 4
    assert mma.duration == h100_calibration.duration("MMA", 4)


def test_split_k_reduction_waits_for_worker_releases(h100_calibration):
    graph = _lower(_split_k_manifest(), h100_calibration)
    reduction = next(
        event for event in graph.events if event.event_type == "Reduction"
    )
    release_ids = {
        lifetime.release_event_id for lifetime in graph.lifetimes
    }

    assert reduction.lifetime_id is None
    assert reduction.eligible_sms is None
    assert dict(reduction.per_sm_demand) == {"alu": 1}
    assert all(
        _is_ancestor(graph, release_id, reduction.event_id)
        for release_id in release_ids
    )
    assert all(
        event.lifetime_id is None
        for event in graph.events
        if event.cta_id == "reduce-0"
    )


def test_output_flush_is_an_explicit_completion_predecessor(h100_calibration):
    graph = _lower(_split_k_manifest(), h100_calibration)
    completion = next(
        event for event in graph.events if event.event_type == "KernelComplete"
    )
    flush_writes = tuple(
        event
        for event in graph.events
        if event.event_type == "HBMWrite" and event.cta_id is None
    )

    assert flush_writes
    assert {event.event_id for event in flush_writes} <= set(
        completion.dependencies
    )


def test_manifest_graph_schedules_and_reports_provenance(h100_calibration):
    manifest = _split_k_manifest()
    graph = _lower(manifest, h100_calibration)
    result = schedule(graph, manifest.resource_config)
    report = build_report(result)

    assert result.graph is graph
    assert report.feasible_makespan == result.makespan
    assert 0.0 < report.dependency_critical_path <= report.feasible_makespan
    assert report.dependency_critical_path_event_ids
    assert report.resource_busy_time["hbm_bandwidth"] > 0.0
    assert report.resource_busy_time["l2_bandwidth"] > 0.0
    assert report.resource_busy_time["tensor_core"] > 0.0
    assert report.resource_busy_time["alu"] > 0.0
    assert not hasattr(report, "makespan")
    assert not hasattr(report, "critical_path")


def test_manifest_graph_schedule_is_invariant_to_event_tuple_order(
    h100_calibration,
):
    manifest = _split_k_manifest()
    graph = _lower(manifest, h100_calibration)
    permuted = EventGraph(
        events=tuple(reversed(graph.events)),
        lifetimes=tuple(reversed(graph.lifetimes)),
    )

    original = schedule(graph, manifest.resource_config)
    reordered = schedule(permuted, manifest.resource_config)

    assert reordered.makespan == original.makespan
    assert reordered.entries == original.entries
