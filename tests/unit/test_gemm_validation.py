"""Tests for authoritative-manifest GEMM validation."""

from types import SimpleNamespace

import pandas as pd
import pytest

from event_simulator import (
    CacheAccess,
    CacheBlock,
    CacheConfig,
    EventGraph,
    GemmLaunchManifest,
    GemmWorkItem,
    GemmWorker,
    InitialCacheState,
    ResourceConfig,
    derive_calibration,
    load_hardware_config,
)
from tests.validation import validate_gemm_v2 as validator


@pytest.fixture
def h100_components():
    hardware = load_hardware_config("hardware/H100.json")
    return hardware, derive_calibration(hardware)


def _resource_config() -> ResourceConfig:
    return ResourceConfig(
        global_capacities={
            "hbm_bandwidth": 1,
            "l2_bandwidth": 1,
            "launch": 1,
        },
        sm_count=1,
        per_sm_capacities={
            "alu": 1,
            "cta_slots": 1,
            "tensor_core": 1,
        },
    )


def _manifest() -> GemmLaunchManifest:
    a = CacheBlock("A", 0, 4)
    b = CacheBlock("B", 0, 4)
    c = CacheBlock("C", 0, 4)
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
        resource_config=_resource_config(),
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
                issued_m=4,
                issued_n=4,
                issued_k=4,
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


def _row(*, index=7, **overrides):
    values = {
        "M": 4,
        "N": 4,
        "K": 4,
        "avg_duration": 10.0,
        "tile_M": 4,
        "tile_N": 4,
        "tile_K": 4,
        "is_split_k": 0,
        "cta_count": 1,
    }
    values.update(overrides)
    return pd.Series(values, name=index)


def test_classical_roofline_uses_chip_wide_compute_and_matched_memory_boundary(
    h100_components,
):
    hardware, _ = h100_components
    row = _row(M=2048, N=4096, K=1024)

    result = validator.classical_roofline(row, hardware)

    expected_compute = 2.0 * 2048 * 4096 * 1024 / hardware.tc_bf16_flops_per_us
    expected_hbm_input = (2048 * 1024 + 4096 * 1024) * 2 / hardware.mem_bandwidth_bytes_per_us
    expected_l2_output = 2048 * 4096 * 2 / hardware.l2_bandwidth_bytes_per_us
    assert result == pytest.approx(
        max(expected_compute, expected_hbm_input, expected_l2_output)
    )


def test_des_predict_passes_authoritative_manifest_and_explicit_cold_state(
    monkeypatch, h100_components
):
    _, calibration = h100_components
    row = _row()
    manifest = _manifest()
    captured = {}

    def fake_lowering(*args, **kwargs):
        captured.update(kwargs)
        return EventGraph(())

    monkeypatch.setattr(validator, "lower_gemm_v2", fake_lowering)
    monkeypatch.setattr(
        validator,
        "schedule",
        lambda graph, resource_config: SimpleNamespace(makespan=1.25),
    )

    result = validator.des_predict(row, calibration, {row.name: manifest})

    assert result == 1.25
    assert captured["manifest"] is manifest
    assert captured["calibration"] is calibration
    assert captured["initial_cache_state"] == InitialCacheState()


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"M": 8}, "manifest_problem_shape_mismatch"),
        ({"tile_K": 8}, "manifest_tile_mismatch"),
        ({"cta_count": 2}, "cta_count_mismatch"),
    ],
)
def test_des_predict_rejects_manifest_mismatches_explicitly(
    overrides, reason, h100_components
):
    _, calibration = h100_components
    row = _row(**overrides)
    unsupported_error = getattr(validator, "UnsupportedGemmRow", ValueError)

    with pytest.raises(unsupported_error, match=reason):
        validator.des_predict(row, calibration, {row.name: _manifest()})


def test_des_predict_counts_missing_authoritative_manifest(h100_components):
    _, calibration = h100_components

    with pytest.raises(
        validator.UnsupportedGemmRow,
        match="missing_authoritative_manifest",
    ):
        validator.des_predict(_row(), calibration, {})


