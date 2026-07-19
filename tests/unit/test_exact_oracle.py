from dataclasses import FrozenInstanceError
from itertools import permutations

import pytest

import event_simulator
from exact_time_grid_reference import exact_time_grid_makespan


Event = event_simulator.Event
EventGraph = event_simulator.EventGraph
ResourceConfig = event_simulator.ResourceConfig
ResourceLifetime = event_simulator.ResourceLifetime
ExactScheduleResult = getattr(event_simulator, "ExactScheduleResult", None)
IncompleteExactSearchError = getattr(
    event_simulator, "IncompleteExactSearchError", RuntimeError
)
ScheduleEntry = getattr(event_simulator, "ScheduleEntry", None)
solve_exact_schedule = getattr(event_simulator, "solve_exact_schedule", None)


def _event(
    event_id: str,
    duration: float,
    *,
    dependencies: tuple[str, ...] = (),
    global_demand: dict[str, int] | None = None,
    per_sm_demand: dict[str, int] | None = None,
    eligible_sms: frozenset[int] | None = None,
    lifetime_id: str | None = None,
) -> Event:
    return Event(
        event_id=event_id,
        event_type="MMA",
        kernel_id="kernel",
        stream_id="stream",
        duration=duration,
        dependencies=dependencies,
        global_demand=global_demand or {},
        per_sm_demand=per_sm_demand or {},
        eligible_sms=eligible_sms,
        lifetime_id=lifetime_id,
    )


def _config(
    global_capacities: dict[str, int] | None = None,
    *,
    sm_count: int = 1,
    per_sm_capacities: dict[str, int] | None = None,
) -> ResourceConfig:
    return ResourceConfig(
        global_capacities=global_capacities or {},
        sm_count=sm_count,
        per_sm_capacities=per_sm_capacities or {},
    )


def _by_id(result):
    return {entry.event_id: entry for entry in result.entries}


def test_exact_oracle_public_api_is_available():
    assert ExactScheduleResult is not None
    assert IncompleteExactSearchError is not RuntimeError
    assert ScheduleEntry is not None
    assert solve_exact_schedule is not None


def test_exact_result_uses_one_immutable_schedule_entry_type():
    graph = EventGraph((_event("b", 2.0), _event("a", 4.0)))

    result = solve_exact_schedule(graph, _config())

    assert isinstance(result, ExactScheduleResult)
    assert result.makespan == 4.0
    assert tuple(entry.event_id for entry in result.entries) == ("a", "b")
    assert all(isinstance(entry, ScheduleEntry) for entry in result.entries)
    assert all(entry.sm_id is None for entry in result.entries)
    with pytest.raises(FrozenInstanceError):
        result.makespan = 5.0
    with pytest.raises(FrozenInstanceError):
        result.entries[0].start_time = 1.0


def test_independent_events_start_together_with_tied_start_time():
    graph = EventGraph((_event("long", 4.0), _event("short", 2.0)))

    result = solve_exact_schedule(graph, _config())
    entries = _by_id(result)

    assert entries["long"].start_time == 0.0
    assert entries["short"].start_time == 0.0
    assert result.makespan == 4.0


def test_exclusive_global_resource_serializes_conflicting_events():
    graph = EventGraph(
        (
            _event("a", 4.0, global_demand={"tensor": 1}),
            _event("b", 2.0, global_demand={"tensor": 1}),
        )
    )
    config = _config({"tensor": 1})

    result = solve_exact_schedule(graph, config)
    entries = _by_id(result)

    assert result.makespan == 6.0
    assert entries["a"].end_time <= entries["b"].start_time
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_simultaneous_multi_resource_demand_is_atomic():
    graph = EventGraph(
        (
            _event(
                "both",
                3.0,
                global_demand={"memory": 1, "tensor": 1},
            ),
            _event("memory", 2.0, global_demand={"memory": 1}),
            _event("tensor", 2.0, global_demand={"tensor": 1}),
        )
    )
    config = _config({"memory": 1, "tensor": 1})

    result = solve_exact_schedule(graph, config)

    assert result.makespan == 5.0
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_exact_oracle_finds_the_short_first_precedence_resource_optimum():
    graph = EventGraph(
        (
            _event("long", 10.0, global_demand={"a": 1}),
            _event("short", 1.0, global_demand={"a": 1}),
            _event(
                "tail",
                10.0,
                dependencies=("short",),
                global_demand={"b": 1},
            ),
        )
    )
    config = _config({"a": 1, "b": 1})

    result = solve_exact_schedule(graph, config)
    entries = _by_id(result)

    assert entries["short"].start_time == 0.0
    assert entries["tail"].start_time == 1.0
    assert entries["long"].start_time == 1.0
    assert result.makespan == 11.0
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_zero_duration_event_occupies_no_resource_time():
    graph = EventGraph(
        (
            _event("zero", 0.0, global_demand={"tensor": 1}),
            _event("work", 3.0, global_demand={"tensor": 1}),
        )
    )
    config = _config({"tensor": 1})

    result = solve_exact_schedule(graph, config)
    entries = _by_id(result)

    assert entries["zero"].start_time == entries["zero"].end_time == 0.0
    assert entries["work"].start_time == 0.0
    assert result.makespan == 3.0
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_one_sm_per_sm_resources_are_exact_anonymous_resources():
    graph = EventGraph(
        (
            _event("a", 1.0, per_sm_demand={"registers": 2}),
            _event("b", 1.0, per_sm_demand={"registers": 2}),
        )
    )
    config = _config(sm_count=1, per_sm_capacities={"registers": 3})

    result = solve_exact_schedule(graph, config)

    assert result.makespan == 2.0
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_one_sm_combines_global_and_per_sm_demands_atomically():
    graph = EventGraph(
        (
            _event(
                "both",
                1.0,
                global_demand={"launch": 1},
                per_sm_demand={"registers": 2},
            ),
            _event("global", 1.0, global_demand={"launch": 1}),
            _event("local", 1.0, per_sm_demand={"registers": 2}),
        )
    )
    config = _config(
        {"launch": 1},
        sm_count=1,
        per_sm_capacities={"registers": 2},
    )

    result = solve_exact_schedule(graph, config)

    assert result.makespan == 2.0
    assert result.makespan == exact_time_grid_makespan(graph, config)


