# Test Report: DES Event Simulator Documentation Backfill

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-18 | Added fresh final regression, structural, checksum, and worktree closure evidence. |
| 2026-07-18 | Added the final documentation, regression, bounded-validation, scalability, and acceptance evidence. |

## 1. Test Script Information

### Environment

| Item | Actual Value |
|---|---|
| Worktree | `/data/ycfeng/pipeweave/.worktrees/des` |
| Conda environment | Not active (`CONDA_DEFAULT_ENV` unset) |
| Virtual environment | Not active (`VIRTUAL_ENV` unset) |
| Python executable | `/usr/bin/python` |
| Python | `3.12.3` |
| pytest | `9.1.1` |
| numpy | `2.4.6` |
| pandas | `3.0.3` |
| Required runtime path for direct validation script | `PYTHONPATH="$PWD"` |

### Test and Validation Files

| Type | Full Path |
|---|---|
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_event_scheduler.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_hardware_adapter.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_structural.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_operator_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_gemm_v2_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_fa_simulation.py` |
| Validation | `/data/ycfeng/pipeweave/.worktrees/des/tests/validation/validate_gemm_v2.py` |
| Documentation | `/data/ycfeng/pipeweave/.worktrees/des/task_memory/task_2026-07-18_des_event_simulator_docs_backfill/` |

### Reproducible Commands

Run from `/data/ycfeng/pipeweave/.worktrees/des`:

```bash
python --version
python - <<'PY'
import sys
import numpy
import pandas
import pytest

print(sys.executable)
print(pytest.__version__)
print(numpy.__version__)
print(pandas.__version__)
PY

TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time python -m pytest tests -q

TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time python -m compileall -q event_simulator tests

