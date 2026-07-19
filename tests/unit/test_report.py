import json
from types import MappingProxyType

import pytest

from event_simulator import (
    Event,
    EventGraph,
    ResourceConfig,
    ResourceLifetime,
    SafeBoundEvaluator,
    build_report,
    schedule,
    solve_exact_schedule,
)


def _event(
    event_id,
    duration,
    *,
    event_type="MMA",
    dependencies=(),
    global_demand=None,
    per_sm_demand=None,
    eligible_sms=None,
    lifetime_id=None,
    kernel_id="kernel",
    stream_id="stream",
    cta_id=None,
    bytes=0,
    instruction_count=0,
):
    return Event(
        event_id=event_id,
        event_type=event_type,
        kernel_id=kernel_id,
        stream_id=stream_id,
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
        cta_id=cta_id,
        bytes=bytes,
        instruction_count=instruction_count,
    )


def _config(*, global_capacities=None, sm_count=1, per_sm_capacities=None):
    return ResourceConfig(
        global_capacities=global_capacities or {},
        sm_count=sm_count,
        per_sm_capacities=per_sm_capacities or {},
    )


def test_report_separates_dependency_exact_bound_and_feasible_values():
    graph = EventGraph(
        (
            _event("a", 3.0, global_demand={"engine": 1}),
            _event("b", 2.0, global_demand={"engine": 1}),
        )
    )
    config = _config(global_capacities={"engine": 1})
    result = schedule(graph, config)
    exact = solve_exact_schedule(graph, config)
    safe_bound = SafeBoundEvaluator().evaluate(graph, config)

    report = build_report(
        result,
        exact_result=exact,
        safe_bound=safe_bound,
    )

    assert report.dependency_critical_path == 3.0
    assert report.dependency_critical_path_event_ids == ("a",)
    assert report.exact_optimum == 5.0
    assert report.safe_bound_value == 5.0
    assert report.feasible_makespan == 5.0
    assert not hasattr(report, "critical_path")
    assert not hasattr(report, "makespan")


def test_dependency_critical_path_ties_use_canonical_event_ids():
    graph = EventGraph(
        (
            _event("b", 2.0),
            _event("a", 2.0),
            _event("c", 1.0, dependencies=("b", "a")),
            _event("d", 3.0),
        )
    )

    report = build_report(schedule(graph, _config()))

    assert report.dependency_critical_path == 3.0
    assert report.dependency_critical_path_event_ids == ("a", "c")


def test_report_uses_demand_weighted_multi_resource_busy_time():
    graph = EventGraph(
        (
            _event(
                "multi",
                2.0,
                global_demand={"memory": 3, "link": 1},
                per_sm_demand={"alu": 2},
            ),
        )
    )
    result = schedule(
        graph,
        _config(
            global_capacities={"memory": 3, "link": 1},
            per_sm_capacities={"alu": 2},
        ),
    )

    report = build_report(result)

    assert report.resource_busy_time == {
        "alu": 4.0,
        "link": 2.0,
        "memory": 6.0,
    }


def test_lifetime_busy_time_counts_reservation_without_member_double_count():
    lifetime = ResourceLifetime(
        lifetime_id="cta",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slot": 2},
    )
    graph = EventGraph(
        (
            _event(
                "acquire",
                1.0,
                lifetime_id="cta",
                kernel_id="kernel-a",
            ),
            _event(
                "member",
                2.0,
                dependencies=("acquire",),
                per_sm_demand={"slot": 2, "alu": 1},
                lifetime_id="cta",
                kernel_id="kernel-a",
            ),
            _event(
                "release",
                1.0,
                dependencies=("member",),
                lifetime_id="cta",
                kernel_id="kernel-a",
            ),
        ),
        (lifetime,),
    )
    result = schedule(
        graph,
        _config(
            per_sm_capacities={"slot": 2, "alu": 1},
        ),
    )

    report = build_report(result)

    assert report.resource_busy_time["slot"] == 8.0
    assert report.resource_busy_time["alu"] == 2.0


def test_report_kernel_duration_uses_minimum_start_and_maximum_end():
    graph = EventGraph(
        (
            _event(
                "a",
                2.0,
                global_demand={"a_engine": 1},
                kernel_id="shared",
            ),
            _event(
                "b",
                4.0,
                global_demand={"b_engine": 1},
                kernel_id="shared",
            ),
            _event(
                "c",
                1.0,
                dependencies=("a",),
                kernel_id="other",
            ),
        )
    )
    result = schedule(
        graph,
        _config(global_capacities={"a_engine": 1, "b_engine": 1}),
    )

    report = build_report(result)

    assert report.kernel_durations == {"other": 1.0, "shared": 4.0}


def test_timeline_combines_immutable_event_spec_and_schedule_entry():
    graph = EventGraph(
        (
            _event(
                "work",
                2.0,
                event_type="GlobalLoad",
                dependencies=(),
                global_demand={"memory": 2},
                per_sm_demand={"slot": 1},
                eligible_sms=frozenset({1}),
                kernel_id="kernel-0",
                stream_id="stream-0",
                cta_id="cta-0",
                bytes=128,
                instruction_count=16,
            ),
        )
    )
    result = schedule(
        graph,
        _config(
            global_capacities={"memory": 2},
            sm_count=2,
            per_sm_capacities={"slot": 1},
        ),
    )

    report = build_report(result)
    item = report.timeline[0]

    assert item["event_id"] == "work"
    assert item["event_type"] == "GlobalLoad"
    assert item["kernel_id"] == "kernel-0"
    assert item["stream_id"] == "stream-0"
    assert item["cta_id"] == "cta-0"
    assert item["bytes"] == 128
    assert item["instruction_count"] == 16
    assert item["dependencies"] == ()
    assert item["global_demand"] == {"memory": 2}
    assert item["per_sm_demand"] == {"slot": 1}
    assert item["eligible_sms"] == (1,)
    assert item["lifetime_id"] is None
    assert item["duration"] == 2.0
    assert item["start_time"] == 0.0
    assert item["end_time"] == 2.0
    assert item["sm_id"] == 1

    assert isinstance(item, MappingProxyType)
    with pytest.raises(TypeError):
        item["event_id"] = "changed"
    with pytest.raises(TypeError):
        item["global_demand"]["memory"] = 0
    with pytest.raises(TypeError):
        item["per_sm_demand"]["slot"] = 0


def test_report_mappings_are_immutable_and_to_dict_is_json_serializable():
    graph = EventGraph((_event("work", 1.0),))
    report = build_report(schedule(graph, _config()))

    assert isinstance(report.kernel_durations, MappingProxyType)
    assert isinstance(report.resource_busy_time, MappingProxyType)
    with pytest.raises(TypeError):
        report.kernel_durations["kernel"] = 0.0

    serialized = json.dumps(report.to_dict(), sort_keys=True)
    payload = json.loads(serialized)

    assert payload["feasible_makespan"] == 1.0
    assert payload["dependency_critical_path"] == 1.0
    assert payload["exact_optimum"] is None
    assert payload["safe_bound_value"] is None
    assert payload["timeline"][0]["event_id"] == "work"


def test_empty_schedule_report_has_explicit_zero_and_absent_optional_evidence():
    report = build_report(schedule(EventGraph(()), _config(sm_count=2)))

    assert report.feasible_makespan == 0.0
    assert report.dependency_critical_path == 0.0
    assert report.dependency_critical_path_event_ids == ()
    assert report.exact_optimum is None
    assert report.safe_bound_value is None
    assert report.kernel_durations == {}
    assert report.resource_busy_time == {}
    assert report.timeline == ()
