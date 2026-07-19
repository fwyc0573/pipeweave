"""Exhaustively cross-check the exact oracle and SafeBound on tiny cases."""

from __future__ import annotations

from hashlib import sha256
from itertools import permutations, product
import json
from pathlib import Path
from time import perf_counter

from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    SafeBoundEvaluator,
    solve_exact_schedule,
)
from tests.unit.exact_time_grid_reference import exact_time_grid_makespan


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / (
    "task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/"
    "safe_bound_oracle_cases.json"
)
EVENT_IDS = ("a", "b", "c")
DURATION_VALUES = (0.0, 1.0, 2.0)
CAPACITIES = (1, 2)
DEPENDENCY_SHAPES = {
    "independent": ((), (), ()),
    "chain": ((), ("a",), ("b",)),
    "fork": ((), ("a",), ("a",)),
    "join": ((), (), ("a", "b")),
    "chain_plus_independent": ((), ("a",), ()),
}
CASE_FIELDS = (
    "case_id",
    "capacity",
    "dependency_shape",
    "duration_a",
    "duration_b",
    "duration_c",
    "demand_a",
    "demand_b",
    "demand_c",
    "time_grid_optimum",
    "exact_oracle_optimum",
    "absolute_delta",
    "safe_bound",
    "exact_minus_bound",
    "relative_exact_minus_bound",
)


