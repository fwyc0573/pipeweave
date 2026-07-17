# Event-Level Simulator MVP

## Goal

Add an independent, deterministic event-level simulator alongside the existing
PipeWeave analytical-plus-ML predictor. The MVP must make kernel work explicit,
schedule events on modeled resources, and use only supplied primitive duration
calibration. It must not train or invoke the existing MLP/RF models.

## Scope

- Single device and deterministic scheduling.
- Explicit event IR with dependencies and timing.
- Exclusive resource scheduling with fail-fast validation.
- GEMM, RMSNorm, and SiLU-and-Mul lowering.
- JSON-serializable timeline and critical-path report.
- Unit and integration tests under `tests/`.

## Non-goals

- Cycle-accurate CUDA simulation.
- Multi-stream overlap, NCCL topology, multi-node communication, or PP bubble modeling.
- Replacement or modification of the existing `aggregator.py` path.
- New third-party dependencies.

## File plan

1. `event_simulator/events.py`: validated event and calibration data structures.
2. `event_simulator/resources.py`: resource configuration and calibrated primitive costs.
3. `event_simulator/scheduler.py`: deterministic dependency/resource scheduler.
4. `event_simulator/operators.py`: supported operator-to-event lowerings.
5. `event_simulator/report.py`: timeline and summary serialization.
6. `event_simulator/__init__.py`: public API.
7. `tests/unit/`: focused validation of the event IR and scheduler.
8. `tests/integration/`: operator lowering plus end-to-end simulation.
9. `README.md`: usage, boundary, and limitations.

## TDD and verification

1. Add tests first and run `pytest -q tests` to observe RED.
2. Implement the smallest event IR and scheduler that satisfies unit tests.
3. Add lowering and report tests, then implement those modules.
4. Run `pytest -q`, `python -m compileall event_simulator tests`, and a JSON smoke example.
5. Review the complete `des` diff from an independent reviewer and resolve all
   important findings before final verification.

## Acceptance criteria

- Dependencies and same-stream events execute in non-decreasing time order.
- Events using one exclusive resource never overlap.
- Unknown resources, duplicate IDs, cycles, missing dependencies, and negative
  durations raise explicit `ValueError`.
- GEMM produces CTA-wave event chains; RMSNorm includes reduction and barrier;
  SiLU-and-Mul includes load, SFU/FMA compute, and store events.
- Report includes event timeline, per-resource busy time, kernel durations, and
  critical path.
- Existing PipeWeave files and prediction path remain untouched.