def test_multiple_sms_accept_global_only_work():
    graph = EventGraph(
        (
            _event("a", 2.0, global_demand={"launch": 1}),
            _event("b", 1.0, global_demand={"launch": 1}),
        )
    )

    result = solve_exact_schedule(
        graph,
        _config({"launch": 1}, sm_count=4, per_sm_capacities={"slots": 2}),
    )

    assert result.makespan == 3.0


def test_multiple_sms_accept_explicit_zero_per_sm_demand():
    graph = EventGraph(
        (_event("event", 2.0, per_sm_demand={"slots": 0}),)
    )

    result = solve_exact_schedule(
        graph,
        _config(sm_count=2, per_sm_capacities={"slots": 1}),
    )

    assert result.makespan == 2.0


def test_multiple_sms_reject_nonzero_per_sm_demand_without_placement():
    graph = EventGraph(
        (_event("event", 1.0, per_sm_demand={"registers": 2}),)
    )
    config = _config(sm_count=2, per_sm_capacities={"registers": 3})

    with pytest.raises(ValueError, match="one SM.*per-SM demand"):
        solve_exact_schedule(graph, config)


def test_exact_oracle_is_invariant_to_event_input_permutation():
    events = (
        _event("long", 4.0, global_demand={"tensor": 1}),
        _event("short", 2.0, global_demand={"tensor": 1}),
        _event("tail", 3.0, dependencies=("short",)),
    )
    config = _config({"tensor": 1})
    observed = {
        solve_exact_schedule(EventGraph(order), config).makespan
        for order in permutations(events)
    }

    assert observed == {6.0}


def test_search_budget_exhaustion_returns_no_exact_result():
    graph = EventGraph((_event("a", 1.0), _event("b", 1.0)))

    with pytest.raises(IncompleteExactSearchError, match="incomplete"):
        solve_exact_schedule(graph, _config(), max_permutations=1)
    assert solve_exact_schedule(
        graph, _config(), max_permutations=2
    ).makespan == 1.0


@pytest.mark.parametrize("budget", [0, -1, 1.5, True])
def test_search_budget_must_be_a_positive_integer(budget):
    graph = EventGraph((_event("event", 1.0),))

    with pytest.raises(ValueError, match="max_permutations"):
        solve_exact_schedule(graph, _config(), max_permutations=budget)


def test_exact_oracle_rejects_empty_graph():
    with pytest.raises(ValueError, match="non-empty"):
        solve_exact_schedule(EventGraph(()), _config())


def test_exact_oracle_rejects_resource_lifetimes():
    lifetime = ResourceLifetime(
        lifetime_id="worker",
        acquire_event_id="acquire",
        release_event_id="release",
        per_sm_reservation={"slots": 1},
    )
    graph = EventGraph(
        (
            _event("acquire", 0.0, lifetime_id="worker"),
            _event(
                "release",
                0.0,
                dependencies=("acquire",),
                lifetime_id="worker",
            ),
        ),
        lifetimes=(lifetime,),
    )
    config = _config(sm_count=1, per_sm_capacities={"slots": 1})

    with pytest.raises(ValueError, match="resource lifetimes"):
        solve_exact_schedule(graph, config)


def test_exact_oracle_rejects_eligible_sm_affinity():
    graph = EventGraph((_event("event", 1.0, eligible_sms=frozenset({0})),))

    with pytest.raises(ValueError, match="eligible-SM affinity"):
        solve_exact_schedule(graph, _config())


@pytest.mark.parametrize(
    ("events", "config"),
    [
        (
            (
                _event("a", 2.0, global_demand={"r": 1}),
                _event("b", 1.0, global_demand={"r": 1}),
            ),
            _config({"r": 1}),
        ),
        (
            (
                _event("a", 2.0),
                _event("b", 1.0, dependencies=("a",)),
                _event("c", 2.0, dependencies=("a",)),
            ),
            _config(),
        ),
        (
            (
                _event("a", 0.0, global_demand={"r": 1}),
                _event("b", 2.0, global_demand={"r": 1}),
                _event("c", 1.0, dependencies=("a",)),
            ),
            _config({"r": 1}),
        ),
    ],
)
def test_serial_sgs_matches_independent_time_grid_enumeration(events, config):
    graph = EventGraph(events)

    actual = solve_exact_schedule(graph, config).makespan
    expected = exact_time_grid_makespan(graph, config)

    assert actual == expected
