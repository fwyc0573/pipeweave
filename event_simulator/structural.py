"""Structural split analysis for DES event decomposition.

Pure analytical functions that compute structural parameters used to
decompose operators into finer-grained events. Each function computes
a deterministic split ratio from static kernel/hardware properties.
"""

from __future__ import annotations


def ceil_div(x: int, y: int) -> int:
    """Integer ceiling division."""
    return (x + y - 1) // y


def compute_wave_split(
    total_ctas: int, num_sms: int, max_ctas_per_sm: int = 1
) -> tuple[int, int]:
    """Split CTA count into full-wave and tail-wave portions.

    Returns (full_wave_ctas, tail_wave_ctas) where:
    - full_wave_ctas: CTAs in complete waves that fully utilize all SMs
    - tail_wave_ctas: remaining CTAs in the final partial wave

    The tail wave has reduced SM utilization: only tail_wave_ctas SMs
    are active while the rest idle.
    """
    if total_ctas <= 0 or num_sms <= 0 or max_ctas_per_sm <= 0:
        raise ValueError("all arguments must be positive")
    ctas_per_wave = num_sms * max_ctas_per_sm
    full_waves = total_ctas // ctas_per_wave
    full_wave_ctas = full_waves * ctas_per_wave
    tail_wave_ctas = total_ctas - full_wave_ctas
    return full_wave_ctas, tail_wave_ctas


def compute_l2_hit_ratio(
    working_set_bytes: int,
    l2_cache_bytes: int,
    concurrent_ctas: int,
) -> float:
    """Estimate L2 cache hit ratio from structural parameters.

    Uses a continuous formula: effective_capacity / max(capacity, working_set).
    This ensures monotonic decrease as working set grows (no discontinuity).

    This is an analytical hit-ratio estimate only. Callers must declare the
    cache-state and traffic boundary independently; this helper does not certify
    a composed schedule as a latency lower bound.

    Returns a float in [0.0, 1.0] representing the fraction of global
    loads that hit in L2 cache.
    """
    if working_set_bytes <= 0 or l2_cache_bytes <= 0 or concurrent_ctas <= 0:
        return 0.0

    effective_l2_per_cta = l2_cache_bytes / concurrent_ctas
    ratio = effective_l2_per_cta / max(effective_l2_per_cta, float(working_set_bytes))
    return max(0.0, min(1.0, ratio))


def compute_tile_efficiency(
    m: int, n: int, tile_m: int, tile_n: int
) -> dict:
    """Compute full vs partial tile decomposition.

    Returns a dict with:
    - full_tile_count: number of tiles that are completely utilized
    - partial_tile_count: number of edge tiles with wasted compute
    - full_tile_mma_ops_factor: relative work factor for full tiles (1.0)
    - partial_tile_avg_efficiency: average utilization of partial tiles [0,1]
    """
    if m <= 0 or n <= 0 or tile_m <= 0 or tile_n <= 0:
        raise ValueError("all dimensions must be positive")

    m_tiles = ceil_div(m, tile_m)
    n_tiles = ceil_div(n, tile_n)
    total_tiles = m_tiles * n_tiles

    # Full tiles: interior tiles with complete dimensions
    m_has_partial = (m % tile_m) != 0
    n_has_partial = (n % tile_n) != 0

    full_m_tiles = m_tiles - (1 if m_has_partial else 0)
    full_n_tiles = n_tiles - (1 if n_has_partial else 0)
    full_tile_count = full_m_tiles * full_n_tiles
    partial_tile_count = total_tiles - full_tile_count

    # Compute average efficiency of partial tiles
    if partial_tile_count > 0:
        m_remainder = m % tile_m if m_has_partial else tile_m
        n_remainder = n % tile_n if n_has_partial else tile_n

        # Corner tile: m_remainder × n_remainder
        # Edge-m tiles: m_remainder × tile_n (full_n_tiles of them)
        # Edge-n tiles: tile_m × n_remainder (full_m_tiles of them)
        total_useful = 0
        total_padded = 0

        if m_has_partial and n_has_partial:
            # Corner tile
            total_useful += m_remainder * n_remainder
            total_padded += tile_m * tile_n
        if m_has_partial:
            # Bottom edge (excluding corner)
            total_useful += full_n_tiles * m_remainder * tile_n
            total_padded += full_n_tiles * tile_m * tile_n
        if n_has_partial:
            # Right edge (excluding corner)
            total_useful += full_m_tiles * tile_m * n_remainder
            total_padded += full_m_tiles * tile_m * tile_n

        avg_efficiency = total_useful / total_padded if total_padded > 0 else 1.0
    else:
        avg_efficiency = 1.0

    return {
        "full_tile_count": full_tile_count,
        "partial_tile_count": partial_tile_count,
        "total_tiles": total_tiles,
        "full_tile_mma_ops_factor": 1.0,
        "partial_tile_avg_efficiency": avg_efficiency,
    }


def is_edge_tile(
    cta_index: int, m_tiles: int, n_tiles: int, m: int, n: int, tile_m: int, tile_n: int
) -> bool:
    """Determine if a CTA (by flat index) is an edge/partial tile."""
    row = cta_index // n_tiles
    col = cta_index % n_tiles
    m_has_partial = (m % tile_m) != 0
    n_has_partial = (n % tile_n) != 0
    return (m_has_partial and row == m_tiles - 1) or (n_has_partial and col == n_tiles - 1)


def compute_actual_tile_dims(
    cta_index: int, m: int, n: int, tile_m: int, tile_n: int, n_tiles: int
) -> tuple[int, int]:
    """Compute the actual (clamped) dimensions of a specific tile."""
    row = cta_index // n_tiles
    col = cta_index % n_tiles
    actual_m = min(tile_m, m - row * tile_m)
    actual_n = min(tile_n, n - col * tile_n)
    return actual_m, actual_n
