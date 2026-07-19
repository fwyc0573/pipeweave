"""Order-invariant analytical lower bounds for normalized Event graphs."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
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

        critical_path = _dependency_critical_path(graph)
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
                float(event.duration) * event.per_sm_demand.get(resource, 0)
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


def _dependency_critical_path(graph: EventGraph) -> float:
    indegrees = dict(graph.indegrees)
    ready = deque(
        event.event_id
        for event in graph.events
        if indegrees[event.event_id] == 0
    )
    completion: dict[str, float] = {}
    while ready:
        event_id = ready.popleft()
        event = graph.by_id[event_id]
        completion[event_id] = float(event.duration) + max(
            (completion[dependency] for dependency in event.dependencies),
            default=0.0,
        )
        for successor in graph.successors[event_id]:
            indegrees[successor] -= 1
            if indegrees[successor] == 0:
                ready.append(successor)
    return max(completion.values())
