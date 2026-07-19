# Test Report: Wave-2 Exact Oracle and SafeBound Proof Layer

## Modification History

| Date | Summary of Changes |
|---|---|
| 2026-07-20 | Added the interruption-recovery pre-commit verification with fresh numeric regression, proof-audit, and benchmark evidence. |
| 2026-07-20 | Added the final fresh handoff verification and closed the Wave-2 gate. |
| 2026-07-20 | Added the independent StepCode Claude APPROVE verdict and its reconciled non-blocking observations. |
| 2026-07-20 | Recorded the complete RED/GREEN sequence, exhaustive independent oracle audit, search benchmark, static checks, and numeric proof evidence. |

**Date:** 2026-07-20

**Repository:** `/data/ycfeng/pipeweave/.worktrees/des`

**Branch:** `des`

**Environment:** no active conda environment; no active virtual environment;
Python `3.12.3`; pytest `9.1.1`; Linux `5.10.25-nvidia-gpu x86_64`

## 1. Test Script Information

### Production modules under test

- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/events.py`
- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/resources.py`
- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/scheduler.py`
- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/exact_oracle.py`
- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/safe_bound.py`
- `/data/ycfeng/pipeweave/.worktrees/des/event_simulator/__init__.py`

### Unit, validation, and performance scripts

- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_event_graph.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_resource_semantics.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_exact_oracle.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/exact_time_grid_reference.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound_permutation_properties.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/unit/test_safe_bound_conservation_properties.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/validation/validate_safe_bound_exact_oracle.py`
- `/data/ycfeng/pipeweave/.worktrees/des/tests/performance/benchmark_exact_oracle.py`

### Generated proof evidence

- `/data/ycfeng/pipeweave/.worktrees/des/task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/formal_bound_contract.md`
- `/data/ycfeng/pipeweave/.worktrees/des/task_memory/task_2026-07-20_des_full_semantics_and_scientific_validation/safe_bound_oracle_cases.json`

### Reproducible commands

#### Focused Wave-2 suite

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
python -m pytest -p no:cacheprovider \
  tests/unit/test_exact_oracle.py \
  tests/unit/test_safe_bound.py \
  tests/unit/test_safe_bound_permutation_properties.py \
  tests/unit/test_safe_bound_conservation_properties.py -q
```

#### Wave-1 plus Wave-2 regression

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
python -m pytest -p no:cacheprovider \
  tests/unit/test_event_graph.py \
  tests/unit/test_resource_semantics.py \
  tests/unit/test_exact_oracle.py \
  tests/unit/test_safe_bound.py \
  tests/unit/test_safe_bound_permutation_properties.py \
  tests/unit/test_safe_bound_conservation_properties.py -q
```

#### Independent exhaustive time-grid validation

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
python tests/validation/validate_safe_bound_exact_oracle.py
```

#### Exact-search scaling and budget failure

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" \
python tests/performance/benchmark_exact_oracle.py
```

#### Static/diff checks

```bash
PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
import ast
from pathlib import Path

paths = [
    Path("event_simulator/exact_oracle.py"),
    Path("event_simulator/safe_bound.py"),
    Path("event_simulator/scheduler.py"),
    Path("tests/validation/validate_safe_bound_exact_oracle.py"),
]
for path in paths:
    ast.parse(path.read_text(), filename=str(path))
print(f"parsed_python_files={len(paths)}")
PY
git diff --check -- . ':(exclude)=10.1'
```

The repository has no configured `pyproject.toml`, `setup.cfg`, `tox.ini`, or
`.flake8`; `ruff`, `black`, `mypy`, and `pyright` are not installed in this
environment. The task therefore uses AST parsing, the established added-line
length audit, pytest, generated property evidence, and `git diff --check`.

## 2. Validation Criteria

### Exact-oracle acceptance

1. Public `ScheduleEntry`, `ExactScheduleResult`,
   `IncompleteExactSearchError`, and `solve_exact_schedule` are available.
2. `ExactScheduleResult` and its entries are immutable.
3. Every returned result follows complete enumeration of all
   precedence-feasible permutations; no pruning or best-known fallback exists.
4. The result matches an independent bounded integer start-assignment oracle.
5. Global and one-SM per-SM demand are admitted atomically across all resources.
6. Zero-duration Events occupy no resource-time under `[start, end)`.
7. Resource lifetimes, affinity, and multi-SM nonzero per-SM demand fail fast.
8. Search-budget exhaustion returns no exact result.

### SafeBound acceptance

1. `bound` equals the maximum of dependency critical path, every chip-global
   resource-time/capacity term, and every aggregate per-SM term.
2. Result and term mappings are immutable and canonically ordered.
3. Affinity and lifetime reservation omissions are explicitly named.
4. Input permutation does not alter any bound or term evidence.
5. Increasing declared duration or demand does not reduce the bound under a
   fixed policy/configuration.
6. Every accepted generated case satisfies `SafeBound <= exact optimum`.
7. No scheduler, measured-hardware, or comparison certification is implicit.

### Numeric acceptance thresholds

