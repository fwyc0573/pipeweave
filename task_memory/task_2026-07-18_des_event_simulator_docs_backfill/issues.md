# DES Event Simulator Documentation Backfill Issues

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Reclassified documentation-governance issues as resolved and retained implementation issues as open. |
| 2026-07-18 | Added L2 rate/lane inconsistency and partial-tile classification-only behavior. |
| 2026-07-18 | Added full-validation scheduler complexity, GEMM v2 semantic drift, and incomplete FlashAttention evidence. |
| 2026-07-18 | Added validation baseline unit error and silent-skip behavior. |
| 2026-07-18 | Added confirmed `tile_k` implementation regression and stale attention documentation. |
| 2026-07-18 | Added preliminary documentation and validation discrepancies for code-level verification. |
| 2026-07-18 | Created the issue and resolution log. |

## Issue Register

### I-001 — Durable design state stops at Phase 0

- **Evidence:** `docs/event_simulator_design.md` labels only Phase 0 as implemented, while `.omc/ultragoal/plan.md` and `.omc/ultragoal/ledger.md` describe later Phase 1+2 work.
- **Root Cause:** Later execution tracking was stored under ignored `.omc/ultragoal/` runtime state and was not reconciled into durable task documentation.
- **Impact:** A new session reading only tracked docs can incorrectly conclude that hardware adapters, structural utilities, and GEMM v2 do not exist.
- **Proposed Resolution:** Verify every claimed story against source/tests, then record historical and current states separately in the durable task artifacts.
- **Status:** Resolved for this task — the current technical state and historical Phase 0 boundary are now reconciled in `design.md` and `summary.md`; implementation follow-up remains in `future.md`.

### I-002 — Large-GEMM validation exit criterion is not proven by the ledger

- **Evidence:** `.omc/ultragoal/plan.md` requires `0%` violations and `<15%` mean gap for large GEMMs; `.omc/ultragoal/ledger.md` reports `0%` violations only for Small GEMM and records a deferred L2 `tile_K` limitation for Large GEMM.
- **Root Cause:** The execution ledger marked G005 complete while simultaneously documenting an unresolved modeling limitation that affects the story's stated large-GEMM acceptance criterion.
- **Impact:** Completion and tightness claims may be overstated if copied into durable docs without fresh validation evidence.
- **Proposed Resolution:** Inspect validation code/artifacts and run the repository's relevant validation/tests; record exact observed metrics and downgrade status if the original exit criterion remains unmet.
- **Status:** Resolved for this task — G005 is durably classified **IMPLEMENTED, NOT ACCEPTED** with fresh numeric evidence.

### I-003 — `docs/des_design_rules.md` lacks a Modification History

- **Evidence:** The file begins with `# DES Refined Roofline — Design Rules and Invariants` and contains no `Modification History` section.
- **Root Cause:** The design-rules document predates or did not follow the current documentation-governance rule.
- **Impact:** Its evolution and provenance are not auditable from the file itself.
- **Proposed Resolution:** Keep this documentation-only backfill focused on the canonical task directory; list an in-place history correction as follow-up unless the final reconciliation shows the existing document must be edited now.
- **Status:** Resolved for this task — in-place cleanup is explicitly deferred to `future.md`; the source document was not modified.

### I-004 — `lower_gemm_v2.tile_k` is documented and validated but unused

- **Evidence:** `event_simulator/operators.py:387` accepts `tile_k`; lines 400–403 claim it controls the live L2 working set; lines 416–417 validate it. The current memory model at lines 452–461 computes `b_tile_col_bytes = tile_n * k * element_bytes` and never references `tile_k`.
- **Root Cause:** A later GEMM memory-model rewrite replaced the earlier tile-K working-set calculation with a B-matrix reuse-factor model but retained the `tile_k` interface and docstring. `git log` shows the earlier `cd44a4c` tile-K correction followed by subsequent memory-model commits.
- **Impact:** Passing a real kernel `tile_k` has no effect. Large K-tiled GEMMs are modeled using full-K B-tile columns, so the L2 reuse estimate can remain too pessimistic and the documented interface is misleading.
- **Proposed Resolution:** This task is documentation-only. Record the mismatch and its validation impact as unresolved future implementation work; do not claim the large-GEMM criterion is satisfied.
- **Status:** Open — implementation change requires a separate explicitly approved bugfix task.

