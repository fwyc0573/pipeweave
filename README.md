# PipeWeave: Synergizing Analytical and Learning Models for Unified GPU Performance Prediction

This repository contains the artifact for the ISCA 2026 paper:

> **PipeWeave: Synergizing Analytical and Learning Models for Unified GPU Performance Prediction**
> arXiv preprint: https://arxiv.org/abs/2601.14910

PipeWeave is a cross-hardware LLM inference latency predictor. It combines roofline-style analytical models with small trained MLPs to predict operator-level and end-to-end latency for transformer workloads on NVIDIA GPUs.

---

## How It Works

For each operator in a workload:
1. An **analytical model** computes hardware pipeline features (tensor pipe, memory pipe, XU pipe, FMA pipe) from the problem config and GPU spec.
2. A trained **MLP** takes those features and predicts `overall_perf` — a normalized efficiency ratio relative to theoretical peak.
3. Actual duration (µs) is derived from `overall_perf` and the theoretical peak throughput.

End-to-end latency is the sum of all per-operator durations.

---

## Repository Structure

```
pipeweave/
├── aggregator.py              # Main entry point: predict e2e latency
├── mlp_model.py               # MLP architecture (MLP, MLP_v2)
├── workload_generator.py      # Generate workload JSON specs
├── train_mlp.py               # Train MLP models on operator data
├── train_mlp_quantile.py      # Quantile regression variant
├── train_collective_rf.py     # Random Forest for collective comms
├── compare_pred_real.py       # Compare predictions vs measurements
├── compare_vllm_pred_real.py  # vLLM-specific comparison
├── tp1.sh / tp2.sh / tp4.sh / tp8.sh   # Batch run scripts
├── vllm_tp4_pp2.sh            # vLLM TP=4 PP=2 run script
│
├── analytical_model/          # Roofline calculators per operator/arch
│   ├── pipes.py               # Shared dataclasses (HardwareSpec, configs)
│   ├── gemm_8_calculator.py   # GEMM for SM80 (Ampere)
│   ├── gemm_9_calculator.py   # GEMM for SM90 (Hopper)
│   ├── gemm_fp8_calculator.py # FP8 GEMM
│   ├── fa2_calculator.py      # Flash Attention 2
│   ├── fa3_calculator.py      # Flash Attention 3
│   ├── rmsnorm_calculator.py
│   ├── silumul_calculator.py
│   └── triton_moe_calculator.py
│
├── hardware/                  # GPU specs (JSON)
├── config/                    # Model architecture configs (JSON)
├── dataset/                   # Profiled operator data (CSV)
├── mlp_models/                # Trained MLP checkpoints
├── mlp_models_quantile/       # Quantile MLP checkpoints
├── workload/                  # Workload JSON specs + trace CSVs
└── e2e/                       # Prediction results & comparisons
```

---

## Setup

```bash
pip install torch numpy pandas scikit-learn joblib
```

No additional installation is required. All scripts run from the repository root.

---

## Quick Start

### Predict end-to-end latency

```bash
python3 aggregator.py \
    --workload workload/Qwen2.5-14B_arxiv_8_fa3_tp1_pp1.json \
    --hardware H100 \
    --model_dir mlp_models \
    --dataset_dir dataset \
    --hardware_dir hardware \
    --output e2e/pipeweave_pred/result.json
```

### Batch runs (all hardware configs)

```bash
bash tp1.sh   # TP=1
bash tp2.sh   # TP=2
bash tp4.sh   # TP=4
bash tp8.sh   # TP=8
```

---

## Workflow

### 1. Generate a workload spec

```bash
python3 workload_generator.py
```

Outputs a JSON file under `workload/` describing per-layer operator sequences for a given model, parallelism config, and request trace.

Workload file naming convention:
```
{MODEL}_{TRACE}_{SEQLEN}_{FA_VERSION}_tp{TP}_pp{PP}.json
```

### 2. Train MLP models