| Metric | Acceptance criterion |
|---|---:|
| Focused Wave-2 unit tests | `76/76` pass; `0` warnings |
| Wave-1+2 regression | `152/152` pass |
| Independent oracle cases | all accepted; exact mismatches `0` |
| Exact comparison error | maximum absolute delta `0.0` |
| SafeBound safety | violations `0`; minimum `exact - bound >= 0.0` |
| Permutation invariance | mismatches `0` |
| Conservation | failures `0` |
| Monotonicity | failures `0` |
| Budget exhaustion | explicit incomplete error; no result |
| Static checks | four changed modules parse; added long lines `0`; diff errors `0` |

## 3. Test Results and Evidence

### RED evidence before production implementation

The corrected Wave-2 tests were run before the new proof-layer production
code existed.

| Metric | Expected | Actual |
|---|---:|---:|
| Collected focused cases | 76 | 76 |
| Ordinary failures | 76 | 76 |
| Collection errors | 0 | 0 |
| Warnings | 0 | 0 |
| Exit code | 1 | 1 |
| Pytest time | recorded | `1.29s` |
| Wrapper elapsed | recorded | `1.684990352s` |

Failures were caused by absent `ExactScheduleResult`, `ScheduleEntry`,
`solve_exact_schedule`, and `IncompleteExactSearchError`, plus the old
single-argument SafeBound evaluator. They were not collection failures or
arithmetic-test defects.

### Test-side defects corrected before production work

| Defect | Incorrect value/behavior | Correct value/behavior | Production delta |
|---|---|---|---|
| Lazy parametrization | `itertools.product` passed directly | materialized tuple; no pytest deprecation warning | none |
| Exact permutation optimum | `5.0` | short `0–2`, long `2–6`, tail `2–5`; optimum `6.0` | none |
| Critical path | `8.0` | independent duration-`10` Event makes CP `10.0` | none |

### GREEN sequence

| Suite / phase | Result | Passed | Failed | Time | Exit code |
|---|---|---:|---:|---:|---:|
| Exact oracle only | PASS | 24 | 0 | `0.84s` | 0 |
| First SafeBound attempt | FAIL | 48 | 4 | `0.85s` | 1 |
| SafeBound after root-cause fix | PASS | 52 | 0 | `0.82s` | 0 |
| Combined Wave-2 focused | PASS | 76 | 0 | `0.93s` | 0 |
| Wave-1+2 regression | PASS | 152 | 0 | `1.06s` | 0 |

The first SafeBound attempt failed only when both resource-term mappings were
empty. `max(critical_path, *empty_terms)` became the iterable-form call
`max(float)`. The fix passes one tuple containing every proof term to `max`;
it adds no special-case branch, fallback, clamp, or compatibility behavior.

### Independent exact and safety matrix

The independent reference enumerated bounded integer start assignments and did
not call serial SGS.

| Metric | Expected | Actual | Delta / Failure count |
|---|---:|---:|---:|
| Oracle cases | 4,725 | 4,725 passed | 0 failed |
| Exact optimum matches | 4,725 | 4,725 | 0 mismatches |
| Maximum absolute exact error | `0.0` | `0.0` | `0.0` |
| Minimum `exact - SafeBound` | `>= 0.0` | `0.0` | 0 violations |
| Input permutations | 28,350 | 28,350 checked | 0 mismatches |
| Resource conservation | 4,725 cases | all checked | 0 failures |
| Monotonicity comparisons | 18,360 | 18,360 checked | 0 failures |

Generated evidence details:

| Evidence metric | Actual value |
|---|---|
| JSON size | `472,855` bytes |
| Case records | `4,725` |
| Group summaries | `10` |
| Case-record SHA-256 | `5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67` |
| Validation internal elapsed | `4.033141780s` |
| Validation wrapper elapsed | `4.117413640s` |
| Exit code | `0` |

Representative expected-versus-actual values:

| Case | Expected optimum | Exact result | Absolute delta | SafeBound | `exact - bound` |
|---|---:|---:|---:|---:|---:|
| All-zero independent, capacity 1 | `0.0` | `0.0` | `0.0` | `0.0` | `0.0` |
| Short/long/tail resource interaction | `6.0` | `6.0` | `0.0` | `6.0` | `0.0` |
| Multi-SM placement counterexample | true placed `2.0` | exact oracle rejects unsupported placement | N/A | `1.0` | true-minus-bound `1.0` (`50%`) |
| Capacity-2 chain-plus-independent `d=222`, `q=222` | `6.0` | `6.0` | `0.0` | `6.0` | `0.0` |

### Exact-search benchmark

All completed cases returned the expected makespan with absolute delta `0.0`.

