"""Tests for event_simulator.structural."""

import pytest

from event_simulator.structural import (
    ceil_div,
    compute_actual_tile_dims,
    compute_l2_hit_ratio,
    compute_tile_efficiency,
    compute_wave_split,
    is_edge_tile,
)


class TestCeilDiv:
    def test_exact_division(self):
        assert ceil_div(256, 128) == 2

    def test_remainder(self):
        assert ceil_div(300, 128) == 3

    def test_one(self):
        assert ceil_div(1, 128) == 1


class TestComputeWaveSplit:
    def test_exact_multiple_of_sms(self):
        full, tail = compute_wave_split(264, num_sms=132, max_ctas_per_sm=1)
        assert full == 264
        assert tail == 0

    def test_one_tail_cta(self):
        full, tail = compute_wave_split(133, num_sms=132, max_ctas_per_sm=1)
        assert full == 132
        assert tail == 1

    def test_large_tail_wave(self):
        full, tail = compute_wave_split(200, num_sms=132, max_ctas_per_sm=1)
        assert full == 132
        assert tail == 68

    def test_multi_cta_per_sm(self):
        full, tail = compute_wave_split(300, num_sms=132, max_ctas_per_sm=2)
        assert full == 264
        assert tail == 36

    def test_fewer_ctas_than_sms(self):
        full, tail = compute_wave_split(50, num_sms=132, max_ctas_per_sm=1)
        assert full == 0
        assert tail == 50

    def test_raises_on_non_positive(self):
        with pytest.raises(ValueError):
            compute_wave_split(0, 132, 1)
        with pytest.raises(ValueError):
            compute_wave_split(100, 0, 1)


class TestComputeL2HitRatio:
    def test_small_working_set_high_hit(self):
        # 32KB working set, 50MB L2, 132 CTAs
        # Per-CTA L2 = 50MB/132 ~ 388KB >> 32KB
        ratio = compute_l2_hit_ratio(32 * 1024, 50 * 1024 * 1024, 132)
        assert ratio > 0.9

    def test_large_working_set_low_hit(self):
        # 10MB working set, 50MB L2, 132 CTAs
        # Per-CTA L2 = 50MB/132 ~ 388KB << 10MB
        ratio = compute_l2_hit_ratio(10 * 1024 * 1024, 50 * 1024 * 1024, 132)
        assert ratio < 0.1

    def test_working_set_equals_capacity(self):
        # Per-CTA L2 exactly equals working set → ratio = 1.0 (continuous formula)
        ratio = compute_l2_hit_ratio(1000, 1000, 1)
        assert ratio == pytest.approx(1.0)

    def test_returns_zero_for_invalid(self):
        assert compute_l2_hit_ratio(0, 1000, 1) == 0.0
        assert compute_l2_hit_ratio(1000, 0, 1) == 0.0

    def test_bounded_zero_one(self):
        for ws in [100, 1000, 10000, 100000, 1000000]:
            ratio = compute_l2_hit_ratio(ws, 50 * 1024 * 1024, 132)
            assert 0.0 <= ratio <= 1.0


class TestComputeTileEfficiency:
    def test_perfect_tiling(self):
        # 256x256 with 128x128 tiles = 4 full tiles, 0 partial
        result = compute_tile_efficiency(256, 256, 128, 128)
        assert result["full_tile_count"] == 4
        assert result["partial_tile_count"] == 0
        assert result["total_tiles"] == 4

    def test_one_partial_row(self):
        # 300x256 with 128x128: m_tiles=3, n_tiles=2
        # Full: 2x2=4, Partial: 3x2 - 4 = 2 (bottom row)
        result = compute_tile_efficiency(300, 256, 128, 128)
        assert result["total_tiles"] == 6
        assert result["full_tile_count"] == 4
        assert result["partial_tile_count"] == 2

    def test_partial_both_dims(self):
        # 300x300 with 128x128: m_tiles=3, n_tiles=3
        # Full interior: 2x2=4, Partial: 9-4=5
        result = compute_tile_efficiency(300, 300, 128, 128)
        assert result["total_tiles"] == 9
        assert result["full_tile_count"] == 4
        assert result["partial_tile_count"] == 5
        assert 0.0 < result["partial_tile_avg_efficiency"] < 1.0

    def test_very_small_problem(self):
        # 1x1 with 128x128: one partial tile
        result = compute_tile_efficiency(1, 1, 128, 128)
        assert result["total_tiles"] == 1
        assert result["full_tile_count"] == 0
        assert result["partial_tile_count"] == 1
        assert result["partial_tile_avg_efficiency"] < 0.01

    def test_raises_on_non_positive(self):
        with pytest.raises(ValueError):
            compute_tile_efficiency(0, 256, 128, 128)


class TestIsEdgeTile:
    def test_interior_tile(self):
        # 256x256, tile 128x128 -> 2x2 grid, all are full
        assert not is_edge_tile(0, 2, 2, 256, 256, 128, 128)
        assert not is_edge_tile(3, 2, 2, 256, 256, 128, 128)

    def test_bottom_edge(self):
        # 300x256, tile 128x128 -> 3x2 grid
        # Row 2 (indices 4,5) are edge
        assert not is_edge_tile(0, 3, 2, 300, 256, 128, 128)
        assert is_edge_tile(4, 3, 2, 300, 256, 128, 128)
        assert is_edge_tile(5, 3, 2, 300, 256, 128, 128)

    def test_right_edge(self):
        # 256x300, tile 128x128 -> 2x3 grid
        # Column 2 (indices 2,5) are edge
        assert is_edge_tile(2, 2, 3, 256, 300, 128, 128)
        assert is_edge_tile(5, 2, 3, 256, 300, 128, 128)


class TestComputeActualTileDims:
    def test_full_tile(self):
        actual_m, actual_n = compute_actual_tile_dims(0, 256, 256, 128, 128, 2)
        assert actual_m == 128
        assert actual_n == 128

    def test_edge_tile(self):
        # 300x256, tile 128x128, n_tiles=2. CTA index 4 = row 2, col 0
        actual_m, actual_n = compute_actual_tile_dims(4, 300, 256, 128, 128, 2)
        assert actual_m == 44  # 300 - 2*128 = 44
        assert actual_n == 128
