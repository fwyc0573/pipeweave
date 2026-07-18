"""FlashAttention3 benchmark for DES validation.

Measures FA3 kernel latency across various configurations on H800.
Outputs CSV with measured durations for comparison against DES predictions.
"""

import torch
import time
import csv
import argparse
from pathlib import Path


def benchmark_fa3(batch_size, seq_len, num_heads, num_kv_heads, head_dim, causal=True, warmup=10, repeats=50):
    """Benchmark FA3 attention kernel and return median latency in microseconds."""
    device = torch.device("cuda")

    q = torch.randn(batch_size, num_heads, seq_len, head_dim, device=device, dtype=torch.bfloat16)
    k = torch.randn(batch_size, num_kv_heads, seq_len, head_dim, device=device, dtype=torch.bfloat16)
    v = torch.randn(batch_size, num_kv_heads, seq_len, head_dim, device=device, dtype=torch.bfloat16)

    # Warmup
    for _ in range(warmup):
        with torch.nn.attention.sdpa_kernel(torch.nn.attention.SDPBackend.FLASH_ATTENTION):
            _ = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=causal)
    torch.cuda.synchronize()

    # Benchmark
    latencies = []
    for _ in range(repeats):
        torch.cuda.synchronize()
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        with torch.nn.attention.sdpa_kernel(torch.nn.attention.SDPBackend.FLASH_ATTENTION):
            _ = torch.nn.functional.scaled_dot_product_attention(q, k, v, is_causal=causal)
        end.record()
        torch.cuda.synchronize()
        latencies.append(start.elapsed_time(end) * 1000)  # ms -> us

    latencies.sort()
    return {
        "min": latencies[0],
        "p5": latencies[int(len(latencies) * 0.05)],
        "median": latencies[len(latencies) // 2],
        "p95": latencies[int(len(latencies) * 0.95)],
        "mean": sum(latencies) / len(latencies),
    }


def main():
    parser = argparse.ArgumentParser(description="FA3 Benchmark for DES Validation")
    parser.add_argument("--output", type=str, default="dataset/fa3_benchmark_h800.csv")
    args = parser.parse_args()

    configs = [
        # (batch_size, seq_len, num_qo_heads, num_kv_heads, head_dim, causal)
        # Prefill scenarios
        (1, 512, 32, 8, 128, True),
        (1, 1024, 32, 8, 128, True),
        (1, 2048, 32, 8, 128, True),
        (1, 4096, 32, 8, 128, True),
        (1, 8192, 32, 8, 128, True),
        (4, 512, 32, 8, 128, True),
        (4, 1024, 32, 8, 128, True),
        (4, 2048, 32, 8, 128, True),
        (4, 4096, 32, 8, 128, True),
        (8, 512, 32, 8, 128, True),
        (8, 1024, 32, 8, 128, True),
        (8, 2048, 32, 8, 128, True),
        # Non-causal
        (1, 2048, 32, 8, 128, False),
        (4, 2048, 32, 8, 128, False),
        # MHA (no GQA)
        (1, 2048, 32, 32, 128, True),
        (4, 2048, 32, 32, 128, True),
        # Different head dims
        (4, 2048, 32, 8, 64, True),
        (4, 2048, 64, 8, 128, True),
        # Decode-like (short q)
        (16, 1, 32, 8, 128, True),
        (32, 1, 32, 8, 128, True),
        (64, 1, 32, 8, 128, True),
    ]

    results = []
    print(f"Running {len(configs)} FA3 benchmark configurations...")
    print(f"{'BS':>4} {'SeqLen':>7} {'QHeads':>7} {'KVHeads':>8} {'HD':>4} {'Causal':>6} {'Median(us)':>11} {'Min(us)':>9}")
    print("-" * 70)

    for bs, seq, qh, kvh, hd, causal in configs:
        try:
            stats = benchmark_fa3(bs, seq, qh, kvh, hd, causal)
            results.append({
                "batch_size": bs,
                "seq_len": seq,
                "num_qo_heads": qh,
                "num_kv_heads": kvh,
                "head_dim": hd,
                "causal": causal,
                "min_us": stats["min"],
                "p5_us": stats["p5"],
                "median_us": stats["median"],
                "p95_us": stats["p95"],
                "mean_us": stats["mean"],
            })
            print(f"{bs:>4} {seq:>7} {qh:>7} {kvh:>8} {hd:>4} {str(causal):>6} {stats['median']:>10.1f} {stats['min']:>8.1f}")
        except Exception as e:
            print(f"{bs:>4} {seq:>7} {qh:>7} {kvh:>8} {hd:>4} {str(causal):>6} FAILED: {e}")

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {output_path} ({len(results)} configs)")


if __name__ == "__main__":
    main()
