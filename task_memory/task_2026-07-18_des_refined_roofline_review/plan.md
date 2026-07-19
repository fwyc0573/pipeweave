# DES Refined Roofline Review and Remediation Plan

> **For agentic workers:** Use role-specific independent review lanes for code/spec quality and architecture, then use strict TDD for every approved implementation change.

**Goal:** Establish with reproducible evidence whether the current DES satisfies the four Refined Roofline goals, repair confirmed local defects, and replace unsupported claims with precise acceptance boundaries.

**Architecture:** Treat the Event IR, operator lowerings, scheduler, hardware adapter, reports, validators, datasets, and public design documents as one scientific contract. Review first, decide from evidence, then apply the smallest root-cause fixes with RED → GREEN → REFACTOR tests.

**Tech Stack:** Python 3.12, pytest, pandas, numpy, repository hardware JSON specifications, Markdown task artifacts, StepCode Claude independent review.

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Added the user-directed ignored-path closure, branch delivery checkpoint, and next-stage handoff boundary. |
| 2026-07-19 | Added a resume-audit closure phase for fresh verification; no broad architecture work was reopened. |
| 2026-07-18 | Completed Phase 7 after independent approval, fresh `131/131` regression, matched scientific audit, formal reporting, and artifact-integrity preparation. |
| 2026-07-18 | Marked the bounded implementation phase complete and started final independent review and validation. |
| 2026-07-18 | Closed the independent-review and remediation-plan gates; started narrow TDD execution. |
| 2026-07-18 | Added the architecture-BLOCK boundary and file-level narrow TDD remediation sequence. |
| 2026-07-18 | Created the evidence-first review and remediation plan. |

## Global Constraints

- Preserve `DES_bound <= actual_time` for every accepted lower-bound validation case.
- Use `optimization_gap = (actual_time - DES_bound) / actual_time` and `hardware_efficiency = DES_bound / actual_time`.
- Do not introduce learned operator-latency closure, empirical scaling factors, silent skips, or fallback logic.
- Do not claim `10000x`, cross-hardware zero-shot, or tighter-than-roofline behavior without reproducible numeric evidence.
- Make no code behavior change before a failing test demonstrates the confirmed defect.
- Treat the historical `=10.1` path as explicitly ignored and outside active validation/staging; perform no filesystem operation on it.
- Do not use `rm` or `mv`.

## Execution Phases

| Phase | Status | Work | Exit Evidence |
|---|---|---|---|
| 1. Capture requirements and metric decision | Completed | Record the original goals, user-selected bounded metric contract, and first Claude review. | `requirements.md` and `review.md` contain the decision and WATCH conditions. |
| 2. Establish baseline and source map | Completed | Read all DES code, relevant legacy predictor paths, design docs, tests, datasets, reports, and commit history; run the clean baseline. | Exact files/symbols, `74/74` baseline tests, and the current claim-support matrix are recorded. |
| 3. Independent two-lane code/design review | Completed | Run code/spec and architecture review lanes over the same source scope; reconcile with additional Claude reviews. | Architect and adversarial Claude returned BLOCK for broad scientific acceptance; code-reviewer returned REQUEST CHANGES; narrow-scope Claude returned APPROVE with WATCH. |
| 4. Benchmark and scientific claim audit | Completed | Measure refined-vs-classical tightness and DES wall-clock cost; locate or establish the absence of a comparable cycle-accurate and cross-hardware benchmark. | Corrected full-H100 classical statistics, matched category samples, DES violations, CTA mismatch, L2 mismatch, and runtime/scaling evidence are durable. |
| 5. Write exact remediation plan | Completed | Convert confirmed findings into file-specific TDD tasks and obtain Claude design review for material choices. | The narrow sequence below received independent Claude APPROVE with one numeric-validation WATCH; broad architecture remains stopped. |
| 6. Implement confirmed local fixes | Completed | Execute one RED/GREEN cycle per defect, keeping changes surgical. | All approved bounded code, validator, and public-documentation changes have observed RED/GREEN evidence; the fresh repository suite passed `127/127`. |
| 7. Final review and validation | Completed | Run independent review, regression, performance/scientific validation, documentation checks, and hashes. | Formal test report, English summary, review verdict, and reproducible evidence are complete. |
| 8. Resume audit and integrity reconciliation | Completed | Re-run the final verification stack after session recovery and apply the user-directed exclusion for the historical `=10.1` path. | Fresh commands and actual numeric outputs are recorded; R-027 is closed as a scope exclusion and does not block delivery. |

| 9. Branch checkpoint and next-stage handoff | In progress | Record the independent pre-commit review, run the final verification stack, stage only confirmed deliverables, commit with Lore trailers, push `origin/des`, and create the bounded next-stage task record. | Clean branch checkpoint is pushed without the ignored path; the next stage has its own requirements/design/harness and Claude design-review artifact. |

