# DES Event Simulator Documentation Backfill Harness

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added DES scientific invariants and implementation acceptance gates. |
| 2026-07-18 | Added binding WATCH conditions from independent Claude review. |
| 2026-07-18 | Defined documentation backfill gates and anti-drift constraints. |

## Task Gates

1. **Evidence Gate:** A design or status claim must cite an existing tracked document, ignored Ultragoal record, implementation path/symbol, test, or fresh command output.
2. **Intent Gate:** `requirements.md` contains only user intent and Q&A; implementation strategy belongs elsewhere.
3. **Implementation Consistency Gate:** Implementation behavior overrides stale descriptive prose when recording current-state facts, while discrepancies remain explicitly documented.
4. **No-Fallback Gate:** Unknown or contradictory evidence is recorded as an issue; it is not silently reconciled through assumptions.
5. **Scope Gate:** This task changes documentation only and does not alter DES behavior.
6. **Review Gate:** The plan/reconciliation receives an independent Claude perspective, and the final document set receives a separate completion review.
7. **Validation Gate:** Completion requires reproducible structural and content checks plus numeric evidence in a stored test report.
8. **Safety Gate:** No `rm`, `mv`, bulk replacement, or modification of the pre-existing untracked `=10.1` path.

## Completion Principles

- Durable `task_memory` artifacts replace ignored runtime state as the canonical task record; they do not delete the source records.
- Historical design intent and current implementation state must be labeled distinctly.
- Open work belongs in `future.md` only when it is explicitly outside the current documentation-backfill session.
- No phase is marked complete before its stated verification evidence exists.

## DES Scientific and Implementation Gates

1. **Lower-Bound Invariant:** Every validated configuration must satisfy `DES_time <= actual_time`; target violation rate is exactly `0%`.
2. **Peak Calibration:** Derived compute coefficients use per-SM peak rates; chip-wide memory coefficients use chip-wide peak bandwidth. Fixed roofline overheads remain zero.
3. **Rate/Lane Conservation:** A chip-wide coefficient must use one aggregate lane, or be converted to a per-lane coefficient before using `num_sms` lanes. I-011 must be resolved before accepting L2-store tightness.
4. **Overlap:** Independent resource paths overlap maximally; serialization requires a dependency, stream-boundary rule, or shared resource.
5. **Structural Honesty:** Wave, cache, and tile effects claimed by docs must materially affect event work/dependencies/duration. Declaration-only event types and classification-only partial tiles are not accepted as modeled effects.
6. **Fail Fast:** Validation must raise on invalid schemas/configurations and unexpected simulation errors. Broad exception swallowing or silent skipped samples fails acceptance.
7. **Status Separation:** `implemented`, `tested`, and `accepted` are distinct. Passing structural tests cannot satisfy a numeric validation exit criterion.
8. **Validation Reproducibility:** Report dataset/category selection, sample count/seed, evaluated/skipped count, predicted values, actual values, absolute gap, relative gap, violations, and runtime.
9. **Scalability:** The official acceptance dataset must complete in a practical bounded run; a partial/interrupted run cannot be promoted to a full-validation result.
10. **Comparison Integrity:** `improvement_vs_roofline` is valid only when both DES and baseline use the same verified hardware-unit convention.

## Independent Review WATCH Conditions

1. G005 must be labeled **IMPLEMENTED, NOT ACCEPTED**; its `<15%` large-GEMM mean-gap exit criterion is not proven and independent five-sample evidence observed approximately `16.9%`.
2. No `improvement_vs_roofline` value from the current validation script may be used as valid evidence because I-006 overstates H100 compute peak by `4.1397582381x`.
3. I-004, I-006, and I-007 must remain explicit future bugfix work; this documentation-only task must not patch them.
4. `lessons.md` must preserve the verified ops/cycle/SM to chip-wide TFLOPS conversion.
5. `docs/des_design_rules.md` Modification History cleanup remains deferred and must be listed in `future.md`.