### I-005 — Tracked design docs incorrectly state that attention is unimplemented

- **Evidence:** `docs/event_simulator_design.md` lists attention under Phase 3 and Current Limitations, while commits `a7db073` and `0ee2110` added/exported `lower_flash_attention`; `tests/integration/test_fa_simulation.py` contains structure, scheduling, causal, and validation tests.
- **Root Cause:** The original Phase 0 design document was not updated after post-Ultragoal FlashAttention work.
- **Impact:** Readers cannot determine the current feature surface from tracked docs alone.
- **Proposed Resolution:** Record the current implementation and its actual abstraction level in this durable task documentation. Treat it as task-level FlashAttention lowering, not completion of all original Phase 3 goals such as realistic CTA residency and counter validation.
- **Status:** Resolved for this task — `design.md` labels FlashAttention experimental and distinguishes it from full roadmap Phase 3 acceptance.

### I-006 — Classical roofline validation uses the wrong `tcBf16` unit

- **Evidence:** `tests/validation/validate_gemm_v2.py:32` computes with `hw_config.tc_bf16 * 1e12`, treating `tcBf16` as chip-wide TFLOPS. `docs/des_design_rules.md` and `HardwareConfig` define it as ops/cycle/SM. For H100, the correct chip-wide peak is `4096 × 1830 × 132 / 1e6 = 989.42976` TFLOPS, while the script assumes `4096` TFLOPS (`4.1397582381x` too high).
- **Root Cause:** The validation script was introduced before the later hardware-unit correction and was not updated with the new convention.
- **Impact:** Classical roofline compute time is understated and its gap is overstated, so the printed DES-tightness improvement factor is invalid and systematically inflated.
- **Proposed Resolution:** In a separate bugfix task, compute baseline time from `hw_config.tc_bf16_flops_per_us` (or the equivalent derived chip-wide rate) and add a unit test with the H100 numeric value.
- **Status:** Open — current comparison metric must not be used as completion evidence.

### I-007 — G005 validation silently skips failures and omits available `tile_K`

- **Evidence:** `tests/validation/validate_gemm_v2.py:49–61` catches `Exception` and returns `None`; the main loop then counts the row as skipped. The H100 dataset has 10,800 rows with valid positive core dimensions and provides `tile_K=64`, but `des_predict` does not read or pass `tile_K`.
- **Root Cause:** The validation harness was designed as a best-effort demonstration rather than a fail-fast acceptance test and was not revised after `lower_gemm_v2` gained `tile_k`.
- **Impact:** Implementation errors can disappear from reported metrics, evaluated sample counts can shrink silently, and the validation path cannot exercise the intended tile-K behavior.
- **Proposed Resolution:** In a separate bugfix task, remove the broad catch, validate schema explicitly, pass `tile_k=int(row["tile_K"])`, assert zero unexpected skips, and cover error propagation with tests.
- **Status:** Open — G005 implementation exists, but its acceptance harness is not governance-compliant.

### I-008 — Full G005 validation is not tractable with the current scheduler loop

- **Evidence:** With `PYTHONPATH` corrected, the official script stayed in its 200-row Large category for more than 16 minutes at 100% of one CPU core and was interrupted at `event_simulator/scheduler.py:69`. The sample has median 3,555, p95 42,861, and maximum 70,371 events. Controlled timing from 387 to 6,147 events grew from `0.014453 s` to `1.026491 s`, with the doubling exponent approaching `1.882`.
- **Root Cause:** Each iteration of `while remaining` rescans `ordered_events` from the beginning to find the next ready event. As completed events accumulate, ready selection approaches O(V²), and large GEMMs emit three events per CTA plus lifecycle/memory events.
- **Impact:** The repository validation cannot deliver its intended 400-row acceptance report in a practical interactive run; full metric claims in the ledger are not reproducible from the current command within this task.
- **Proposed Resolution:** In a separate performance bugfix, replace repeated full rescans with a deterministic dependency-count/ready-queue scheduler while preserving ordering semantics, add scaling tests, then rerun the full 400-row validation.
- **Status:** Open — no scheduler code change is authorized in this documentation task.

### I-009 — Current GEMM v2 no longer emits the planned explicit L2 hit/miss split