PYTHONPATH="$PWD" python tests/validation/validate_gemm_v2.py
```

The deterministic bounded audit uses the same H100 dataset filters as `validate_gemm_v2.py`, but selects exactly five rows per category using:

```python
category.sample(n=5, random_state=42)
```

It intentionally reports DES only. The current script's classical-roofline comparison is excluded from acceptance because I-006 gives that baseline the wrong throughput unit.

## 2. Validation Criteria

| Validation Area | Metric / Output | Acceptance Criterion |
|---|---|---|
| Required task artifacts | Base Markdown file count | Exactly 11 required files exist. |
| Documentation history | `Modification History` presence | Present in every Markdown task artifact, including this report. |
| Requirements provenance | `[Original Request]` tags | Every numbered requirement contains the tag. |
| Progress auditability | Required fix-record fields | Every session record contains Motivation, Expectation, Method, and Result. |
| Review auditability | Required review fields | Every review entry contains all five mandated fields. |
| Summary contract | Required English sections | Task Overview, Deliverables Inventory, Validation Status, and Open Items/Future Extensions exist. |
| Source-path traceability | Repository-relative backtick paths | Every checked cited path exists; ignored runtime evidence is allowed to remain ignored. |
| Python syntax/import compilation | `compileall` exit code | Exit code `0`. |
| Regression suite | pytest outcomes | All collected tests pass; zero failures/errors. |
| DES lower-bound invariant | `predicted_us <= actual_us` | `0%` violations. |
| G005 large-GEMM tightness | Mean `(actual - DES) / actual` | Strictly less than `15%`. |
| G005 reproducibility | Official 400-row validation | Completes without silent skips or unexpected exceptions. |
| `tile_k` structural behavior | Event signature and makespan delta | A documented structural input should materially affect the relevant modeled mechanism. |
| Classical baseline integrity | H100 BF16 peak conversion | Per-SM ops/cycle must be converted to chip-wide TFLOPS before comparison. |

## 3. Test Results and Evidence

### 3.1 Result Summary

| Test / Validation Area | Result | Expected | Actual Evidence |
|---|---|---:|---:|
| Required base artifacts | PASS | 11 | 11 |
| Repository regression suite | PASS | 74/74 | 74/74 passed |
| Python compile check | PASS | Exit `0` | Exit `0` |
| Bounded lower-bound check | PASS | 0/15 violations | 0/15 violations (`0.000000%`) |
| Large bounded mean gap | **FAIL** | `<15.000000%` | `16.922601%` |
| Large gap delta from target | **FAIL** | `<0 percentage points` | `+1.922601` percentage points |
| Full 400-row validation | **FAIL / INCOMPLETE** | Complete practical run | Still in Large category after more than 16 minutes; manually interrupted |
| Classical roofline comparison | **INVALID** | Dimensionally correct baseline | Peak overstated by `4.1397582381x` |
| `tile_k` behavior | **FAIL** | Material structural effect | 0 event-signature changes; `0.000000000000 us` makespan delta |
| Documentation backfill task | PASS after final structural checks | All gates satisfied | Durable artifacts, review, report, and hashes recorded |
| G005 acceptance | **NOT ACCEPTED** | All G005 gates pass | Lower-bound passes, but tightness, scalability, and harness-integrity gates fail |

### 3.2 Regression Suite

Command:

```bash
TIMEFORMAT=$'ELAPSED_SECONDS=%3R\nUSER_SECONDS=%3U\nSYS_SECONDS=%3S'
time python -m pytest tests -q
```

| Test File | Passed | Failed |
|---|---:|---:|
| `tests/unit/test_event_scheduler.py` | 14 | 0 |
| `tests/unit/test_hardware_adapter.py` | 8 | 0 |
| `tests/unit/test_structural.py` | 24 | 0 |
| `tests/integration/test_operator_simulation.py` | 7 | 0 |
| `tests/integration/test_gemm_v2_simulation.py` | 11 | 0 |
| `tests/integration/test_fa_simulation.py` | 10 | 0 |
| **Total** | **74** | **0** |

Initial audit evidence:

```text
74 passed in 2.19s
ELAPSED_SECONDS=2.590
```

The final completion run is recorded again in Section 3.9 so the delivery claim uses fresh evidence after all documentation edits.

### 3.3 Deterministic Bounded GEMM Validation

Dataset facts:

| Metric | Actual |
|---|---:|
| H100 rows | 10,800 |
| Large rows available | 4,231 |
| Medium rows available | 1,798 |
| Small rows available | 3,562 |
| Random seed | 42 |
| Sample size per category | 5 |
| Total evaluated | 15 |
| Total skipped | 0 |

Aggregate metrics:

| Category | Evaluated | Skipped | Violations | Violation Rate | Mean Gap | Median Gap | Gap Range |
|---|---:|---:|---:|---:|---:|---:|---:|
| Large | 5 | 0 | 0 | `0.000000%` | `16.922601%` | `18.139800%` | `13.702786%`–`20.754829%` |
| Medium | 5 | 0 | 0 | `0.000000%` | `46.647680%` | `44.013243%` | `29.472309%`–`65.989583%` |
| Small | 5 | 0 | 0 | `0.000000%` | `45.909409%` | `57.965279%` | `14.202214%`–`81.805879%` |
| **All** | **15** | **0** | **0** | **`0.000000%`** | Not pooled for acceptance | Not pooled for acceptance | `13.702786%`–`81.805879%` |

The per-row relative gap is `(actual_us - predicted_us) / actual_us`. Positive values indicate an optimistic lower bound; `predicted_us > actual_us` would be a bound violation.

#### Large Rows

| M | N | K | tile_M | tile_N | Dataset tile_K | DES Predicted (us) | Actual (us) | Absolute Gap (us) | Relative Gap | Violation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 10,113 | 4,608 | 7,168 | 208 | 192 | 64 | 687.446776707 | 797.804600000 | 110.357823293 | 13.832688% | No |
| 5,889 | 2,048 | 6,144 | 248 | 128 | 64 | 156.136971313 | 190.836600000 | 34.699628687 | 18.182900% | No |
| 36,864 | 2,560 | 2,048 | 128 | 320 | 64 | 402.909682710 | 492.192400000 | 89.282717290 | 18.139800% | No |
| 32,768 | 2,304 | 16,384 | 192 | 192 | 64 | 2,578.487566898 | 2,987.915200000 | 409.427633102 | 13.702786% | No |
| 6,945 | 2,304 | 3,584 | 160 | 256 | 64 | 117.532633529 | 148.315200000 | 30.782566471 | 20.754829% | No |

#### Medium Rows

| M | N | K | tile_M | tile_N | Dataset tile_K | DES Predicted (us) | Actual (us) | Absolute Gap (us) | Relative Gap | Violation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 416 | 1,536 | 1,024 | 104 | 64 | 64 | 1.822550216 | 5.358800000 | 3.536249784 | 65.989583% | No |
| 480 | 1,536 | 8,960 | 96 | 64 | 64 | 14.692190111 | 23.246400000 | 8.554209889 | 36.797998% | No |
| 375 | 2,432 | 2,560 | 64 | 112 | 64 | 4.900451305 | 11.387200000 | 6.486748695 | 56.965265% | No |
| 896 | 2,560 | 2,432 | 128 | 144 | 64 | 11.971652301 | 16.974400000 | 5.002747699 | 29.472309% | No |
| 435 | 6,144 | 1,024 | 112 | 192 | 64 | 5.888239160 | 10.517200000 | 4.628960840 | 44.013243% | No |

#### Small Rows

| M | N | K | tile_M | tile_N | Dataset tile_K | DES Predicted (us) | Actual (us) | Absolute Gap (us) | Relative Gap | Violation |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 114 | 5,504 | 2,048 | 64 | 88 | 64 | 3.501794578 | 8.865800000 | 5.364005422 | 60.502216% | No |
| 74 | 151,936 | 5,120 | 80 | 384 | 64 | 464.329896907 | 541.191000000 | 76.861103093 | 14.202214% | No |
| 116 | 4,352 | 5,120 | 64 | 96 | 64 | 8.397108144 | 19.976600000 | 11.579491856 | 57.965279% | No |
| 86 | 8,192 | 8,192 | 88 | 64 | 64 | 40.457579229 | 47.637200000 | 7.179620771 | 15.071458% | No |
| 28 | 1,536 | 2,048 | 16 | 64 | 64 | 0.972584956 | 5.345600000 | 4.373015044 | 81.805879% | No |

### 3.4 G005 Acceptance Decision

| Criterion | Expected | Actual | Delta | Decision |
|---|---:|---:|---:|---|
| Large bound violation rate | `0.000000%` | `0.000000%` | `0.000000` points | PASS |
| Large mean gap | `<15.000000%` | `16.922601%` | `+1.922601` points | FAIL |
| Evaluated/skipped integrity | 5/0 for bounded audit | 5/0 | 0 skipped | PASS for bounded audit |
| Official run completion | 400 evaluated | Not completed | More than 16 minutes without leaving Large category | FAIL |

Decision: **G005 is IMPLEMENTED, NOT ACCEPTED.** The bounded audit supports the DES lower-bound invariant but does not satisfy the large-GEMM tightness requirement, and the official validation cannot presently complete in a practical bounded run.

### 3.5 `tile_k` Behavioral Regression Evidence

Controlled configuration:

```text
M = N = K = 4096
tile_M = tile_N = 128
tile_k values = 0 and 64
```

| Metric | `tile_k=0` | `tile_k=64` | Delta / Equality |
|---|---:|---:|---:|
| Event count | 3,075 | 3,075 | 0 |
| Full event signatures | Reference | Comparison | Equal |
| Makespan | 143.257862154871 us | 143.257862154871 us | 0.000000000000 us |

This confirms I-004: the documented `tile_k` parameter currently has no behavioral effect in `lower_gemm_v2`.

### 3.6 Full-Validation Failure and Root Cause

Initial direct invocation:

```bash
python tests/validation/validate_gemm_v2.py
```

Observed failure:

```text
ModuleNotFoundError: No module named 'event_simulator'
```

Root cause: direct script execution sets the import root to `tests/validation`, not the repository root. The reproducible invocation is:

```bash
PYTHONPATH="$PWD" python tests/validation/validate_gemm_v2.py
```

With the import path corrected, the process consumed one CPU core at 100%, remained in the 200-row Large category for more than 16 minutes, and was manually interrupted. The traceback was at `event_simulator/scheduler.py:69` in the ready-event selection scan.

Large-sample event distribution:

| Metric | Events |
|---|---:|
| Minimum | 381 |
| Median | 3,555 |
| P90 | 28,517 |
| P95 | 42,861 |
| Maximum | 70,371 |
| Mean | 9,667.935 |

Controlled scheduler scaling:

| CTAs | Events | Scheduler Time | Approximate Doubling Exponent |
|---:|---:|---:|---:|
| 128 | 387 | 0.014453 s | Baseline |
| 256 | 771 | 0.032426 s | 1.172 |
| 512 | 1,539 | 0.087180 s | 1.427 |
| 1,024 | 3,075 | 0.278809 s | 1.677 |
| 2,048 | 6,147 | 1.026491 s | 1.882 |

Root cause: the scheduler's `while remaining` loop scans `ordered_events` from the beginning for every selected event. Ready selection therefore approaches O(V²). This is recorded as I-008; no scheduler patch is authorized in this documentation-only task.

### 3.7 Classical-Roofline Unit Integrity

Repository H100 values:

```text
tcBf16 = 4096 ops/cycle/SM
smFreq = 1830 MHz
numSms = 132
```

| Metric | Expected / Correct | Current Validation Script | Error Factor |
|---|---:|---:|---:|
| Chip-wide BF16 peak | `4096 × 1830 × 132 / 1e6 = 989.42976 TFLOPS` | `4096 TFLOPS` | `4.1397582381x` high |

Because classical roofline compute time is understated, the current `improvement_vs_roofline` output is invalid and is not used anywhere in this acceptance decision.

### 3.8 Failure Handling Record

| Failure | Root Cause | Resolution in This Task | Final Status |
|---|---|---|---|
| `/usr/bin/time` not found | GNU `time` is absent from the host | Used Bash built-in `time` with `TIMEFORMAT`; documented in `task_memory/env_handbook.md` | Resolved |
| Direct validation import failed | Repository root absent from script import path | Set `PYTHONPATH="$PWD"`; documented in `task_memory/env_handbook.md` | Resolved |
| Official validation did not finish | Scheduler ready scan approaches O(V²) | Preserved evidence, ran bounded deterministic audit, opened I-008; did not patch code | Open implementation issue |
| Large mean gap exceeded target | Current GEMM v2 structural/memory model is not tight enough for the sampled target | Downgraded G005; recorded I-004/I-009/I-011/I-012 | Open implementation/design issue |
| Baseline comparison dimensionally wrong | Per-SM rate treated as chip-wide TFLOPS | Excluded metric and opened I-006; no scaling-factor workaround | Open validation issue |
| Validation silently catches exceptions | Broad `except Exception` implements best-effort skipping | Opened I-007 and refused to treat the harness as acceptance-compliant | Open validation issue |

### 3.9 Final Documentation and Regression Verification

Fresh post-reconciliation regression evidence:

```text
74 passed in 2.16s
PYTEST_ELAPSED_SECONDS=2.543
PYTEST_USER_SECONDS=2.441
PYTEST_SYS_SECONDS=0.068

