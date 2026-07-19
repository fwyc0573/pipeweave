"""Order-invariant analytical lower bounds for normalized Event graphs."""

from __future__ import annotations

from dataclasses import dataclass
import heapq
from types import MappingProxyType
from typing import Mapping

from .events import EventGraph
from .resources import ResourceConfig


@dataclass(frozen=True)
class SafeBound:
    """A proven lower bound with immutable term and relaxation evidence."""

    bound: float
    dependency_critical_path: float
    global_resource_terms: Mapping[str, float]
    aggregate_per_sm_terms: Mapping[str, float]
    relaxations: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "global_resource_terms",
            MappingProxyType(dict(sorted(self.global_resource_terms.items()))),
        )
        object.__setattr__(
            self,
            "aggregate_per_sm_terms",
            MappingProxyType(dict(sorted(self.aggregate_per_sm_terms.items()))),
        )
        object.__setattr__(self, "relaxations", tuple(self.relaxations))


class SafeBoundEvaluator:
    """Evaluate critical-path and renewable-resource conservation bounds."""

    def evaluate(
        self, graph: EventGraph, config: ResourceConfig
    ) -> SafeBound:
        if not graph.events:
            raise ValueError("safe bound requires a non-empty EventGraph")
        config.validate_graph(graph)

        critical_path, _ = dependency_critical_path(graph)
        lifetime_by_id = {
            lifetime.lifetime_id: lifetime for lifetime in graph.lifetimes
        }
        transient_per_sm_demand = {
            event.event_id: (
                event.per_sm_demand
                if event.lifetime_id is None
                else lifetime_by_id[
                    event.lifetime_id
                ].transient_per_sm_demand(event.per_sm_demand)
            )
            for event in graph.events
        }
        global_terms = {
            resource: sum(
                float(event.duration) * event.global_demand.get(resource, 0)
                for event in graph.events
            )
            / capacity
            for resource, capacity in config.global_capacities.items()
        }
        per_sm_terms = {
            resource: sum(
                float(event.duration)
                * transient_per_sm_demand[event.event_id].get(resource, 0)
                for event in graph.events
            )
            / (config.sm_count * capacity)
            for resource, capacity in config.per_sm_capacities.items()
        }

        relaxations = []
        if any(event.eligible_sms is not None for event in graph.events) or any(
            lifetime.eligible_sms is not None for lifetime in graph.lifetimes
        ):
            relaxations.append("eligible_sm_affinity")
        if graph.lifetimes:
            relaxations.append("resource_lifetime_reservations")

        bound = max(
            (
                critical_path,
                *global_terms.values(),
                *per_sm_terms.values(),
            )
        )
        return SafeBound(
            bound=bound,
            dependency_critical_path=critical_path,
            global_resource_terms=global_terms,
            aggregate_per_sm_terms=per_sm_terms,
            relaxations=tuple(relaxations),
        )


def dependency_critical_path(
    graph: EventGraph,
) -> tuple[float, tuple[str, ...]]:
    """Return the deterministic dependency-only longest path and witness."""

    if not graph.events:
        return 0.0, ()

    indegrees = dict(graph.indegrees)
    ready = [
        event.event_id
        for event in graph.events
        if indegrees[event.event_id] == 0
    ]
    heapq.heapify(ready)
    completion: dict[str, float] = {}
    predecessor: dict[str, str | None] = {}
    while ready:
        event_id = heapq.heappop(ready)
        event = graph.by_id[event_id]
        if event.dependencies:
            predecessor_end = max(
                completion[dependency]
                for dependency in event.dependencies
            )
            predecessor_id = min(
                dependency
                for dependency in event.dependencies
                if completion[dependency] == predecessor_end
            )
        else:
            predecessor_end = 0.0
            predecessor_id = None
        completion[event_id] = float(event.duration) + predecessor_end
        predecessor[event_id] = predecessor_id
        for successor in graph.successors[event_id]:
            indegrees[successor] -= 1
            if indegrees[successor] == 0:
                heapq.heappush(ready, successor)

    end_id = min(
        completion,
        key=lambda event_id: (-completion[event_id], event_id),
    )
    path = []
    current_id: str | None = end_id
    while current_id is not None:
        path.append(current_id)
        current_id = predecessor[current_id]
    path.reverse()
    return completion[end_id], tuple(path)
