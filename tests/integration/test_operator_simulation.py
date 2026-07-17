import json

from event_simulator import (
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
    {
        "launch": 1,
        "sm": 2,
        "global_memory": 2,
        "tensor_core": 2,
        "alu": 2,
        "sfu": 1,
        "barrier": 2,
    }
)


def test_gemm_lowering_emits_cta_wave_events():
    events = lower_gemm(
        "gemm-0",
        m=256,
        n=256,
        k=64,
        tile_m=128,
        tile_n=128,
        calibration=CALIBRATION,
    )

    event_types = [event.event_type for event in events]
    cta_ids = {event.cta_id for event in events if event.cta_id is not None}

    assert len(cta_ids) == 4
    assert event_types.count("CTAAdmission") == 4
    assert event_types.count("MMA") == 4
    assert event_types.count("GlobalStore") == 4
    assert event_types[-1] == "KernelComplete"


def test_rmsnorm_lowering_emits_reduction_and_barrier_events():
    events = lower_rmsnorm(
        "rmsnorm-0", rows=2, hidden_size=128, calibration=CALIBRATION
    )
    event_types = [event.event_type for event in events]

    assert "Reduction" in event_types
    assert "Barrier" in event_types
    assert event_types.index("Reduction") < event_types.index("Barrier")
    assert event_types[-1] == "KernelComplete"


def test_silu_and_mul_lowering_emits_load_compute_store_events():
    events = lower_silu_and_mul(
        "silu-0", elements=256, calibration=CALIBRATION
    )
    event_types = [event.event_type for event in events]

    assert event_types == [
        "KernelLaunch",
        "GlobalLoad",
        "SFU",
        "FMA",
        "GlobalStore",
        "KernelComplete",
    ]


def test_full_simulation_report_contains_timeline_and_numeric_metrics():
    events = []
    events.extend(
        lower_gemm(
            "gemm-0",
            m=128,
            n=128,
            k=64,
            tile_m=128,
            tile_n=128,
            calibration=CALIBRATION,
        )
    )
    events.extend(
        lower_silu_and_mul(
            "silu-0", elements=128, calibration=CALIBRATION, stream_id="stream-0"
        )
    )

    result = schedule(events, RESOURCES)
    report = build_report(result)
    serialized = json.dumps(report.to_dict(), sort_keys=True)

    assert report.makespan > 0.0
    assert report.critical_path == report.makespan
    assert report.critical_path_event_ids[0] == "gemm-0:launch"
    assert report.critical_path_event_ids[-1] == "silu-0:complete"
    assert report.kernel_durations["gemm-0"] > 0.0
    assert report.kernel_durations["silu-0"] > 0.0
    assert report.resource_busy_time["global_memory"] > 0.0
    assert len(report.timeline) == len(events)
    assert '"critical_path"' in serialized


def test_empty_simulation_produces_an_empty_zero_duration_report():
    result = schedule([], ResourceConfig({}))
    report = build_report(result)

    assert report.makespan == 0.0
    assert report.critical_path == 0.0
    assert report.critical_path_event_ids == ()
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
