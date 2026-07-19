"""Tests for validated DES-bound comparison metrics."""

from math import inf, nan

import pytest

import event_simulator


def compare_des_bound(*args, **kwargs):
    """Call the package-level API after asserting that it exists."""
    function = getattr(event_simulator, "compare_des_bound", None)
    assert function is not None, "event_simulator.compare_des_bound is missing"
    return function(*args, **kwargs)


def test_compare_des_bound_reports_bounded_gap_and_efficiency():
    comparison = compare_des_bound(actual_time=4.0, des_bound=3.0)

    assert comparison.actual_time == 4.0
    assert comparison.des_bound == 3.0
    assert comparison.optimization_gap == pytest.approx(0.25)
    assert comparison.hardware_efficiency == pytest.approx(0.75)
    assert comparison.optimization_gap + comparison.hardware_efficiency == pytest.approx(1.0)


def test_compare_des_bound_accepts_a_tight_positive_bound():
    comparison = compare_des_bound(actual_time=2.5, des_bound=2.5)

    assert comparison.optimization_gap == 0.0
    assert comparison.hardware_efficiency == 1.0


def test_bound_comparison_direct_construction_computes_validated_metrics():
    comparison_type = getattr(event_simulator, "BoundComparison", None)
    assert comparison_type is not None, "event_simulator.BoundComparison is missing"

    comparison = comparison_type(actual_time=4.0, des_bound=3.0)

    assert comparison.optimization_gap == pytest.approx(0.25)
    assert comparison.hardware_efficiency == pytest.approx(0.75)


def test_bound_comparison_direct_construction_rejects_bound_violation():
    comparison_type = getattr(event_simulator, "BoundComparison", None)
    assert comparison_type is not None, "event_simulator.BoundComparison is missing"

    with pytest.raises(ValueError, match="must not exceed actual_time"):
        comparison_type(actual_time=3.0, des_bound=3.1)


@pytest.mark.parametrize(
    ("actual_time", "des_bound"),
    [
        (0.0, 0.5),
        (-1.0, 0.5),
        (1.0, 0.0),
        (1.0, -0.5),
        (inf, 0.5),
        (1.0, inf),
        (nan, 0.5),
        (1.0, nan),
        (True, 0.5),
        (1.0, False),
        ("1.0", 0.5),
        (1.0, object()),
    ],
)
def test_compare_des_bound_rejects_non_positive_or_non_finite_inputs(
    actual_time, des_bound
):
    with pytest.raises(ValueError, match="finite and positive"):
        compare_des_bound(actual_time=actual_time, des_bound=des_bound)


def test_compare_des_bound_rejects_bound_violation():
    with pytest.raises(ValueError, match="must not exceed actual_time"):
        compare_des_bound(actual_time=3.0, des_bound=3.1)