```bash
python3 train_mlp.py
```

Reads profiled operator data from `dataset/`, trains one MLP per operator type (GEMM, Attention, RMSNorm, SiLU×Mul), and saves checkpoints to `mlp_models/`.

### 3. Run predictions

```bash
python3 aggregator.py --workload <workload.json> --hardware <GPU_NAME> ...
```

### 4. Compare against ground truth

```bash
python3 compare_pred_real.py
```

Generates comparison CSVs under `e2e/` with MAPE and other accuracy metrics against real profiling data and baselines (Roofline, Habitat, NeuSight, vLLM).

---

## Experimental Event-Level Simulator

The `des` branch also contains an independent research MVP under
`event_simulator/`. Unlike the existing analytical-plus-ML path, this simulator
does not use MLP/RF predictions to close the final latency equation. It lowers
supported operators into explicit events and derives duration from dependencies,
resource capacity, and caller-supplied primitive calibration.

```python
from event_simulator import (
    PrimitiveCalibration,
    ResourceConfig,
    build_report,
    lower_silu_and_mul,
    schedule,
)

calibration = PrimitiveCalibration(
    {
        "KernelLaunch": 0.5,
        "GlobalLoad": 0.001,
        "SFU": 0.002,
        "FMA": 0.001,
        "GlobalStore": 0.001,
        "KernelComplete": 0.1,
    }
)
resources = ResourceConfig(
    {"launch": 1, "global_memory": 2, "sfu": 1, "alu": 2}
)
events = lower_silu_and_mul(
    "silu-0", elements=4096, calibration=calibration
)
report = build_report(schedule(events, resources))
print(report.to_dict())
```

All calibration values must use one consistent time unit; microseconds are
recommended. Missing calibration and unknown resources fail immediately. The
MVP supports a single device plus GEMM, RMSNorm, and SiLU-and-Mul lowering. It
does not yet model attention, cache hierarchy, warp scheduling, NCCL, pipeline
parallel timing, or online request scheduling.

See [`docs/event_simulator_design.md`](docs/event_simulator_design.md) for the
codebase analysis, measurement boundary, architecture, risks, and staged plan.

---

## Supported Hardware

| GPU | Architecture |
|-----|-------------|
| A100 | Ampere |
| A40 | Ampere |
| H100 | Hopper |
| H800 | Hopper |
| H200 | Hopper |
| H20 | Hopper |
| L20 | Ada |
| L40 | Ada |
| RTX A6000 | Ampere |
| RTX 6000 Ada | Ada |
| RTX PRO 6000 S | Blackwell |

---

## Supported Models

| Model | Config file |
|-------|------------|
| Llama-3-8B | `config/Llama-3-8B.json` |
| Llama-3-70B | `config/Llama-3-70B.json` |
| Llama-3.1-8B | `config/Llama-3.1-8B.json` |
| Llama-3.1-70B | `config/Llama-3.1-70B.json` |
| Qwen2-72B | `config/Qwen2-72B.json` |
| Qwen2.5-14B | `config/Qwen2.5-14B.json` |
| Qwen2.5-32B | `config/Qwen2.5-32B.json` |
| Qwen3-14B | `config/Qwen3-14B.json` |
| Qwen3-32B | `config/Qwen3-32B.json` |

---

## Citation

If you use this work, please cite:

```bibtex
@article{pipeweave2026,
  title   = {PipeWeave: Synergizing Analytical and Learning Models for Unified GPU Performance Prediction},
  author  = {Kaixuan Zhang and Yunfan Cui and Shuhao Zhang and Chutong Ding and Shiyou Qian and Luping Wang and Jian Cao and Guangtao Xue and Cheng Huang and Guodong Yang and Liping Zhang},
  journal = {arXiv preprint},
  year    = {2026},
  url     = {https://arxiv.org/abs/2601.14910}
}
```

> Note: The full ISCA 2026 citation will be updated upon publication.
