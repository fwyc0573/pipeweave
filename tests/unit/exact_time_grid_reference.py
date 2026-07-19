"""Independent integer-time oracle for tiny exact-schedule test cases."""

from itertools import product

from event_simulator import EventGraph, ResourceConfig


def exact_time_grid_makespan(
    graph: EventGraph, config: ResourceConfig
) -> float:
    """Enumerate bounded integer start assignments without using serial SGS."""

    if not graph.events:
        raise ValueError("time-grid reference requires a non-empty EventGraph")
    if graph.lifetimes:
        raise ValueError("time-grid reference does not support resource lifetimes")
    if any(event.eligible_sms is not None for event in graph.events):
        raise ValueError("time-grid reference does not support eligible-SM affinity")
    if config.sm_count > 1 and any(
        any(demand > 0 for demand in event.per_sm_demand.values())
        for event in graph.events
    ):
        raise ValueError(
            "time-grid reference requires one SM for nonzero per-SM demand"
        )

    config.validate_graph(graph)
    durations = {}
    for event in graph.events:
        duration = float(event.duration)
        if not duration.is_integer():
            raise ValueError("time-grid reference requires integer durations")
        durations[event.event_id] = int(duration)

    capacities = dict(config.global_capacities)
    if config.sm_count == 1:
        capacities.update(config.per_sm_capacities)

    horizon = sum(durations.values())
    event_ids = tuple(event.event_id for event in graph.events)
    best: int | None = None
    for start_values in product(range(horizon + 1), repeat=len(event_ids)):
        starts = dict(zip(event_ids, start_values, strict=True))
        ends = {
            event_id: starts[event_id] + durations[event_id]
            for event_id in event_ids
        }
        makespan = max(ends.values())
        if makespan > horizon or (best is not None and makespan >= best):
            continue
        if any(
            ends[dependency] > starts[event.event_id]
            for event in graph.events
            for dependency in event.dependencies
        ):
            continue
        if not _resource_feasible(graph, capacities, starts, ends, horizon):
            continue
        best = makespan

    if best is None:
        raise AssertionError("validated tiny instance has no feasible assignment")
    return float(best)


def _resource_feasible(
    graph: EventGraph,
    capacities: dict[str, int],
    starts: dict[str, int],
    ends: dict[str, int],
    horizon: int,
) -> bool:
    for time in range(horizon):
        active = tuple(
            event
            for event in graph.events
            if starts[event.event_id] <= time < ends[event.event_id]
        )
        for resource, capacity in capacities.items():
            demand = sum(
                event.global_demand.get(resource, 0)
                + event.per_sm_demand.get(resource, 0)
                for event in active
            )
            if demand > capacity:
                return False
    return True
