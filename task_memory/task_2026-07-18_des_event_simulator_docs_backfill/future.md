# DES Event Simulator Documentation Backfill Future Work

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Replaced the empty shell with prioritized implementation, validation, and documentation follow-up. |
| 2026-07-18 | Created the future-work boundary document. |

## Outside the Current Session

All items below require separate tasks and, where behavior changes, explicit user approval. They are not part of the current documentation-only plan.

### Priority 0 — Restore Validation Correctness

1. Fix `tests/validation/validate_gemm_v2.py::classical_roofline` to use the derived chip-wide BF16 rate; add H100 numeric unit tests.
2. Remove the broad `except Exception`/silent skip in `des_predict`; validate input schema explicitly and fail on unexpected simulation errors.
3. Pass dataset `tile_K` into `lower_gemm_v2` and add a RED/GREEN test proving different valid tile-K regimes can change the intended L2 reuse behavior.
4. Reconcile `lower_gemm_v2`'s tile-K contract with the current B-column effective-traffic model rather than layering a temporary correction factor.

### Priority 1 — Make Full Acceptance Reproducible

1. Replace repeated full ready-event scans with a deterministic dependency-count/ready-queue scheduler while preserving stream/resource predecessor semantics.
2. Add scheduler performance tests across event counts and define an explicit runtime threshold.
3. Resolve the L2 coefficient/lane conservation ambiguity (I-011) and test aggregate bandwidth.
4. Decide whether GEMM v2's public contract is explicit L2 hit/miss events or chip-level effective DRAM bytes; update code, docstrings, design rules, and tests consistently.
5. Decide how partial-tile structural inefficiency is represented; current classification uses useful work only.
6. Rerun all 200 Large + 100 Medium + 100 Small H100 rows with zero unexpected skips; record per-row and aggregate metrics.

### Priority 2 — Complete FlashAttention Evidence

1. Finish the 21-configuration H800 benchmark matrix; the tracked CSV currently contains only two rows.
2. Add a fail-fast DES-vs-measurement validator with bound/tightness metrics and full predicted/actual evidence.
3. Add realistic CTA residency tokens, shared-memory/register constraints, phase overlap, and mechanism-counter validation before declaring research-roadmap Phase 3 complete.
4. Validate FA2/FA3 scheduler reuse, GQA/head grouping, causal work, and decode-like shapes against kernel traces.

### Priority 3 — Continue the Original Research Roadmap

- Implement typed hardware/workload frontend adapters without MLP/RF inference.
- Perform independent primitive hardware characterization and version its environment metadata.
- Add streams, synchronization, copy engines, NCCL/topology, compute/communication overlap, request lifecycle, decode, PP, and CPU launch events.
- Run the full held-out operator/E2E scientific evaluation.

### Documentation Cleanup

1. Add a Modification History to `docs/des_design_rules.md` in place.
2. Update `docs/event_simulator_design.md` and `README.md` after the above design/status decisions are approved; preserve the Phase 0 historical record while adding a clearly dated current-state section.
3. Keep runtime `.omc` records as provenance only; maintain future task state under tracked `task_memory/` artifacts.