compileall exit code: 0
COMPILE_ELAPSED_SECONDS=0.044
COMPILE_USER_SECONDS=0.040
COMPILE_SYS_SECONDS=0.004
```

The final structural-check output, checksum verification, and worktree status are added after all completion-state documents and hashes are finalized.

Final closure metrics:

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Required base artifacts | 11 | 11 | PASS |
| Task Markdown histories | 12 | 12 | PASS |
| `[Original Request]` tags | 2 | 2 | PASS |
| Progress records with all four fields | 10 | 10 | PASS |
| Review entries with all five fields | 2 | 2 | PASS |
| Required summary sections | 4 | 4 | PASS |
| Unresolved hash/status placeholders | 0 | 0 | PASS |
| Missing checked cited paths | 0 | 0 | PASS |
| Verified checksum entries | 13 | 13 | PASS |
| Source diff under `event_simulator/`, `tests/`, `docs/`, and `README.md` | Empty | Empty | PASS |

Checksum evidence:

```text
13/13 files: OK
sha256sum exit code: 0
```

Final worktree evidence:

```text
?? =10.1
?? task_memory/
```

The `=10.1` path predates this task and was not modified. The new `task_memory/` tree is the requested durable documentation output.

## 4. Final Acceptance Statement

- **Documentation backfill:** PASS after the complete Section 3.9 closure evidence is recorded.
- **DES implementation regression suite:** PASS for the tested 74 cases.
- **DES scientific lower-bound check:** PASS for the deterministic 15-row bounded sample only.
- **G005 validation story:** **IMPLEMENTED, NOT ACCEPTED**.
- **FlashAttention lowering:** Implemented and integration-tested, but experimental and not measurement-accepted.
- **Implementation code changes in this task:** 0.
