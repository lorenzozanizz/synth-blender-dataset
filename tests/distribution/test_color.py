import pytest

from ext.distribution.color import (
    UniformColorSampler,
    UniformHSVColorSampler,
    GaussianRGBSampler,
    PaletteSampler,
    PresetColorSampler,
    rgb_color,
)


def is_valid_rgb(color: tuple, dims: int = 3) -> bool:
    """ Check if color is valid RGB(A) with values in [0, 1] """
    if len(color) != dims:
        return False
    return all(0.0 <= c <= 1.0 for c in color)


def is_valid_hsv(h: float, s: float, v: float) -> bool:
    """ Check if HSV values are in valid ranges """
    return 0.0 <= h <= 1.0 and 0.0 <= s <= 1.0 and 0.0 <= v <= 1.0


# Tests for UniformColorSampler
def test_uniform_color_sampler_rgb():
    """ UniformColorSampler should return RGB tuple with values in [0, 1] """
    for _ in range(100):
        color = UniformColorSampler.sample_color(use_alpha=False)
        assert is_valid_rgb(color, dims=3)
        assert len(color) == 3


def test_uniform_color_sampler_rgba():
    """ UniformColorSampler with alpha should return RGBA tuple """
    for _ in range(100):
        color = UniformColorSampler.sample_color(use_alpha=True)
        assert is_valid_rgb(color, dims=4)
        assert len(color) == 4


def test_uniform_color_sampler_randomness():
    """ UniformColorSampler should produce different colors """
    colors = [UniformColorSampler.sample_color() for _ in range(50)]
    # Not all colors should be identical
    assert len(set(colors)) > 1


# Tests for UniformHSVColorSampler
def test_uniform_hsv_color_sampler_returns_rgb():
    """ UniformHSVColorSampler should return RGB tuple """
    for _ in range(100):
        color = UniformHSVColorSampler.sample_color()
        assert is_valid_rgb(color, dims=3)
        assert len(color) == 3


def test_uniform_hsv_color_sampler_saturation_range():
    """ HSV sampler saturation should be in [0.5, 1.0] """
    from colorsys import rgb_to_hsv

    for _ in range(100):
        r, g, b = UniformHSVColorSampler.sample_color()
        h, s, v = rgb_to_hsv(r, g, b)
        assert 0.5 <= s <= 1.0


def test_uniform_hsv_color_sampler_value_range():
    """ HSV sampler value should be in [0.7, 1.0] """
    from colorsys import rgb_to_hsv

    for _ in range(100):
        r, g, b = UniformHSVColorSampler.sample_color()
        h, s, v = rgb_to_hsv(r, g, b)
        assert 0.7 <= v <= 1.0


def test_uniform_hsv_color_sampler_hue_diversity():
    """ HSV sampler should produce diverse hues """
    from colorsys import rgb_to_hsv

    hues = []
    for _ in range(100):
        r, g, b = UniformHSVColorSampler.sample_color()
        h, s, v = rgb_to_hsv(r, g, b)
        hues.append(h)

    # Should have good distribution across hue circle
    assert max(hues) > 0.5
    assert min(hues) < 0.5


def test_uniform_hsv_ignores_alpha():
    """ HSV sampler should ignore use_alpha parameter """
    color_without = UniformHSVColorSampler.sample_color(use_alpha=False)
    color_with = UniformHSVColorSampler.sample_color(use_alpha=True)

    # Both should return RGB (3 components)
    assert len(color_without) == 3
    assert len(color_with) == 3


# Tests for GaussianRGBSampler
def test_gaussian_rgb_sampler_default():
    """ GaussianRGBSampler with defaults should return white-ish colors """
    for _ in range(100):
        color = GaussianRGBSampler.sample_color()
        assert is_valid_rgb(color, dims=3)


def test_gaussian_rgb_sampler_base_color():
    """ GaussianRGBSampler should center around base_color """
    base = (0.2, 0.5, 0.8)
    colors = [GaussianRGBSampler.sample_color(base_color=base, variance=0.1) for _ in range(100)]

    # Average should be close to base color
    avg_r = sum(c[0] for c in colors) / len(colors)
    avg_g = sum(c[1] for c in colors) / len(colors)
    avg_b = sum(c[2] for c in colors) / len(colors)

    assert abs(avg_r - base[0]) < 0.1
    assert abs(avg_g - base[1]) < 0.1
    assert abs(avg_b - base[2]) < 0.1