## Initial Acceptance Model

| Goal | Required Evidence |
|---|---|
| Tighter than traditional roofline | On identical rows, both bounds remain below actual latency and DES has a lower mean/median absolute relative gap than a dimensionally correct classical roofline. |
| `10000x` faster than cycle accurate | Same modeled workload and clearly identified cycle-accurate reference; measured simulator-runtime ratio `cycle_accurate_runtime / DES_runtime >= 10000`. No proxy ratio is accepted as proof. |
| Interpretable and zero-shot | Reports expose event/resource/critical-path attribution; prediction uses only workload and hardware specifications; no trained latency model or target-hardware fitting enters the DES path; held-out hardware evidence is required for empirical zero-shot claims. |
| Optimization gap | Bound-valid rows report a finite value in `[0, 1]`; bound violations fail fast or are explicitly rejected from acceptance rather than converted into a misleading gap. |

## Verification Strategy

1. Run targeted tests for each reviewed component and a fresh full repository suite.
2. Reproduce every defect before editing and preserve RED output.
3. Record predicted, actual, classical-bound, absolute gap, relative gap, simulator runtime, and comparison runtime when available.
4. Run `compileall`, source-reference checks, Markdown structure checks, and SHA-256 verification before completion.
5. Keep implementation, tested, scientifically accepted, and unsupported claims distinct.

## Architecture BLOCK Boundary

The independent architect and adversarial StepCode Claude both returned **BLOCK** for public scientific acceptance and broad implementation. This task must not implement:

- a `SafeBoundEvaluator` or scheduler rewrite;
- CTA residency, multi-resource demand, or SM/lane affinity;
- persistent-CTA or split-K execution semantics;
- a cache hierarchy or implicit warm-cache state;
- a scheduler-performance refactor;
- a cycle-accurate or multi-hardware benchmark campaign.

The current scheduler remains an explanatory feasible list scheduler. Its `makespan` must not be automatically certified or renamed as `DES_bound`.

## File-Level Narrow TDD Sequence

| Order | Behavior | RED Test | Minimal Production/Validation Change | Acceptance |
|---:|---|---|---|---|
| 1 | Bounded comparison metric | `tests/unit/test_bound_comparison.py` | Add a focused comparison helper and public export; require finite positive `actual_time` and `des_bound`, reject `des_bound > actual_time`, and never accept `SimulationResult` implicitly. | Exact `0.25/0.75` gap/efficiency example passes; all invalid branches raise `ValueError`. |
| 2 | Legacy GEMM work convention | `tests/integration/test_operator_simulation.py` | Change one-tile MMA count to `ceil(2*M*N*K/256)`. | Exact instruction count and all legacy operator tests pass. |
| 3 | Hardware rate/resource consistency | `tests/unit/test_hardware_adapter.py` | Reject non-positive required rates and unknown `operator_type`; use one chip-wide L2 lane and the L2 coefficient for `GlobalStore`. | H100 aggregate L2 capacity equals `8,820,000 B/us`; invalid fields/types fail fast. |
| 4 | Cold-input traffic conservation | `tests/integration/test_gemm_v2_simulation.py` | Under the explicitly cold-HBM contract, count unique A+B once and do not divide already-unique B bytes. Do not add a cache model. | Exact unique bytes and fixed-policy monotonicity tests pass. This item proceeds only if the final Claude scope review does not BLOCK it. |
| 5 | FlashAttention integration drift | `tests/integration/test_fa_simulation.py` | Correct FA2 binary-search arguments/tuple handling and use the canonical FA3 scheduling-threshold formula; retain Experimental status. | FA2 path executes; threshold-boundary test matches the canonical decision; input errors fail fast. |
| 6 | Matched GEMM validation | `tests/unit/test_gemm_validation.py` | Correct chip-wide compute units; match cold A+B HBM/output-to-L2 boundary; pass `tile_K`; reject/count split-K and CTA-grid mismatch explicitly; propagate unexpected errors; remove the clamped ratio. | Numeric unit tests, unsupported-policy classification, and unexpected-error propagation pass. |
| 7 | Public truthfulness | Markdown/source-reference checks | Update `README.md`, `docs/des_design_rules.md`, and `docs/event_simulator_design.md` in place with Modification History and Established/Experimental/Unproven/Blocked status. | No unconditional theoretical-bound, `10000x`, empirical zero-shot, or universal-tighter claim remains. |
| 8 | Closure | Full suite, `compileall`, bounded matched validation, independent review | No additional behavior beyond the tested fixes. | All tests pass; numeric evidence and unresolved BLOCK items are recorded in the formal test report and English summary. |
