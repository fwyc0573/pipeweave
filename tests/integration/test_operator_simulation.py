import json
from math import ceil

from event_simulator import (
    EventGraph,
    PrimitiveCalibration,
    ResourceConfig,
    build_report,
    lower_gemm,
    lower_rmsnorm,
    lower_silu_and_mul,
    schedule,
)


CALIBRATION = PrimitiveCalibration(
    {
        "KernelLaunch": 0.5,
        "CTAAdmission": 0.1,
        "GlobalLoad": 0.01,
        "GlobalStore": 0.02,
        "MMA": 0.001,
        "FMA": 0.002,
        "SFU": 0.003,
        "Barrier": 0.04,
        "Reduction": 0.005,
        "KernelComplete": 0.1,
    }
)

RESOURCES = ResourceConfig(
    global_capacities={
        "hbm_bandwidth": 2,
        "launch": 1,
        "l2_bandwidth": 2,
    },
    sm_count=2,
    per_sm_capacities={
        "alu": 1,
        "sfu": 1,
        "barrier": 1,
        "cta_slots": 1,
        "tensor_core": 1,
    },
)


def test_gemm_lowering_emits_cta_wave_events():
    graph = lower_gemm(
        "gemm-0",
        m=256,
        n=256,
        k=64,
        tile_m=128,
        tile_n=128,
        calibration=CALIBRATION,
    )

    event_types = [event.event_type for event in graph.events]
    cta_ids = {
        event.cta_id for event in graph.events if event.cta_id is not None
    }

    assert len(cta_ids) == 4
    assert event_types.count("CTAAdmission") == 4
    assert event_types.count("MMA") == 4
    assert event_types.count("GlobalStore") == 4
    assert event_types.count("KernelComplete") == 1


def test_gemm_lowering_counts_two_flops_per_multiply_accumulate():
    graph = lower_gemm(
        "gemm-work",
        m=16,
        n=16,
        k=256,
        tile_m=16,
        tile_n=16,
        calibration=CALIBRATION,
    )

    mma_event = next(
        event for event in graph.events if event.event_type == "MMA"
    )
    expected_instructions = ceil(2 * 16 * 16 * 256 / 256)

    assert expected_instructions == 512
    assert mma_event.instruction_count == expected_instructions
    assert mma_event.duration == CALIBRATION.duration("MMA", expected_instructions)


def test_rmsnorm_lowering_emits_reduction_and_barrier_events():
    graph = lower_rmsnorm(
        "rmsnorm-0", rows=2, hidden_size=128, calibration=CALIBRATION
    )
    event_types = [event.event_type for event in graph.events]

    assert "Reduction" in event_types
    assert "Barrier" in event_types
    reduction = next(
        event for event in graph.events if event.event_type == "Reduction"
    )
    barrier = next(
        event for event in graph.events if event.event_type == "Barrier"
    )
    assert barrier.dependencies == (reduction.event_id,)
    assert event_types.count("KernelComplete") == 1


def test_silu_and_mul_lowering_emits_load_compute_store_events():
    graph = lower_silu_and_mul(
        "silu-0", elements=256, calibration=CALIBRATION
    )
    event_types = {event.event_type for event in graph.events}

    assert event_types == {
        "KernelLaunch",
        "GlobalLoad",
        "SFU",
        "FMA",
        "GlobalStore",
        "KernelComplete",
    }
    by_type = {event.event_type: event for event in graph.events}
    assert by_type["GlobalLoad"].dependencies == (
        by_type["KernelLaunch"].event_id,
    )
    assert by_type["SFU"].dependencies == (by_type["GlobalLoad"].event_id,)
    assert by_type["FMA"].dependencies == (by_type["SFU"].event_id,)
    assert by_type["GlobalStore"].dependencies == (by_type["FMA"].event_id,)
    assert by_type["KernelComplete"].dependencies == (
        by_type["GlobalStore"].event_id,
    )


def test_full_simulation_report_contains_timeline_and_numeric_metrics():
    graph = lower_gemm(
        "gemm-0",
        m=128,
        n=128,
        k=64,
        tile_m=128,
        tile_n=128,
        calibration=CALIBRATION,
    )

    result = schedule(graph, RESOURCES)
    report = build_report(result)
    serialized = json.dumps(report.to_dict(), sort_keys=True)

    assert report.feasible_makespan > 0.0
    assert 0.0 < report.dependency_critical_path <= report.feasible_makespan
    assert report.dependency_critical_path_event_ids[0] == "gemm-0:launch"
    assert report.dependency_critical_path_event_ids[-1] == "gemm-0:complete"
    assert report.kernel_durations["gemm-0"] > 0.0
    assert report.resource_busy_time["hbm_bandwidth"] > 0.0
    assert len(report.timeline) == len(graph.events)
    assert '"dependency_critical_path"' in serialized
    assert '"feasible_makespan"' in serialized


def test_empty_simulation_produces_an_empty_zero_duration_report():
    graph = EventGraph(())
    resources = ResourceConfig(
        global_capacities={},
        sm_count=1,
        per_sm_capacities={},
    )
    result = schedule(graph, resources)
    report = build_report(result)

    assert report.feasible_makespan == 0.0
    assert report.dependency_critical_path == 0.0
    assert report.dependency_critical_path_event_ids == ()
    assert report.timeline == ()


def test_lowering_fails_when_required_calibration_is_missing():
    calibration = PrimitiveCalibration({"KernelLaunch": 1.0})

    try:
        lower_silu_and_mul("silu-0", elements=1, calibration=calibration)
    except ValueError as error:
        assert "missing primitive calibration" in str(error)
    else:
        raise AssertionError("Expected missing calibration to fail")


def test_calibration_rejects_non_numeric_duration():
    try:
        PrimitiveCalibration({"MMA": "0.1"})
    except ValueError as error:
        assert "primitive duration" in str(error)
    else:
        raise AssertionError("Expected non-numeric calibration to fail")
