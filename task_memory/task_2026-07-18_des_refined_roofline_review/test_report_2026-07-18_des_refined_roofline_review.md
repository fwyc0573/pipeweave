# Test Report: DES Refined Roofline Review and Bounded Remediation

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-19 | Added the authoritative final post-document verification snapshot from session `97006`, including exact timing and exit-code metrics. |
| 2026-07-19 | Added the fresh pre-commit verification stack with exact test, validator, smoke, checksum, and diff metrics. |
| 2026-07-19 | Added the user-directed ignored-path disposition and final pre-commit review evidence. |
| 2026-07-19 | Added fresh resume-audit results and reconciled the active closure scope. |
| 2026-07-18 | Created the formal report with TDD history, fresh regression evidence, matched-boundary metrics, failure resolutions, and scientific claim verdicts. |

**Date:** 2026-07-18
**Resume-audit date:** 2026-07-19
**Repository:** `/data/ycfeng/pipeweave/.worktrees/des`
**Branch:** `des`
**Scope:** Bounded local code/documentation remediation and scientific review; broad DES architecture remains outside this task.

## 1. Test Script Information

### Environment

| Item | Actual Value |
|---|---|
| Conda environment | `<unset>` |
| Python | `3.12.3` |
| Python executable | `/usr/bin/python` |
| pytest | `9.1.1` |
| pandas | `3.0.3` |
| numpy | `2.4.6` |
| Repository import path | `PYTHONPATH="$PWD"` |
| Bytecode/cache policy for final run | `PYTHONDONTWRITEBYTECODE=1`, pytest `-p no:cacheprovider` |

No GPU, Docker, external service, or network dependency was used. The H100 results use checked-in hardware specifications and `dataset/gemm_test.csv`.

### Test and validation scripts

| Type | Full Path |
|---|---|
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_bound_comparison.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_hardware_adapter.py` |
| Unit | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_gemm_validation.py` |
| Unit / docs contract | `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_des_documentation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_operator_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_gemm_v2_simulation.py` |
| Integration | `/data/ycfeng/pipeweave/.worktrees/des/tests/integration/test_fa_simulation.py` |
| Scientific validator | `/data/ycfeng/pipeweave/.worktrees/des/tests/validation/validate_gemm_v2.py` |

### Exact reproducible commands

#### Targeted changed-path tests

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
TIMEFORMAT=$'TARGETED_ELAPSED_SECONDS=%3R\nTARGETED_USER_SECONDS=%3U\nTARGETED_SYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider \
    tests/unit/test_bound_comparison.py \
    tests/unit/test_hardware_adapter.py \
    tests/unit/test_gemm_validation.py \
    tests/unit/test_des_documentation.py \
    tests/integration/test_operator_simulation.py \
    tests/integration/test_gemm_v2_simulation.py \
    tests/integration/test_fa_simulation.py -q
```

#### Full regression

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
TIMEFORMAT=$'FULL_ELAPSED_SECONDS=%3R\nFULL_USER_SECONDS=%3U\nFULL_SYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python -m pytest -p no:cacheprovider tests -q
```

#### Compilation

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
TIMEFORMAT=$'COMPILE_ELAPSED_SECONDS=%3R\nCOMPILE_USER_SECONDS=%3U\nCOMPILE_SYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 \
  python -m compileall -q \
    event_simulator tests/unit tests/integration tests/validation
```

#### Matched-boundary H100 validator

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
TIMEFORMAT=$'VALIDATOR_ELAPSED_SECONDS=%3R\nVALIDATOR_USER_SECONDS=%3U\nVALIDATOR_SYS_SECONDS=%3S'
time env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
  python tests/validation/validate_gemm_v2.py
```

#### Cross-hardware adapter smoke

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python - <<'PY'
from pathlib import Path

from event_simulator import derive_calibration, derive_resource_config, load_hardware_config

operator_types = ("gemm", "gemm_v2", "flash_attention", "rmsnorm", "silu_and_mul")
paths = sorted(Path("hardware").glob("*.json"))
for path in paths:
    hardware = load_hardware_config(path)
    calibration = derive_calibration(hardware)
    configs = {
        name: derive_resource_config(hardware, operator_type=name)
        for name in operator_types
    }
    assert len(calibration.duration_per_unit) == 22
    assert len(configs) == 5
    assert all(
        config.capacities["l2_bandwidth"] == 1
        for name, config in configs.items()
        if name in {"gemm", "gemm_v2"}
    )