def test_gaussian_rgb_sampler_variance_effect():
    """ Higher variance should produce more spread colors """
    base = (0.5, 0.5, 0.5)

    colors_low = [GaussianRGBSampler.sample_color(base_color=base, variance=0.01) for _ in range(100)]
    colors_high = [GaussianRGBSampler.sample_color(base_color=base, variance=0.5) for _ in range(100)]

    # Calculate spread (standard deviation)
    spread_low = sum(abs(c[0] - base[0]) for c in colors_low) / len(colors_low)
    spread_high = sum(abs(c[0] - base[0]) for c in colors_high) / len(colors_high)

    assert spread_high > spread_low


def test_gaussian_rgb_sampler_clipping():
    """ GaussianRGBSampler should clip values to [0, 1] """
    # Very extreme base and variance should still be clipped
    color = GaussianRGBSampler.sample_color(base_color=(0.1, 0.9, 0.5), variance=10.0)
    assert is_valid_rgb(color, dims=3)


def test_gaussian_rgb_sampler_black_base():
    """ GaussianRGBSampler with black base should stay in valid range """
    for _ in range(100):
        color = GaussianRGBSampler.sample_color(base_color=(0.0, 0.0, 0.0), variance=0.5)
        assert is_valid_rgb(color, dims=3)


def test_gaussian_rgb_sampler_white_base():
    """ GaussianRGBSampler with white base should stay in valid range """
    for _ in range(100):
        color = GaussianRGBSampler.sample_color(base_color=(1.0, 1.0, 1.0), variance=0.5)
        assert is_valid_rgb(color, dims=3)


# Tests for PaletteSampler
class MockPaletteItem:
    """ Mock palette item for testing """

    def __init__(self, color: rgb_color, weight: float):
        self.color = color
        self.weight = weight


def test_palette_sampler_empty_palette():
    """ PaletteSampler with empty palette should handle gracefully """
    # This might raise or return empty tuple depending on implementation
    try:
        color = PaletteSampler.sample_color(palette=[])
        assert color == () or color is None
    except (IndexError, ValueError):
        pass  # Expected behavior for empty palette


def test_palette_sampler_single_color():
    """ PaletteSampler with single color should always return that color """
    palette = [MockPaletteItem(color=(0.5, 0.3, 0.8), weight=1.0)]

    for _ in range(10):
        color = PaletteSampler.sample_color(palette=palette)
        assert color == (0.5, 0.3, 0.8)


def test_palette_sampler_multiple_colors():
    """ PaletteSampler should return colors from palette """
    palette = [
        MockPaletteItem(color=(1.0, 0.0, 0.0), weight=1.0),  # Red
        MockPaletteItem(color=(0.0, 1.0, 0.0), weight=1.0),  # Green
        MockPaletteItem(color=(0.0, 0.0, 1.0), weight=1.0),  # Blue
    ]

    colors = [PaletteSampler.sample_color(palette=palette) for _ in range(100)]

    # All sampled colors should be from palette
    palette_colors = {item.color for item in palette}
    assert all(c in palette_colors for c in colors)

def test_palette_sampler_all_colors_valid():
    """ All samples from palette should be valid RGB """
    palette = [
        MockPaletteItem(color=(0.2, 0.4, 0.6), weight=1.0),
        MockPaletteItem(color=(0.8, 0.3, 0.1), weight=2.0),
        MockPaletteItem(color=(0.5, 0.5, 0.5), weight=1.5),
    ]

    for _ in range(5):
        color = PaletteSampler.sample_color(palette=palette)
        assert is_valid_rgb(color, dims=3)

# Tests for PresetColorSampler
def test_preset_color_sampler_has_alpha():
    """ PresetColorSampler should have has_alpha property """
    sampler = PresetColorSampler()
    assert hasattr(sampler, 'has_alpha')
    assert sampler.has_alpha is False


def test_preset_color_sampler_sample_method():
    """ PresetColorSampler should have sample method """
    sampler = PresetColorSampler()
    assert hasattr(sampler, 'sample')
    assert callable(sampler.sample)


def test_all_samplers_return_valid_colors():
    """ All samplers should return valid RGB colors """
    samplers = [
        (UniformColorSampler, {}),
        (UniformHSVColorSampler, {}),
        (GaussianRGBSampler, {'base_color': (0.5, 0.5, 0.5)}),
    ]

    for sampler_cls, kwargs in samplers:
        for _ in range(10):
            color = sampler_cls.sample_color(**kwargs)
            assert is_valid_rgb(color, dims=3), f"Invalid color from {sampler_cls.__name__}: {color}"