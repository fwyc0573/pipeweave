"""Convert hardware specification JSON into DES-ready configurations.

Provides:
- HardwareConfig: frozen dataclass holding parsed hardware parameters
- load_hardware_config: parse a hardware JSON file
- derive_resource_config: produce ResourceConfig for a given operator context
- derive_calibration: produce PrimitiveCalibration from peak hardware rates
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from .resources import PrimitiveCalibration, ResourceConfig


@dataclass(frozen=True)
class HardwareConfig:
    """Parsed GPU hardware specification."""

    name: str
    num_sms: int
    sm_freq_mhz: float
    mem_bandwidth_gb_s: float
    l2_cache_bandwidth_gb_s: float
    l2_cache_size_kb: int
    shared_memory_size_kb: int
    shared_memory_bandwidth: float
    tc_bf16: float
    tc_fp8: float
    xu_fp32: float
    fma_fp32: float
    architecture: str
    total_global_mem_bytes: int = 0
    register_file_size_kb: int = 256
    l1_cache_size_kb: int = 256

    @property
    def mem_bandwidth_bytes_per_us(self) -> float:
        """HBM bandwidth in bytes per microsecond."""
        return self.mem_bandwidth_gb_s * 1e9 / 1e6  # GB/s -> B/us

    @property
    def l2_bandwidth_bytes_per_us(self) -> float:
        """L2 cache bandwidth in bytes per microsecond."""
        return self.l2_cache_bandwidth_gb_s * 1e9 / 1e6

    @property
    def l2_cache_size_bytes(self) -> int:
        """L2 cache size in bytes."""
        return self.l2_cache_size_kb * 1024

    @property
    def tc_bf16_ops_per_us(self) -> float:
        """Tensor core BF16 operations per microsecond (chip-wide)."""
        return self.tc_bf16 * 1e12 / 1e6  # TFLOPS -> FLOP/us

    @property
    def tc_bf16_mma_per_us(self) -> float:
        """Tensor core MMA instructions per microsecond (chip-wide).
        Each MMA instruction computes 256 FLOPs (16x16x1 warp-level)."""
        return self.tc_bf16_ops_per_us / 256.0

    @property
    def fma_fp32_ops_per_us(self) -> float:
        """FMA FP32 operations per microsecond (chip-wide)."""
        return self.fma_fp32 * 1e12 / 1e6

    @property
    def xu_fp32_ops_per_us(self) -> float:
        """XU (special function) FP32 operations per microsecond (chip-wide)."""
        return self.xu_fp32 * 1e12 / 1e6


def load_hardware_config(json_path: str | Path) -> HardwareConfig:
    """Load a hardware specification from a JSON file."""
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"hardware config not found: {path}")
    with open(path) as f:
        data = json.load(f)
    return HardwareConfig(
        name=data["name"],
        num_sms=data["numSms"],
        sm_freq_mhz=float(data["smFreq"]),
        mem_bandwidth_gb_s=float(data["memBandwidth"]),
        l2_cache_bandwidth_gb_s=float(data["l2CacheBandwidth"]),
        l2_cache_size_kb=int(data["l2CacheSize"]),
        shared_memory_size_kb=int(data.get("sharedMemorySize", 0)),
        shared_memory_bandwidth=float(data.get("sharedMemoryBandwidth", 0)),
        tc_bf16=float(data["tcBf16"]),
        tc_fp8=float(data.get("tcFp8", 0)),
        xu_fp32=float(data.get("xuFp32", 0)),
        fma_fp32=float(data.get("FmaFp32", 0)),
        architecture=data.get("architecture", "unknown"),
        total_global_mem_bytes=int(data.get("totalGlobalMem", 0)),
        register_file_size_kb=int(data.get("registerFileSize", 256)),
        l1_cache_size_kb=int(data.get("l1CacheSize", 256)),
    )


def derive_resource_config(
    hw: HardwareConfig, *, operator_type: str = "gemm"
) -> ResourceConfig:
    """Derive a ResourceConfig appropriate for the given operator type.

    Resource model:
    - Compute (tensor_core, alu, sfu): num_sms lanes — PER-SM parallelism
    - Memory bandwidth (dram, l2): 1 lane — chip-wide shared pool
      (events are summed into one bandwidth bottleneck by the scheduler)
    - SM slots: num_sms lanes — CTA admission parallelism
    """
    if operator_type in ("gemm", "gemm_v2"):
        return ResourceConfig(
            {
                "launch": 1,
                "sm": hw.num_sms,
                "tensor_core": hw.num_sms,
                "dram_bandwidth": 1,
                "l2_bandwidth": 1,
                "global_memory": 1,
                "alu": hw.num_sms,
                "sfu": hw.num_sms,
                "barrier": hw.num_sms,
            }
        )
    elif operator_type == "flash_attention":
        return ResourceConfig(
            {
                "launch": 1,
                "tensor_core": hw.num_sms,
                "dram_bandwidth": 1,
            }
        )
    else:
        return ResourceConfig(
            {
                "launch": 1,
                "sm": hw.num_sms,
                "global_memory": 1,
                "alu": hw.num_sms,
                "sfu": hw.num_sms,
                "barrier": hw.num_sms,
            }
        )


def derive_calibration(hw: HardwareConfig) -> PrimitiveCalibration:
    """Derive primitive duration-per-unit from hardware peak rates.

    All durations are in microseconds.

    Memory bandwidth model: DRAM and L2 bandwidth are CHIP-WIDE shared resources.
    The calibration gives duration per byte at CHIP-WIDE peak rate.
    The ResourceConfig uses a SINGLE lane for each bandwidth pool, so the
    scheduler naturally serializes all memory events into a total bandwidth
    bottleneck. This is the correct roofline model: total_bytes / peak_BW.

    Compute model: Tensor cores are PER-SM resources (one lane per SM in
    ResourceConfig). Each CTA's compute duration = work / per_SM_rate.
    The scheduler places CTA compute events on SM lanes, expressing parallelism.

    For bound validity: peak rates give minimum achievable time.
    """
    num_sms = hw.num_sms

    # Memory: CHIP-WIDE bandwidth (single shared pool)
    dram_us_per_byte = 1.0 / hw.mem_bandwidth_bytes_per_us
    l2_us_per_byte = 1.0 / hw.l2_bandwidth_bytes_per_us

    # Compute: PER-SM throughput (each SM has its own TC pipeline)
    tc_bf16_mma_per_sm_per_us = hw.tc_bf16_mma_per_us / num_sms
    fma_per_sm_per_us = hw.fma_fp32_ops_per_us / num_sms
    xu_per_sm_per_us = hw.xu_fp32_ops_per_us / num_sms

    mma_us_per_instr = 1.0 / tc_bf16_mma_per_sm_per_us if tc_bf16_mma_per_sm_per_us > 0 else 0.0
    fma_us_per_op = 1.0 / fma_per_sm_per_us if fma_per_sm_per_us > 0 else 0.0
    xu_us_per_op = 1.0 / xu_per_sm_per_us if xu_per_sm_per_us > 0 else 0.0

    # Fixed overheads — set to minimum achievable for valid lower bound
    # These represent unavoidable fixed costs, calibrated at peak (fastest) rate
    kernel_launch_us = 0.5
    kernel_complete_us = 0.01
    cta_admission_us = 0.005
    barrier_us = 0.02

    return PrimitiveCalibration(
        {
            # Kernel lifecycle
            "KernelLaunch": kernel_launch_us,
            "KernelComplete": kernel_complete_us,
            # CTA admission
            "CTAAdmission": cta_admission_us,
            "CTAAdmission_FullWave": cta_admission_us,
            "CTAAdmission_TailWave": cta_admission_us,
            # Memory — cache-aware splits
            "GlobalLoad": dram_us_per_byte,
            "GlobalLoad_L2Hit": l2_us_per_byte,
            "GlobalLoad_L2Miss": dram_us_per_byte,
            "GlobalStore": dram_us_per_byte,
            # Compute
            "MMA": mma_us_per_instr,
            "MMA_FullTile": mma_us_per_instr,
            "MMA_PartialTile": mma_us_per_instr,
            "MMA_PipelineDrain": mma_us_per_instr,
            "FMA": fma_us_per_op,
            "SFU": xu_us_per_op,
            "Reduction": fma_us_per_op,
            # Synchronization
            "Barrier": barrier_us,
            # Shared memory (approximate)
            "SharedLoad": l2_us_per_byte,
            "SharedStore": l2_us_per_byte,
            # FlashAttention composites
            "FA_Compute": mma_us_per_instr,
            "FA_Memory": dram_us_per_byte,
            "FA_TaskSync": 0.0,
        }
    )