print(f"hardware_files={len(paths)}")
print("calibration_coefficients_per_hardware=22")
print("known_operator_configs_per_hardware=5")
PY
```

#### Scheduler order-dependence counterexample

```bash
cd /data/ycfeng/pipeweave/.worktrees/des
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python - <<'PY'
from event_simulator import Event, ResourceConfig, schedule

resources = ResourceConfig({"a": 1, "b": 1})
long = Event("long", "MMA", "kernel", "stream-long", "a", 10.0, stream_ordered=False)
short = Event("short", "MMA", "kernel", "stream-short", "a", 1.0, stream_ordered=False)
tail = Event(
    "tail", "FMA", "kernel", "stream-tail", "b", 10.0,
    dependencies=("short",), stream_ordered=False,
)
for name, events in (("long-first", [long, short, tail]), ("short-first", [short, long, tail])):
    result = schedule(events, resources)
    print(f"{name}_makespan={result.makespan:.1f}")
PY
```

The absolute-time and old/new Small diagnostics use the same public functions and deterministic `random_state=42` samples. Their selection rules, formulas, and full numeric outputs are preserved below; the official validator command above independently reproduces the population, rejection, violation, paired-gap, and runtime results.

## 2. Validation Criteria

### Code behavior

1. Every modified logical branch is exercised, including both FA3 threshold outcomes.
2. `BoundComparison` owns its invariant for factory and direct construction:
   - finite real values only;
   - `0 < des_bound <= actual_time`;
   - derived metrics cannot be supplied by callers;
   - `optimization_gap + hardware_efficiency = 1`.
3. Required hardware rates and operator types fail fast; no zero-duration fallback is accepted.
4. Chip-wide L2 bandwidth appears once: one lane at the declared chip-wide rate.
5. Under the declared cold-HBM GEMM boundary, modeled input traffic equals unique A+B once and output C terminates at L2.
6. FA2/FA3 integration follows the reused call/threshold contracts for the tested surface and rejects malformed input.
7. The validator propagates unexpected exceptions, counts named unsupported rows, uses an exhaustive category partition, and compares tightness only where both candidates satisfy the bound check.

### Regression and artifact quality

1. Targeted and full pytest runs have exit code `0` and zero failures.
2. `compileall` has exit code `0`.
3. Public and source documentation contains no unconditional greedy lower-bound, global `10000x`, empirical zero-shot, or universal tighter-than-classical claim.
4. All task artifacts contain Modification History, required sections, and no unresolved draft markers.
5. `git diff --check` passes. The historical `=10.1` path is explicitly ignored by user instruction and is excluded from active validation and staging; no existence assertion is required.

### Scientific acceptance

| Goal | Acceptance Criterion |
|---|---|
| Tighter than classical roofline | Same rows and boundary; both candidates valid; DES has a smaller gap. Category/sample results must not be generalized. |
| `10000x` faster | Same workload and boundary against a named cycle-accurate comparator, with measured runtime ratio at least `10000`. |
| Interpretable | Event work, dependencies, resources, selected timeline, and selected critical path are auditable. |
| Cross-hardware zero-shot | Held-out multi-hardware accuracy with no target-hardware latency fitting. A constructible spec path alone is insufficient. |
| Optimization gap | Only an externally accepted positive bound may be compared; violations must raise rather than be clamped. |
| Universal theoretical bound | Order-invariant proven safe evaluation plus matched launch/residency/measurement contracts. |

## 3. Test Results and Evidence

### Final test summary

| Suite | Expected | Actual | Result |
|---|---:|---:|---|
| Targeted changed paths | All pass | `93/93` passed in `2.66s`; elapsed `3.114s`; user `4.894s`; sys `0.080s` | PASS |
| Full repository regression | All pass | `131/131` passed in `2.75s`; elapsed `3.281s`; user `5.107s`; sys `0.086s` | PASS |
| Compileall | Exit `0` | Exit `0`; elapsed `0.108s`; user `0.056s`; sys `0.004s`; no output | PASS |
| Matched H100 validator | Exit `0`, no hidden failures | Exit `0`; elapsed `3.583s`; user `5.236s`; sys `0.099s` | PASS as an audit; scientific violations remain visible |
| Hardware adapter smoke | `11` hardware files, `22` coefficients, `5` configs each | `11/11`, `22/22`, `5/5` | PASS |

### Resume-audit verification (2026-07-19)

These are fresh runs from the recovered worktree, not copied historical claims.

| Check | Command/result | Actual evidence | Status |
|---|---|---:|---|
| Targeted changed paths | `python -m pytest -p no:cacheprovider ... -q` | `93/93` passed; pytest `8.52s`; shell elapsed `9.741s`; exit `0` | PASS |
| Full repository regression | `python -m pytest -p no:cacheprovider tests -q` | `131/131` passed; pytest `2.76s`; shell elapsed `3.225s`; exit `0` | PASS |
| Python compilation | `python -m compileall -q event_simulator tests/unit tests/integration tests/validation` | exit `0`; shell elapsed `0.265s`; no output | PASS |
| Matched H100 validator | `python tests/validation/validate_gemm_v2.py` | exit `0`; shell elapsed `3.618s`; `4,246/10,800` supported policy rows and four Small DES violations remain visible | PASS as audit |
| Cross-hardware smoke | Inline Python over `hardware/*.json` | `11/11` files; `22` coefficients and `5` configs per file; one L2 lane for GEMM/GEMM-v2 | PASS |
| Diff whitespace | `git diff --check` | exit `0` | PASS |

The historical `=10.1` path is explicitly **ignored** by user instruction and excluded from active validation and staging. No existence check or filesystem operation was performed for delivery. Issue `R-027` is closed as a scope exclusion, not a test or source-code failure.

### Final post-document verification (2026-07-19, session `97006`)

This is the authoritative fresh run after the report, summary, notes, progress, and review artifacts were reconciled. The earlier resume-audit table remains as a historical snapshot; timing variation is expected because the commands were rerun independently.

| Check | Command/result | Actual evidence | Status |
|---|---|---:|---|
| Targeted changed paths | `python -m pytest -p no:cacheprovider ... -q` | `93/93` passed; pytest `2.63s`; shell elapsed `3.088s`; user `4.996s`; sys `0.169s`; exit `0` | PASS |
| Full repository regression | `python -m pytest -p no:cacheprovider tests -q` | `131/131` passed; pytest `2.65s`; shell elapsed `3.118s`; user `4.739s`; sys `0.116s`; exit `0` | PASS |
| Python compilation | `python -m compileall -q event_simulator tests/unit tests/integration tests/validation` | exit `0`; elapsed `0.046s`; user `0.042s`; sys `0.004s`; no output | PASS |
| Matched H100 validator | `python tests/validation/validate_gemm_v2.py` | exit `0`; elapsed `3.401s`; user `5.322s`; sys `0.080s`; `4,246/10,800` supported policy rows and four Small DES violations remain visible | PASS as audit |
| Cross-hardware smoke | Inline Python over `hardware/*.json` | `11/11` files; `22` coefficients and `5` configs per file; one L2 lane for GEMM/GEMM-v2 | PASS |
| Diff whitespace | `git diff --check` | exit `0` | PASS |
| Artifact checksums | `sha256sum -c task_memory/task_2026-07-18_des_refined_roofline_review/checksums.sha256` | `28/28` entries `OK`; exit `0` | PASS |
| Historical path handling | User-directed scope rule | Excluded from validation and staging; no filesystem operation | CLOSED R-027 |


## Pre-commit verification (2026-07-19)

This is the fresh validation run after the user-directed scope reconciliation and the latest Claude pre-commit review. The ignored `=10.1` path was not inspected or staged.

### Test Script Information

- Worktree: `/data/ycfeng/pipeweave/.worktrees/des`
- Environment: `/usr/bin/python` 3.12.3; no active conda or virtual environment; pytest 9.1.1; pandas 3.0.3; numpy 2.4.6.
- Targeted command:
  ```bash
  PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider \
    tests/unit/test_bound_comparison.py \
    tests/unit/test_hardware_adapter.py \
    tests/unit/test_gemm_validation.py \
    tests/unit/test_des_documentation.py \
    tests/integration/test_operator_simulation.py \
    tests/integration/test_gemm_v2_simulation.py \
    tests/integration/test_fa_simulation.py -q
  ```
- Full command: `PYTHONPATH="$PWD" python -m pytest -p no:cacheprovider tests -q`
- Compilation command: `python -m compileall -q event_simulator tests/unit tests/integration tests/validation`
- Validator command: `PYTHONPATH="$PWD" python tests/validation/validate_gemm_v2.py`
- Smoke/checksum commands: the all-hardware adapter loop from the preceding section, `sha256sum -c task_memory/task_2026-07-18_des_refined_roofline_review/checksums.sha256`, and `git diff --check`.

### Validation Criteria

- Targeted and full pytest suites exit `0` with zero failures.
- Compilation exits `0`.
- The H100 validator exits `0` while retaining explicit unsupported-row, split-K, CTA-mismatch, and bound-violation counts.
- All hardware specifications construct `22` calibration coefficients and `5` known operator configurations, with one chip-wide L2 lane for GEMM/GEMM-v2.
- All `28` task-manifest entries verify, and whitespace validation exits `0`.
- The ignored `=10.1` path remains outside all active checks and staging.

### Test Results and Evidence

| Check | Expected | Actual | Result |
|---|---|---|---|
| Targeted changed-path tests | All pass | `93/93` passed; pytest `2.66s`; shell elapsed `3.108s`; user `5.032s`; sys `0.096s`; exit `0` | PASS |
| Full repository regression | All pass | `131/131` passed; pytest `2.77s`; shell elapsed `3.218s`; user `4.807s`; sys `0.170s`; exit `0` | PASS |
| Python compilation | Exit `0` | exit `0`; elapsed `0.046s`; user `0.037s`; sys `0.008s`; no output | PASS |
| Matched H100 validator | Exit `0`; visible rejection/violation accounting | exit `0`; elapsed `3.461s`; user `5.328s`; sys `0.107s`; `4,246/10,800` supported rows; four Small DES and classical violations; `437/437` split-K rows unsupported across the population audit | PASS as audit |
| Cross-hardware adapter smoke | `11` files; `22` coefficients; `5` configs each | `11/11` files; `22` coefficients and `5` configs per file; one L2 lane for GEMM/GEMM-v2 | PASS |
| Artifact checksums | `28/28` entries `OK` | `28/28` entries `OK`; exit `0` | PASS |
| Whitespace check | exit `0` | `git diff --check` exit `0` | PASS |
| Historical `=10.1` handling | Excluded by user instruction | Not inspected, staged, or otherwise targeted | CLOSED R-027 |

### Key Numeric Metrics

| Metric | Predicted / expected | Actual | Error / delta |
|---|---:|---:|---:|
| Supported H100 policy rows | `4,246` | `4,246/10,800` | coverage `39.314814815%` |
| Small DES bound violations | `0` for universal-bound acceptance | `4/62` sampled/evaluated (`6.5%`) | remains visible; universal claim blocked |
| Targeted test count | `93` | `93` passed | `0` failures |
| Full test count | `131` | `131` passed | `0` failures |

### TDD RED -> GREEN evidence

| Changed behavior | RED evidence | GREEN evidence | Root-cause fix |
|---|---|---|---|
| Bounded comparison API | `15` assertions failed because the package API was absent | Initial `15/15`, final direct-construction suite `17/17` | Added invariant-owning `BoundComparison` and explicit `compare_des_bound()` export |
| Public value-object construction | `2` new tests failed because callers supplied derived fields and no direct validation ran | `17/17` | `init=False` derived fields plus `__post_init__` validation/computation |
| Legacy GEMM work | Actual `256` instructions vs expected `512` | `8/8` operator integration tests | Restored `2*M*N*K/256` convention |
| L2/rate/fail-fast | `9` failed, `6` passed | `19/19` | One chip-wide L2 lane, L2 store coefficient, positive finite required rates, exact known operator set |
| Cold input conservation | Actual `393,216 B` vs expected `524,288 B`; `M=129` traffic fell below `M=128` | `12/12` | Count unique A+B once; remove division of already-unique B |
| FA2/FA3 integration | `8` failed, `10` passed; FA2 raised `TypeError`; FA3 old/canonical work counts `91/182` | Initial `18/18`, final `19/19` | Correct FA2 arguments/tuple, canonical FA3 formula, validation, both threshold branches |
| GEMM validator | Initial required branches failed `8/8` | `11/11` | Correct units/boundary, explicit rejection accounting, no broad exception, exhaustive `Other` category |
| Public Markdown truthfulness | `5` failed, `1` passed | Public contract `6/6` | Established/Experimental/Unproven/Blocked status and bounded-only metric wording |
| Source documentation truthfulness | `1` failed on stale universal-bound phrases | Combined docs/source contract `7/7` | Removed claims that optimistic primitives certify composed greedy makespan |

### Bounded metric numeric check

| Metric | Expected | Actual | Delta |
|---|---:|---:|---:|
| `actual_time` | `4.0` | `4.0` | `0.0` |
| `des_bound` | `3.0` | `3.0` | `0.0` |
| `optimization_gap` | `(4-3)/4 = 0.25` | `0.25` | `0.0` |
| `hardware_efficiency` | `3/4 = 0.75` | `0.75` | `0.0` |
| Complement sum | `1.0` | `1.0` | `0.0` |

Zero, negative, non-finite, bool, string, object, and `des_bound > actual_time` cases all raise `ValueError`. `SimulationResult` is not an accepted implicit input.

### Unit/resource/traffic corrections

| Check | Expected / Ground Truth | Before | After | Result |
|---|---:|---:|---:|---|
| H100 BF16 chip peak | `4096 * 1830 * 132 = 989,429,760 FLOPs/us` (`989.429760 TFLOPS`) | Validator interpreted `4096 TFLOPS` (`4.1397582381x` high) | `989.429760 TFLOPS` | PASS |
| H100 aggregate L2 | `8,820,000 B/us` | `442,506,240 B/us` effective store capacity (`50.170775510204x` declared) | `8,820,000 B/us` | PASS, delta `0` |
| Legacy one-tile MMA | `512` instructions | `256` | `512` | PASS, delta `0` |
| Cold input example | `524,288 B` unique A+B | `393,216 B` | `524,288 B` | PASS, delta `0` |

### H100 population and supported-policy coverage

| Metric | Actual |
|---|---:|
| H100 rows | `10,800` |
| Rows matching the modeled launch policy | `4,246` (`39.314814815%`) |
| CTA-grid mismatches | `6,554` (`60.685185185%`) |
| Split-K rows | `437` (`437/437` explicitly unsupported; overlaps CTA mismatch) |
| Maximum reconstructed grid among supported rows | `132` CTAs |
| Exhaustive categories | Large `4,231`; Medium `1,798`; Small `3,562`; Other `1,209`; total `10,800` |

### Matched sampled tightness and validity

| Category | Sampled | Evaluated | Unsupported | DES Violations | Both Valid | DES Tighter | Classical Tighter | Equal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Large | 200 | 24 | 176 CTA mismatch | 0 | 24 | 24 | 0 | 0 |
| Medium | 100 | 83 | 17 CTA mismatch | 0 | 83 | 80 | 0 | 3 |
| Small | 100 | 62 | 31 CTA mismatch + 7 split-K | 4 | 58 | 1 | 29 | 28 |
| Other | 100 | 26 | 74 CTA mismatch | 0 | 26 | 26 | 0 | 0 |

This is scoped sample evidence. It supports Large/Medium/Other positive behavior and directly rejects an unrestricted global tighter-than-classical claim.

### Absolute time and error scales

| Category | Mean Actual (us) | Mean DES (us) | Mean Classical (us) | DES MAE (us) | Classical MAE (us) | DES All-row MAPE | Classical All-row MAPE |
|---|---:|---:|---:|---:|---:|---:|---:|
| Large | `39.014666666667` | `31.429699237947` | `29.104068002429` | `7.584967428720` | `9.910598664238` | `25.136598598951%` | `31.453028079252%` |
| Medium | `22.669559036145` | `15.055291025114` | `13.544613414728` | `7.614268011031` | `9.124945621416` | `44.382446381328%` | `50.961102480044%` |
| Small | `13.203912903226` | `9.500076111021` | `9.495655199596` | `3.819359456605` | `3.823780368030` | `38.913601674171%` | `38.987222180839%` |
| Other | `16.843523076923` | `11.099008313674` | `9.963211560753` | `5.744514763249` | `6.880311516171` | `42.470372669348%` | `49.920482043962%` |

Median scales:

| Category | Median Actual (us) | Median DES (us) | Median Classical (us) |
|---|---:|---:|---:|
| Large | `26.267500000000` | `20.607229173637` | `18.638847491307` |
| Medium | `17.218200000000` | `10.880113244861` | `9.554959430369` |
| Small | `8.206700000000` | `5.289957999236` | `5.289957999236` |
| Other | `12.744200000000` | `7.363374506524` | `6.512866368604` |

### Both-valid gap metrics

Unlike all-row MAPE, these gaps exclude any row where either candidate exceeds actual latency.

| Category | DES Mean Gap | Classical Mean Gap | DES Median Gap | Classical Median Gap |
|---|---:|---:|---:|---:|
| Large | `25.136598598951%` | `31.453028079252%` | `24.175%` | `30.047%` |
| Medium | `44.382446381328%` | `50.961102480044%` | `41.570%` | `49.688%` |
| Small | `40.926363100408%` | `41.005060883398%` | `40.553%` | `40.553%` |
| Other | `42.470372669348%` | `49.920482043962%` | `42.182%` | `49.821%` |

### Small bound violations

These rows remain failures of the candidate-bound acceptance gate. They were not clamped, scaled, or silently removed.

| Dataset Index | M | N | K | Tile MxNxK | Actual (us) | DES (us) | Classical (us) | DES Excess (us) | Relative Excess |
|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 23826 | 40 | 4608 | 4096 | 40x64x64 | `10.472800000000` | `11.358228331424` | `11.358228331424` | `0.885428331424` | `8.454552091362%` |
| 30591 | 26 | 4608 | 4096 | 32x64x64 | `10.619200000000` | `11.324016800305` | `11.324016800305` | `0.704816800305` | `6.637193011766%` |
| 25485 | 6 | 8192 | 2048 | 8x64x64 | `8.213200000000` | `10.016647575410` | `10.016647575410` | `1.803447575410` | `21.957916225228%` |
| 24198 | 96 | 4096 | 4096 | 48x64x64 | `10.056400000000` | `10.243909889271` | `10.243909889271` | `0.187509889271` | `1.864582646580%` |

The evidence establishes an unmatched candidate/measurement contract. It does **not** by itself prove warm-L2 residency or isolate cache state from greedy scheduling, kernel policy, output visibility, or measurement provenance.

### Validator runtime

| Category | Mean Runtime (s) | Median (s) | P95 (s) | Max (s) |
|---|---:|---:|---:|---:|
| Large | `0.015694263` | `0.014895156` | `0.017739527` | `0.029963014` |
| Medium | `0.014160245` | `0.014464374` | `0.015256200` | `0.020373815` |
| Small | `0.011012532` | `0.010503474` | `0.014568596` | `0.022784104` |
| Other | `0.014627369` | `0.014761805` | `0.015135437` | `0.015664057` |

The sampled supported rows have small reconstructed grids. This does not erase the earlier scalability observation: a reviewed `58,467`-event Large GEMM took `115.882818766s`. No named cycle-accurate runtime is available, so a `10000x` ratio cannot be computed.

### Small resource/traffic WATCH comparison

The exact same `100` supported Small rows (`random_state=42`) were evaluated under:

- old-equivalent contract: unique B divided by reuse, `num_sms` L2 lanes, store charged with DRAM coefficient;
- revised contract: cold unique A+B, one chip-wide L2 lane, store charged with L2 coefficient.

| Metric | Old Equivalent | Revised | Delta / Interpretation |
|---|---:|---:|---|
| Mean actual (us) | `13.792804000000` | same rows | reference |
| Mean candidate (us) | `8.654575482592` | `9.962412046531` | `+1.307836563939 us` |
| Mean per-row increase | — | `40.262000853904%` | candidate became tighter/larger |
| Maximum increase | — | `195.419957441241%` | shape-dependent effect |
| Violations | `6` | `8` | `+2`; universal bound still fails |
| MAPE | `46.221247450098%` | `34.607057135215%` | improved `11.614190314883` percentage points |

The old model violated its declared cold traffic and aggregate capacity. The revised model is more physically consistent and has lower aggregate error, but neither fact certifies a bound on every measured Small row.

### Scheduler counterexample

| Same Event DAG | Makespan | Difference from best observed ordering |
|---|---:|---:|
| `long-first` | `21.0` | `+10.0` (`+90.909091%` relative to `11.0`) |
| `short-first` | `11.0` | `0.0` |

Only non-semantic input order changed. Therefore the current greedy makespan is a feasible-schedule result, not a certified theoretical lower-bound evaluator.

### Cross-hardware construction smoke

All checked-in files passed:

| Metric | Expected | Actual | Result |
|---|---:|---:|---|
| Hardware JSON files | `11` | `11` | PASS |
| Calibration coefficients per hardware | `22` | `22` | PASS |
| Known operator resource configs per hardware | `5` | `5` | PASS |
| GEMM/GEMM-v2 L2 lanes | `1` chip-wide | `1` on all `11` hardware files | PASS |

This proves constructibility of the specification-driven path. It does not prove held-out zero-shot accuracy.

## 4. Failures Encountered and Root-cause Resolution

### Expected TDD RED failures

All RED failures in the TDD matrix were deliberately introduced before their corresponding implementation change. Each was resolved at root cause and rerun to GREEN; none remains in the final suite.

### Environment timing command

- **Failure:** `/usr/bin/time: No such file or directory` before the first baseline test.
- **Root cause:** GNU `time` is absent; this is an environment-command issue, not a repository failure.
- **Resolution:** Used Bash's verified `time` keyword from `task_memory/env_handbook.md`.
- **Final evidence:** Targeted, full, compile, and validator timings all completed with exit `0`.

### pandas row integer promotion

- **Failure:** Validator unit tests rejected values read by `pandas.iterrows()` because integer columns were promoted to integer-valued floating-point numbers.
- **Root cause:** The validator equated Python `int` representation with integer semantics.
- **Resolution:** Accept finite integer-valued real numbers while rejecting fractional, bool, NaN, and infinity values.
- **Final evidence:** Validator unit suite `11/11`; full suite `131/131`.

### First all-hardware smoke invocation

- **Failure:** `derive_resource_config()` was initially called with positional `operator_type`, causing the same caller `TypeError` on `11/11` files.
- **Root cause:** `operator_type` is keyword-only.
- **Resolution:** Re-ran with `operator_type=name`; no repository code changed.
- **Final evidence:** `11/11` hardware files, `22/22` coefficients, `5/5` configs.

### Final smoke assertion API typo

- **Failure:** The first final smoke command called nonexistent `ResourceConfig.capacity(...)`, raising `AttributeError`.
- **Root cause:** The assertion used an invented convenience method instead of the documented `capacities` mapping.
- **Resolution:** Re-ran with `config.capacities["l2_bandwidth"]`; no repository code changed.
- **Final evidence:** All `11` files passed the corrected assertion.

No final code, regression, compilation, validator, or artifact failure remains.

## 5. Scientific Claim Matrix

| Design Goal | Result | Evidence-based Verdict |
|---|---|---|
| Tighter than traditional roofline | Large `24/24`, Medium `80/83`, Other `26/26` sampled both-valid rows favor DES; Small only `1/58`, with `29` classical tighter, `28` equal, and `4` violations | **PARTIAL locally / UNPROVEN globally** |
| `10000x` faster than cycle-accurate | No named matched comparator; current scheduler also has a large-DAG scalability risk | **UNPROVEN** |
| More interpretable than ML | Explicit events, work, resources, timeline, and selected critical path; no learned latency closure | **ESTABLISHED structurally / Experimental scientifically** |
| Cross-hardware zero-shot | `11/11` hardware specs construct, but no held-out accuracy protocol exists | **UNPROVEN** |
| Optimization-gap API | Exact bounded contract, direct/factory invariants, invalid cases rejected | **PASS for externally accepted bounds** |
| Universal theoretical lower bound | `21.0` vs `11.0` order counterexample, launch-policy limits, and four Small violations | **BLOCKED** |

## 6. Final Test Verdict

The bounded code and documentation remediation is **PASS / APPROVE WITH WATCH**. It is suitable for delivery as an honest mechanistic prototype with a separate bounded comparison API.

The broad DES Refined Roofline scientific claim is **not accepted**. Global tightness, `10000x`, empirical zero-shot, and universal theoretical-bound status remain explicit open research/architecture work. No scaling factor, clamp, fallback, silent skip, cache-state guess, or unsupported scientific promotion was introduced.
