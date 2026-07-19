"""Tests for the matched-boundary GEMM validation harness."""

from types import SimpleNamespace

import pandas as pd
import pytest

from event_simulator import (
    derive_calibration,
    derive_resource_config,
    load_hardware_config,
)
from tests.validation import validate_gemm_v2 as validator


@pytest.fixture
def h100_components():
    hardware = load_hardware_config("hardware/H100.json")
    return (
        hardware,
        derive_calibration(hardware),
        derive_resource_config(hardware, operator_type="gemm_v2"),
    )


def _row(**overrides):
    row = {
        "M": 128,
        "N": 256,
        "K": 64,
        "avg_duration": 10.0,
        "tile_M": 64,
        "tile_N": 64,
        "tile_K": 32,
        "is_split_k": 0,
        "cta_count": 8,
    }
    row.update(overrides)
    return row


def test_classical_roofline_uses_chip_wide_compute_and_matched_memory_boundary(
    h100_components,
):
    hardware, _, _ = h100_components
    row = _row(M=2048, N=4096, K=1024)

    result = validator.classical_roofline(row, hardware)

    expected_compute = 2.0 * 2048 * 4096 * 1024 / hardware.tc_bf16_flops_per_us
    expected_hbm_input = (2048 * 1024 + 4096 * 1024) * 2 / hardware.mem_bandwidth_bytes_per_us
    expected_l2_output = 2048 * 4096 * 2 / hardware.l2_bandwidth_bytes_per_us
    assert result == pytest.approx(
        max(expected_compute, expected_hbm_input, expected_l2_output)
    )


def test_des_predict_passes_dataset_tile_k(monkeypatch, h100_components):
    hardware, calibration, resources = h100_components
    captured = {}

    def fake_lowering(*args, **kwargs):
        captured.update(kwargs)
        return []

    monkeypatch.setattr(validator, "lower_gemm_v2", fake_lowering)
    monkeypatch.setattr(
        validator, "schedule", lambda events, resource_config: SimpleNamespace(makespan=1.25)
    )

    result = validator.des_predict(
        _row(tile_K=48), hardware, calibration, resources
    )

    assert result == 1.25
    assert captured["tile_k"] == 48


@pytest.mark.parametrize(
    ("row", "reason"),
    [
        (_row(is_split_k=1), "split_k"),
        (_row(cta_count=7), "cta_count_mismatch"),
        (_row(tile_K=0), "non_positive_tile"),
        (_row(tile_K=1.5), "non_positive_tile"),
        (_row(is_split_k=0.5), "invalid_split_k"),
    ],
)
def test_des_predict_rejects_unsupported_rows_explicitly(
    row, reason, h100_components
):
    hardware, calibration, resources = h100_components
    unsupported_error = getattr(validator, "UnsupportedGemmRow", ValueError)

    with pytest.raises(unsupported_error, match=reason):
        validator.des_predict(row, hardware, calibration, resources)


def test_des_predict_propagates_unexpected_lowering_errors(
    monkeypatch, h100_components
):
    hardware, calibration, resources = h100_components

    def fail_lowering(*args, **kwargs):
        raise RuntimeError("unexpected lowering failure")

    monkeypatch.setattr(validator, "lower_gemm_v2", fail_lowering)

    with pytest.raises(RuntimeError, match="unexpected lowering failure"):
        validator.des_predict(_row(), hardware, calibration, resources)


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
    hardware, calibration, resources = h100_components
    sample = pd.DataFrame(
        [
            _row(M=16, N=16, K=16, tile_M=8, tile_N=8, tile_K=8, cta_count=4),
            _row(is_split_k=1),
            _row(cta_count=7),
            _row(avg_duration=0.0),
        ]
    )

    batch = evaluate(sample, hardware, calibration, resources)

    assert len(batch.actual_times) == 1
    assert batch.unsupported_counts == {
        "cta_count_mismatch": 1,
        "invalid_actual_time": 1,
        "split_k": 1,
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