def test_des_predict_does_not_use_split_k_heuristics(h100_components):
    _, calibration = h100_components
    row = _row(is_split_k=1)

    result = validator.des_predict(row, calibration, {row.name: _manifest()})

    assert result > 0.0


def test_des_predict_propagates_unexpected_lowering_errors(
    monkeypatch, h100_components
):
    _, calibration = h100_components
    row = _row()

    def fail_lowering(*args, **kwargs):
        raise RuntimeError("unexpected lowering failure")

    monkeypatch.setattr(validator, "lower_gemm_v2", fail_lowering)

    with pytest.raises(RuntimeError, match="unexpected lowering failure"):
        validator.des_predict(row, calibration, {row.name: _manifest()})


def test_des_predict_propagates_unexpected_scheduling_errors(
    monkeypatch, h100_components
):
    _, calibration = h100_components
    row = _row()

    def fail_scheduling(*args, **kwargs):
        raise RuntimeError("unexpected scheduling failure")

    monkeypatch.setattr(validator, "schedule", fail_scheduling)

    with pytest.raises(RuntimeError, match="unexpected scheduling failure"):
        validator.des_predict(row, calibration, {row.name: _manifest()})


def test_prediction_summary_compares_tightness_only_on_both_valid_rows():
    summarize = getattr(validator, "summarize_predictions", None)
    assert summarize is not None, "summarize_predictions is missing"

    summary = summarize(
        des_times=[8.0, 11.0, 6.0],
        roofline_times=[7.0, 5.0, 12.0],
        actual_times=[10.0, 10.0, 10.0],
    )

    assert summary["evaluated"] == 3
    assert summary["des_violations"] == 1
    assert summary["roofline_violations"] == 1
    assert summary["both_valid"] == 1
    assert summary["des_strictly_tighter"] == 1
    assert summary["des_mean_gap"] == pytest.approx(0.2)
    assert summary["roofline_mean_gap"] == pytest.approx(0.3)


def test_evaluate_sample_counts_unsupported_reasons(h100_components):
    evaluate = getattr(validator, "evaluate_sample", None)
    assert evaluate is not None, "evaluate_sample is missing"
    hardware, calibration = h100_components
    sample = pd.DataFrame(
        [
            dict(_row(index=10)),
            dict(_row(index=20)),
            dict(_row(index=30, cta_count=2)),
            dict(_row(index=40, avg_duration=0.0)),
        ],
        index=[10, 20, 30, 40],
    )
    manifest = _manifest()

    batch = evaluate(
        sample,
        hardware,
        calibration,
        {10: manifest, 30: manifest, 40: manifest},
    )

    assert len(batch.actual_times) == 1
    assert batch.unsupported_counts == {
        "cta_count_mismatch": 1,
        "invalid_actual_time": 1,
        "missing_authoritative_manifest": 1,
    }
    assert len(batch.simulator_runtimes) == 1
    assert batch.simulator_runtimes[0] > 0.0


def test_category_partition_is_disjoint_and_exhaustive():
    partition = getattr(validator, "partition_categories", None)
    assert partition is not None, "partition_categories is missing"
    rows = pd.DataFrame(
        [
            {"row_id": "large", "M": 1024, "N": 1024, "K": 1024},
            {"row_id": "medium", "M": 512, "N": 4096, "K": 4096},
            {"row_id": "small", "M": 128, "N": 4096, "K": 4096},
            {"row_id": "other", "M": 2048, "N": 512, "K": 4096},
        ]
    )

    categories = partition(rows)

    assert list(categories) == ["Large", "Medium", "Small", "Other"]
    assert {
        label: frame["row_id"].tolist() for label, frame in categories.items()
    } == {
        "Large": ["large"],
        "Medium": ["medium"],
        "Small": ["small"],
        "Other": ["other"],
    }
    assert sum(len(frame) for frame in categories.values()) == len(rows)
