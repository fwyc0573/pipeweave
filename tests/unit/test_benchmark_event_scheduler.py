import importlib

import pytest


EXPECTED_FIELDS = (
    "event_count",
    "edge_count",
    "resource_count",
    "graph_build_seconds",
    "schedule_seconds",
    "report_seconds",
    "ready_queue_operations",
    "blocked_ready_rechecks",
    "placement_checks",
    "lifetime_checks",
    "old_runtime_seconds",
    "new_runtime_seconds",
    "speedup",
    "makespan",
    "exact_optimum",
    "optimality_gap",
    "feasibility_violation_count",
    "determinism_mismatch_count",
)


def _benchmark_module():
    return importlib.import_module(
        "tests.performance.benchmark_event_scheduler"
    )


def test_historical_cases_match_reviewed_sizes_and_runtimes():
    benchmark = _benchmark_module()

    actual = {
        3 * case.cta_count + 3: case.old_runtime_seconds
        for case in benchmark.HISTORICAL_CASES
    }

    assert actual == {
        387: 0.014082,
        771: 0.034505,
        1_539: 0.090736,
        3_075: 0.280886,
        6_147: 1.038378,
        58_467: 115.882818766,
    }


def test_benchmark_graph_matches_historical_shape_and_resource_contract():
    benchmark = _benchmark_module()

    benchmark_input = benchmark.build_benchmark_input(
        cta_count=128,
        sm_count=132,
    )

    assert len(benchmark_input.graph.events) == 387
    assert sum(
        len(event.dependencies) for event in benchmark_input.graph.events
    ) == 514
    assert len(benchmark_input.config.global_capacities) == 3
    assert len(benchmark_input.config.per_sm_capacities) == 2
    assert benchmark_input.config.sm_count == 132


def test_small_case_reports_exact_gap_and_integrity_metrics():
    benchmark = _benchmark_module()

    result = benchmark.run_benchmark_case(
        benchmark.BenchmarkCase(
            cta_count=1,
            sm_count=1,
            old_runtime_seconds=None,
            run_exact=True,
        )
    )

    assert benchmark.FIELD_NAMES == EXPECTED_FIELDS
    assert tuple(result.to_row()) == EXPECTED_FIELDS
    assert result.event_count == 6
    assert result.edge_count == 6
    assert result.resource_count == 5
    assert result.makespan == pytest.approx(3.5)
    assert result.exact_optimum == pytest.approx(3.5)
    assert result.optimality_gap == pytest.approx(0.0)
    assert result.feasibility_violation_count == 0
    assert result.determinism_mismatch_count == 0
    assert result.lifetime_checks == 0
    assert result.new_runtime_seconds == pytest.approx(
        result.graph_build_seconds
        + result.schedule_seconds
        + result.report_seconds
    )


def test_benchmark_csv_uses_lf_line_endings(monkeypatch, capsys):
    benchmark = _benchmark_module()
    monkeypatch.setattr(
        benchmark,
        "DEFAULT_CASES",
        (benchmark.EXACT_CASE,),
    )

    benchmark.main()

    output = capsys.readouterr().out
    assert output.count("\n") == 2
    assert "\r" not in output


@pytest.mark.parametrize("cta_count", [True, 0, -1, 1.5])
def test_benchmark_graph_rejects_invalid_cta_count(cta_count):
    benchmark = _benchmark_module()

    with pytest.raises(ValueError, match="cta_count must be a positive integer"):
        benchmark.build_benchmark_input(
            cta_count=cta_count,
            sm_count=132,
        )


@pytest.mark.parametrize("sm_count", [True, 0, -1, 1.5])
def test_benchmark_graph_rejects_invalid_sm_count(sm_count):
    benchmark = _benchmark_module()

    with pytest.raises(ValueError, match="sm_count must be a positive integer"):
        benchmark.build_benchmark_input(
            cta_count=1,
            sm_count=sm_count,
        )