| Case | Events | Edges | Resources | Complete permutations | Expected | Actual | Delta | Runtime |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| independent-1 | 1 | 0 | 0 | 1 | `1.0` | `1.0` | `0.0` | `0.000036768s` |
| independent-2 | 2 | 0 | 0 | 2 | `1.0` | `1.0` | `0.0` | `0.000047632s` |
| independent-3 | 3 | 0 | 0 | 6 | `1.0` | `1.0` | `0.0` | `0.000116842s` |
| independent-4 | 4 | 0 | 0 | 24 | `1.0` | `1.0` | `0.0` | `0.000309468s` |
| independent-5 | 5 | 0 | 0 | 120 | `1.0` | `1.0` | `0.0` | `0.001869168s` |
| independent-6 | 6 | 0 | 0 | 720 | `1.0` | `1.0` | `0.0` | `0.012246391s` |
| independent-7 | 7 | 0 | 0 | 5,040 | `1.0` | `1.0` | `0.0` | `0.095154976s` |
| independent-8 | 8 | 0 | 0 | 40,320 | `1.0` | `1.0` | `0.0` | `0.854807379s` |
| independent-9 | 9 | 0 | 0 | 362,880 | `1.0` | `1.0` | `0.0` | `8.757123135s` |
| resource-serial-8 | 8 | 0 | 1 | 40,320 | `8.0` | `8.0` | `0.0` | `5.286754904s` |
| chain-128 | 128 | 127 | 0 | 1 | `128.0` | `128.0` | `0.0` | `0.001141802s` |

Budget behavior:

| Case | Events | Total possible permutations | Budget | Result returned | Status | Runtime |
|---|---:|---:|---:|---|---|---:|
| budget-exhaustion-9 | 9 | 362,880 | 1,000 | no | `IncompleteExactSearchError` | `0.023271485s` |

The complete benchmark exited `0`; wrapper elapsed was `15.109415953s`. The
measurements demonstrate factorial dependence on the number of feasible Event
orders and do not establish a default production cutoff.

### Static and artifact checks

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Changed proof/performance Python files parsed | 4 | 4 | PASS |
| Newly added Python lines over 88 characters | 0 | 0 | PASS |
| `git diff --check` errors | 0 | 0 | PASS |
| Generated JSON parse | success | 4,725 cases, 15 fields, 10 groups | PASS |

## 4. Result

**Test status: PASS.** The exact-oracle and SafeBound implementation meets the
Wave-2 unit, independent-oracle, safety, invariance, conservation,
monotonicity, budget-failure, performance-evidence, and static-validation
criteria. StepCode Claude independently returned **APPROVE** with no blocker;
its endpoint-proof, deterministic-sort, tuple-`max`, and integer-subdomain
observations were reconciled without adding speculative code. The final fresh
handoff passed `152/152` tests, `4,725/4,725` independent cases, `17/17`
artifact checks, digest verification, the added-line audit, and
`git diff --check`. Wave 2 is closed.

## 5. Claim Boundary

These results establish the declared fixed-duration modeled proof contract
only. They do not establish silicon cycle accuracy, Hopper equivalence,
measured-hardware safety, universal physical lower-bound validity, or a
`10000x` runtime claim.

## 6. Interruption-Recovery Pre-Commit Verification

The reviewed Wave-1/2 checkpoint was verified again immediately before its
stage commit and push.

| Check | Expected | Actual | Delta / failures | Result |
|---|---:|---:|---:|---|
| Wave-1/2 regression | 152 passed | 152 passed in `0.99s` | 0 failures | PASS |
| Independent oracle corpus | 4,725 cases | 4,725 passed | 0 mismatches / violations | PASS |
| Input permutations | 28,350 | 28,350 checked | 0 mismatches | PASS |
| Monotonicity comparisons | 18,360 | 18,360 checked | 0 failures | PASS |
| Required artifacts | 17 | 17 present | 0 missing | PASS |
| Python AST parse | 15 files | 15 parsed | 0 failures | PASS |
| Added Python lines over 88 characters | 0 | 0 | 0 | PASS |
| `git diff --check` errors | 0 | 0 | 0 | PASS |

Fresh benchmark values remained behaviorally identical to the recorded
expected results:

| Case | Expected makespan | Actual makespan | Absolute delta | Runtime |
|---|---:|---:|---:|---:|
| independent-9 (`9! = 362,880`) | `1.0` | `1.0` | `0.0` | `8.494442112s` |
| resource-serial-8 (`8! = 40,320`) | `8.0` | `8.0` | `0.0` | `5.264503544s` |
| chain-128 | `128.0` | `128.0` | `0.0` | `0.001100687s` |
| budget-exhaustion-9 | no exact result | `IncompleteExactSearchError` | N/A | `0.033102431s` |

The regression wrapper elapsed `1.367510628s`, validation wrapper elapsed
`4.134851064s`, and complete benchmark wrapper elapsed `14.896103679s`.
The stable digest for the canonical **case records** remained
`5e173514000270d7c5d2a504b1adcd9d62f9285ee6d12819a48397c63724da67`;
the enclosing JSON file also contains run metadata, so its whole-file digest
is intentionally not used as the case-record identity.

The initial staged `git diff --check` reported three trailing-whitespace
errors on the report metadata lines. The root cause was Markdown hard-break
spaces in a previously untracked report, which the earlier unstaged diff did
not include. The spaces were removed rather than suppressing the check; the
final staged validation is the authoritative result.