def main() -> None:
    started = perf_counter()
    cases = []
    bounds = {}
    groups = {}
    exact_mismatches = 0
    safety_violations = 0
    permutation_mismatches = 0
    conservation_failures = 0
    permutations_checked = 0
    maximum_absolute_delta = 0.0
    minimum_exact_minus_bound: float | None = None

    for capacity in CAPACITIES:
        config = ResourceConfig({"resource": capacity}, 1, {})
        for durations in product(DURATION_VALUES, repeat=len(EVENT_IDS)):
            for demands in product(range(capacity + 1), repeat=len(EVENT_IDS)):
                for shape_name, dependencies in DEPENDENCY_SHAPES.items():
                    events = _events(durations, demands, dependencies)
                    graph = EventGraph(events)
                    time_grid = exact_time_grid_makespan(graph, config)
                    exact = solve_exact_schedule(graph, config).makespan
                    result = SafeBoundEvaluator().evaluate(graph, config)
                    bound = result.bound
                    absolute_delta = abs(exact - time_grid)
                    safety_margin = exact - bound
                    relative_margin = (
                        safety_margin / exact if exact > 0.0 else None
                    )
                    expected_resource_term = sum(
                        duration * demand
                        for duration, demand in zip(
                            durations, demands, strict=True
                        )
                    ) / capacity

                    exact_mismatches += absolute_delta != 0.0
                    safety_violations += safety_margin < 0.0
                    conservation_failures += (
                        result.global_resource_terms["resource"]
                        != expected_resource_term
                    )
                    maximum_absolute_delta = max(
                        maximum_absolute_delta, absolute_delta
                    )
                    minimum_exact_minus_bound = (
                        safety_margin
                        if minimum_exact_minus_bound is None
                        else min(minimum_exact_minus_bound, safety_margin)
                    )

                    signature = _signature(exact, result)
                    for order in permutations(events):
                        permuted_graph = EventGraph(order)
                        permuted_exact = solve_exact_schedule(
                            permuted_graph, config
                        ).makespan
                        permuted_result = SafeBoundEvaluator().evaluate(
                            permuted_graph, config
                        )
                        permutations_checked += 1
                        permutation_mismatches += (
                            _signature(permuted_exact, permuted_result)
                            != signature
                        )

                    case_id = _case_id(
                        capacity, shape_name, durations, demands
                    )
                    case = [
                        case_id,
                        capacity,
                        shape_name,
                        *durations,
                        *demands,
                        time_grid,
                        exact,
                        absolute_delta,
                        bound,
                        safety_margin,
                        relative_margin,
                    ]
                    cases.append(case)
                    bounds[(capacity, durations, demands, shape_name)] = bound
                    _record_group(
                        groups,
                        capacity,
                        shape_name,
                        exact,
                        bound,
                        absolute_delta,
                        safety_margin,
                    )

    monotonicity_checks, monotonicity_failures = _check_monotonicity(bounds)
    failures = {
        "exact_mismatches": exact_mismatches,
        "safety_violations": safety_violations,
        "permutation_mismatches": permutation_mismatches,
        "conservation_failures": conservation_failures,
        "monotonicity_failures": monotonicity_failures,
    }
    if any(failures.values()):
        raise AssertionError(f"proof-layer validation failed: {failures}")

    case_bytes = json.dumps(
        cases, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    summary = {
        "oracle_cases_total": len(cases),
        "oracle_cases_passed": len(cases),
        "exact_mismatches": exact_mismatches,
        "safety_violations": safety_violations,
        "maximum_absolute_delta": maximum_absolute_delta,
        "minimum_exact_minus_bound": minimum_exact_minus_bound,
        "permutations_checked": permutations_checked,
        "permutation_mismatches": permutation_mismatches,
        "conservation_failures": conservation_failures,
        "monotonicity_checks": monotonicity_checks,
        "monotonicity_failures": monotonicity_failures,
        "case_records_sha256": sha256(case_bytes).hexdigest(),
    }
    evidence = {
        "schema_version": 1,
        "domain": {
            "event_ids": EVENT_IDS,
            "duration_values": DURATION_VALUES,
            "capacities": CAPACITIES,
            "demand_values": "every integer from zero through capacity",
            "dependency_shapes": DEPENDENCY_SHAPES,
            "resource_model": "one global renewable integer resource",
            "time_model": "non-preemptive half-open integer-time intervals",
        },
        "summary": summary,
        "groups": [groups[key] for key in sorted(groups)],
        "case_fields": CASE_FIELDS,
        "cases": cases,
    }
    _write_evidence(evidence)

    elapsed = perf_counter() - started
    for key, value in summary.items():
        print(f"{key}={value}")
    print(f"elapsed_seconds={elapsed:.9f}")
    print(f"evidence_path={OUTPUT}")


def _events(durations, demands, dependencies) -> tuple[Event, ...]:
    return tuple(
        Event(
            event_id=event_id,
            event_type="MMA",
            kernel_id="kernel",
            stream_id="stream",
            duration=duration,
            dependencies=event_dependencies,
            global_demand={"resource": demand},
        )
        for event_id, duration, event_dependencies, demand in zip(
            EVENT_IDS, durations, dependencies, demands, strict=True
        )
    )


def _signature(exact, result) -> tuple:
    return (
        exact,
        result.bound,
        result.dependency_critical_path,
        tuple(result.global_resource_terms.items()),
        tuple(result.aggregate_per_sm_terms.items()),
        result.relaxations,
    )


def _case_id(capacity, shape_name, durations, demands) -> str:
    duration_key = "".join(str(int(value)) for value in durations)
    demand_key = "".join(str(value) for value in demands)
    return f"capacity-{capacity}:{shape_name}:d-{duration_key}:q-{demand_key}"


def _record_group(
    groups,
    capacity,
    shape_name,
    exact,
    bound,
    absolute_delta,
    safety_margin,
) -> None:
    key = (capacity, shape_name)
    group = groups.setdefault(
        key,
        {
            "capacity": capacity,
            "dependency_shape": shape_name,
            "cases": 0,
            "minimum_exact_optimum": exact,
            "maximum_exact_optimum": exact,
            "minimum_safe_bound": bound,
            "maximum_safe_bound": bound,
            "maximum_absolute_delta": absolute_delta,
            "minimum_exact_minus_bound": safety_margin,
        },
    )
    group["cases"] += 1
    group["minimum_exact_optimum"] = min(
        group["minimum_exact_optimum"], exact
    )
    group["maximum_exact_optimum"] = max(
        group["maximum_exact_optimum"], exact
    )
    group["minimum_safe_bound"] = min(group["minimum_safe_bound"], bound)
    group["maximum_safe_bound"] = max(group["maximum_safe_bound"], bound)
    group["maximum_absolute_delta"] = max(
        group["maximum_absolute_delta"], absolute_delta
    )
    group["minimum_exact_minus_bound"] = min(
        group["minimum_exact_minus_bound"], safety_margin
    )


def _check_monotonicity(bounds) -> tuple[int, int]:
    checks = 0
    failures = 0
    for (capacity, durations, demands, shape_name), bound in bounds.items():
        for index in range(len(EVENT_IDS)):
            if durations[index] < max(DURATION_VALUES):
                increased = list(durations)
                increased[index] += 1.0
                checks += 1
                failures += (
                    bounds[
                        (capacity, tuple(increased), demands, shape_name)
                    ]
                    < bound
                )
            if demands[index] < capacity:
                increased = list(demands)
                increased[index] += 1
                checks += 1
                failures += (
                    bounds[
                        (capacity, durations, tuple(increased), shape_name)
                    ]
                    < bound
                )
    return checks, failures


def _write_evidence(evidence) -> None:
    cases = evidence.pop("cases")
    header = json.dumps(evidence, indent=2, sort_keys=False)
    case_lines = [
        "    " + json.dumps(case, separators=(",", ":"))
        for case in cases
    ]
    content = (
        header[:-2]
        + ",\n  \"cases\": [\n"
        + ",\n".join(case_lines)
        + "\n  ]\n}\n"
    )
    OUTPUT.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