- **Evidence:** The Ultragoal G004 objective and `lower_gemm_v2` docstring describe L2 hit/miss split events. Current code emits one `GlobalLoad_L2Miss` with discounted effective DRAM bytes; `GlobalLoad_L2Hit` is only declared/calibrated. `compute_l2_hit_ratio` is imported but unused by the lowering.
- **Root Cause:** Successive memory-model corrections evolved the DAG from per-CTA split loads to one chip-level cold-miss event plus analytical B reuse, but the original objective/docstring/event inventory were not reconciled.
- **Impact:** Literal event-level cache breakdown is unavailable, and documentation that promises explicit L2 hit events is stale. The current model can still represent a refined lower bound through effective bytes, but it is a different mechanism.
- **Proposed Resolution:** Document the current effective-byte design exactly. A future design decision must either restore explicit hit events with consistent bandwidth lanes or revise public contracts/docstrings to the chip-level effective-traffic model.
- **Status:** Open — design choice requires separate approval.

### I-010 — FlashAttention lowering lacks complete measurement validation

- **Evidence:** FlashAttention lowering and 10 integration tests exist, but `dataset/fa3_benchmark_h800.csv` contains only two measured configurations, and no tracked validator compares DES predictions to that CSV. The original Phase 3 also requires residency modeling and mechanism-counter validation, which are absent.
- **Root Cause:** Post-Ultragoal work implemented task-level compute/DRAM decomposition and basic tests before the full Phase 3 characterization/validation program.
- **Impact:** Attention can be simulated structurally, but accuracy, bound validity across configurations, and the broader Phase 3 exit criterion are unproven.
- **Proposed Resolution:** Label FlashAttention as experimental task-level lowering, not completed Phase 3; finish benchmark coverage and add a fail-fast prediction-vs-measurement validator in future work.
- **Status:** Open — current documentation now labels the lowering experimental; measurement validation remains future work.

### I-011 — L2 calibration and lane capacity do not conserve chip-wide bandwidth

- **Evidence:** `derive_calibration` computes `GlobalStore` duration from `1 / hw.l2_bandwidth_bytes_per_us`, where the hardware value is chip-wide. `derive_resource_config` assigns `l2_bandwidth = num_sms` lanes. `docs/des_design_rules.md` says chip-wide rate implies one lane, although its L2 table simultaneously lists `num_sms` lanes. Adapter tests assert 132 H100 L2 lanes but do not test aggregate rate conservation.
- **Root Cause:** The model conflates physical per-SM L2 slices with a chip-wide aggregate bandwidth coefficient.
- **Impact:** Up to `num_sms` store events can each consume the full chip-wide rate concurrently, overestimating aggregate L2 service by as much as `num_sms`. This remains optimistic, so it does not threaten the lower-bound direction, but it weakens tightness and violates the documented rate/lane consistency rule.
- **Proposed Resolution:** Choose one representation: one lane with the chip-wide coefficient, or `num_sms` lanes with a coefficient derived from per-slice bandwidth. Add an aggregate-throughput test before accepting L2-store metrics.
- **Status:** Open — separate design/bugfix approval required.

### I-012 — Partial-tile events are classified but do not model padded-work inefficiency

- **Evidence:** `lower_gemm_v2` labels edge CTAs `MMA_PartialTile` but computes instructions from clamped `actual_m * actual_n * k`; full and partial event types share the same coefficient. `compute_tile_efficiency` is tested but unused.
- **Root Cause:** The lowering retained optimistic useful-work accounting while adding a structural event label, without defining a separate padded instruction count or efficiency effect.
- **Impact:** Partial tiling does not add structural time as claimed by the design rules; the event taxonomy overstates the modeled mechanism.
- **Proposed Resolution:** Make an explicit design decision between ideal useful-work lower bound and padded physical instruction work. Then align design rules, event naming, lowering math, and tests without an empirical scaling factor.
- **Status:** Open — separate design approval required.

## Status Summary

| Category | Issue IDs | Count |
|---|---|---:|
| Resolved documentation-governance issues | I-001, I-002, I-003, I-005 | 4 |
| Open implementation/design/validation issues | I-004, I-006, I-007, I-008, I-009, I-010, I-011, I-012 | 8 |
| Total recorded issues | I-001–I-012 | 12 |
