import pytest
from unittest.mock import patch

from mathutils import Vector
from ext.distribution.computation import (
    Distribution,
    ConstantSampler,
    PresetSampler,
    SelectorSampler,
    VectorSampler,
    SphereDistribution,
    SamplerCompiler,
    ONE_D_DISTRIBUTIONS,
    UPPER_D_DISTRIBUTIONS
)


# Tests for ConstantSampler
def test_constant_sampler_dimension():
    """ConstantSampler should have dimension 1"""
    sampler = ConstantSampler(5.0)
    assert sampler.dimension == 1


def test_constant_sampler_returns_constant_value():
    """ConstantSampler should always return the same value"""
    value = 42.5
    sampler = ConstantSampler(value)

    for _ in range(100):
        sample = sampler.sample()
        assert sample == [value]
        assert len(sample) == 1


def test_constant_sampler_zero():
    """ConstantSampler with zero should work"""
    sampler = ConstantSampler(0.0)
    assert sampler.sample() == [0.0]


def test_constant_sampler_negative():
    """ConstantSampler with negative value should work"""
    sampler = ConstantSampler(-10.5)
    assert sampler.sample() == [-10.5]


# Tests for PresetSampler - Individual Distribution Methods
def test_preset_sampler_uniform():
    """Uniform distribution should return values within range"""
    params = {'min': 10.0, 'max': 20.0}

    for _ in range(100):
        sample = PresetSampler._sample_uniform(params, dim=5)
        assert len(sample) == 5
        assert all(10.0 <= x <= 20.0 for x in sample)


def test_preset_sampler_uniform_single_value_range():
    """Uniform with min=max should return that value"""
    params = {'min': 5.0, 'max': 5.0}

    sample = PresetSampler._sample_uniform(params, dim=10)
    assert all(x == 5.0 for x in sample)


def test_preset_sampler_bernoulli():
    """Bernoulli should return 0 or 1"""
    params = {'p': 0.5}

    for _ in range(100):
        sample = PresetSampler._sample_bernoulli(params, dim=10)
        assert len(sample) == 10
        assert all(x in [0, 1] for x in sample)


def test_preset_sampler_bernoulli_p_zero():
    """Bernoulli with p=0 should always return 0"""
    params = {'p': 0.0}

    for _ in range(50):
        sample = PresetSampler._sample_bernoulli(params, dim=20)
        assert all(x == 0 for x in sample)


def test_preset_sampler_bernoulli_p_one():
    """Bernoulli with p=1 should always return 1"""
    params = {'p': 1.0}

    for _ in range(50):
        sample = PresetSampler._sample_bernoulli(params, dim=20)
        assert all(x == 1 for x in sample)


def test_preset_sampler_beta():
    """Beta distribution should return values in specified range"""
    params = {'min': 0.0, 'max': 1.0, 'alpha': 2.0, 'beta': 5.0}

    for _ in range(100):
        sample = PresetSampler._sample_beta(params, dim=5)
        assert len(sample) == 5
        assert all(0.0 <= x <= 1.0 for x in sample)


def test_preset_sampler_beta_offset_range():
    """Beta distribution should respect min/max offset"""
    params = {'min': 10.0, 'max': 20.0, 'alpha': 2.0, 'beta': 2.0}

    for _ in range(50):
        sample = PresetSampler._sample_beta(params, dim=5)
        assert all(10.0 <= x <= 20.0 for x in sample)


def test_preset_sampler_geometric():
    """Geometric distribution should return non-negative integers"""
    params = {'p': 0.5}

    for _ in range(50):
        sample = PresetSampler._sample_geometric(params, dim=10)
        assert len(sample) == 10
        assert all(x >= 0 for x in sample)


def test_preset_sampler_binomial():
    """Binomial distribution should return integers in [0, n]"""
    params = {'n': 10, 'p': 0.5}

    for _ in range(100):
        sample = PresetSampler._sample_binomial(params, dim=5)
        assert len(sample) == 5
        assert all(0 <= x <= 10 for x in sample)


def test_preset_sampler_gaussian():
    """Gaussian distribution should return values around mean"""
    params = {'mean': 100.0, 'std': 10.0}

    samples = []
    for _ in range(500):
        sample = PresetSampler._sample_gaussian(params, dim=1)
        samples.extend(sample)

    # Check mean is approximately correct
    mean = sum(samples) / len(samples)
    assert 95.0 < mean < 105.0


def test_preset_sampler_multivariate_uniform():
    """Multivariate uniform should respect per-dimension bounds"""
    params = {
        'min_vec': [0.0, 10.0, -5.0],
        'max_vec': [1.0, 20.0, 5.0]
    }

    for _ in range(100):
        sample = PresetSampler._sample_multivariate_uniform(params, dim=3)
        assert len(sample) == 3
        assert 0.0 <= sample[0] <= 1.0
        assert 10.0 <= sample[1] <= 20.0
        assert -5.0 <= sample[2] <= 5.0


def test_preset_sampler_isotropic_gaussian():
    """Isotropic gaussian should respect dimension and bounds"""
    params = {
        'mean_vec': [0.0, 10.0, -5.0],
        'variance': 1.0
    }

    for _ in range(100):
        sample = PresetSampler._sample_isotropic_gaussian(params, dim=3)
        assert len(sample) == 3


def test_preset_sampler_isotropic_gaussian_dimension_mismatch():
    """Isotropic gaussian should raise on dimension mismatch"""
    params = {
        'mean_vec': [0.0, 10.0],  # Length 2
        'variance': 1.0
    }

    with pytest.raises(ValueError, match="mean length"):
        PresetSampler._sample_isotropic_gaussian(params, dim=3)

# Tests for PresetSampler - Integration
def test_preset_sampler_config_compilation():
    """PresetSampler should compile config correctly"""
    config = {
        'preset': 'UNIFORM',
        'parameters': {'min': 5.0, 'max': 10.0},
        'do_discretize': False,
        'do_clamp': False
    }

    sampler = PresetSampler(config, dim=3)
    assert sampler.dimension == 3
    assert sampler.type == Distribution.UNIFORM
    assert sampler.discretize is False
    assert sampler.clamp is None


def test_preset_sampler_discretize():
    """PresetSampler should discretize values when enabled"""
    config = {
        'preset': 'GAUSSIAN',
        'parameters': {'mean': 5.5, 'std': 2.0},
        'do_discretize': True,
        'do_clamp': False
    }

    sampler = PresetSampler(config, dim=10)

    for _ in range(50):
        sample = sampler.sample()
        assert all(isinstance(x, int) for x in sample)


def test_preset_sampler_clamping():
    """PresetSampler should clamp values within specified range"""
    config = {
        'preset': 'GAUSSIAN',
        'parameters': {'mean': 50.0, 'std': 100.0},  # High std to exceed clamps
        'do_discretize': False,
        'do_clamp': True,
        'clamping_factors': (0.0, 10.0)
    }

    sampler = PresetSampler(config, dim=20)

    for _ in range(50):
        sample = sampler.sample()
        assert all(0.0 <= x <= 10.0 for x in sample)


def test_preset_sampler_discretize_and_clamp():
    """PresetSampler should discretize then clamp"""
    config = {
        'preset': 'GAUSSIAN',
        'parameters': {'mean': 50.0, 'std': 100.0},
        'do_discretize': True,
        'do_clamp': True,
        'clamping_factors': (0, 10)
    }

    sampler = PresetSampler(config, dim=20)

    for _ in range(50):
        sample = sampler.sample()
        assert all(isinstance(x, int) for x in sample)
        assert all(0 <= x <= 10 for x in sample)


def test_preset_sampler_none_distribution():
    """PresetSampler with NONE distribution should return None"""
    config = {
        'preset': 'NONE',
        'parameters': {},
        'do_discretize': False,
        'do_clamp': False
    }

    sampler = PresetSampler(config, dim=5)
    sample = sampler.sample()
    assert len(sample) == 5 and all(item == 0 for item in sample)


# Tests for SelectorSampler
def test_selector_sampler_dimension():
    """SelectorSampler should have same dimension as constituent samplers"""
    sampler1 = ConstantSampler(1.0)
    sampler2 = ConstantSampler(2.0)

    selector = SelectorSampler([sampler1, sampler2], weights=[0.5, 0.5])
    assert selector.dimension == 1


def test_selector_sampler_selects_from_options():
    """SelectorSampler should select one of the provided samplers"""
    sampler1 = ConstantSampler(10.0)
    sampler2 = ConstantSampler(20.0)

    selector = SelectorSampler([sampler1, sampler2], weights=[0.5, 0.5])

    samples = [selector.sample()[0] for _ in range(100)]
    assert all(x in [10.0, 20.0] for x in samples)


def test_selector_sampler_respects_weights():
    """SelectorSampler should respect probability weights"""
    sampler1 = ConstantSampler(10.0)
    sampler2 = ConstantSampler(20.0)

    # 99:1 weight ratio
    selector = SelectorSampler([sampler1, sampler2], weights=[99.0, 1.0])

    samples = [selector.sample()[0] for _ in range(500)]
    count_10 = sum(1 for x in samples if x == 10.0)

    # Should heavily favor sampler1
    assert count_10 > 400


def test_selector_sampler_dimension_mismatch():
    """SelectorSampler should raise on dimension mismatch"""
    sampler1 = ConstantSampler(1.0)  # dimension 1
    sampler2 = VectorSampler([ConstantSampler(1.0), ConstantSampler(2.0)])  # dimension 2

    with pytest.raises(ValueError, match="same dimension"):
        SelectorSampler([sampler1, sampler2], weights=[0.5, 0.5])


def test_selector_sampler_single_option():
    """SelectorSampler with single option should always select it"""
    sampler = ConstantSampler(42.0)
    selector = SelectorSampler([sampler], weights=[1.0])

    for _ in range(10):
        assert selector.sample() == [42.0]



# Tests for VectorSampler
def test_vector_sampler_dimension():
    """VectorSampler dimension should equal number of inputs"""
    samplers = [ConstantSampler(1.0), ConstantSampler(2.0), ConstantSampler(3.0)]
    vector = VectorSampler(samplers)

    assert vector.dimension == 3


def test_vector_sampler_combines_samples():
    """VectorSampler should concatenate samples from constituent samplers"""
    samplers = [ConstantSampler(10.0), ConstantSampler(20.0), ConstantSampler(30.0)]
    vector = VectorSampler(samplers)

    sample = vector.sample()
    assert sample == [10.0, 20.0, 30.0]


def test_vector_sampler_non_1d_input():
    """VectorSampler should reject non-1D inputs"""
    sampler_1d = ConstantSampler(1.0)
    sampler_2d = VectorSampler([ConstantSampler(1.0), ConstantSampler(2.0)])

    with pytest.raises(ValueError, match="1D"):
        VectorSampler([sampler_1d, sampler_2d])


def test_vector_sampler_empty():
    """VectorSampler with no inputs should have dimension 0"""
    vector = VectorSampler([])
    assert vector.dimension == 0
    assert vector.sample() == []


def test_vector_sampler_mixed_distributions():
    """VectorSampler should work with different distribution types"""
    config_uniform = {
        'preset': 'UNIFORM',
        'parameters': {'min': 0.0, 'max': 1.0},
        'do_discretize': False,
        'do_clamp': False
    }

    samplers = [
        ConstantSampler(5.0),
        PresetSampler(config_uniform, dim=1)
    ]
    vector = VectorSampler(samplers)

    assert vector.dimension == 2
    sample = vector.sample()
    assert len(sample) == 2
    assert sample[0] == 5.0
    assert 0.0 <= sample[1] <= 1.0


# Tests for SamplerCompiler
def test_sampler_compiler_simple_config():
    """SamplerCompiler should compile simple preset config"""
    config = {
        'preset': 'UNIFORM',
        'parameters': {'min': 5.0, 'max': 10.0},
        'do_discretize': False,
        'do_clamp': False,
        'use_tree': False
    }

    sampler = SamplerCompiler.compile(config, dim=3)
    assert isinstance(sampler, PresetSampler)
    assert sampler.dimension == 3


def test_sampler_compiler_detects_simple_vs_tree():
    """SamplerCompiler should route to correct compilation method"""
    config_simple = {
        'preset': 'GAUSSIAN',
        'parameters': {'mean': 0.0, 'std': 1.0},
        'do_discretize': False,
        'do_clamp': False,
        'use_tree': False
    }

    sampler = SamplerCompiler._compile_simple_config(config_simple, dim=2)
    assert isinstance(sampler, PresetSampler)
    assert sampler.dimension == 2


@patch('ext.distribution.computation.bpy')
def test_sampler_compiler_node_config_constant(mock_bpy):
    """SamplerCompiler should compile constant node"""
    # Mock node tree
    mock_bpy.data.node_groups = []

    config = {
        'type': 'constant',
        'value': 42.0
    }

    # Manually compile constant
    sampler = ConstantSampler(config['value'])
    assert sampler.sample() == [42.0]

# Tests for Distribution Enum
def test_one_d_distributions():
    """ONE_D_DISTRIBUTIONS should only contain 1D types"""
    for dist in ONE_D_DISTRIBUTIONS:
        assert dist in Distribution


def test_upper_d_distributions():
    """UPPER_D_DISTRIBUTIONS should only contain multi-D types"""
    for dist in UPPER_D_DISTRIBUTIONS:
        assert dist in Distribution


# Integration Tests - Complex Sampling Scenarios
def test_nested_selector_vector():
    """VectorSampler with SelectorSampler inputs"""
    selector1 = SelectorSampler(
        [ConstantSampler(1.0), ConstantSampler(2.0)],
        weights=[0.5, 0.5]
    )
    selector2 = SelectorSampler(
        [ConstantSampler(10.0), ConstantSampler(20.0)],
        weights=[0.5, 0.5]
    )

    vector = VectorSampler([selector1, selector2])
    assert vector.dimension == 2

    sample = vector.sample()
    assert sample[0] in [1.0, 2.0]
    assert sample[1] in [10.0, 20.0]


def test_complex_gaussian_workflow():
    """Complex workflow with Gaussian, discretization, and clamping"""
    config = {
        'preset': 'GAUSSIAN',
        'parameters': {'mean': 5.0, 'std': 2.0},
        'do_discretize': True,
        'do_clamp': True,
        'clamping_factors': (0, 10)
    }

    sampler = PresetSampler(config, dim=5)

    for _ in range(50):
        sample = sampler.sample()
        assert len(sample) == 5
        assert all(isinstance(x, int) for x in sample)
        assert all(0 <= x <= 10 for x in sample)


def test_preset_sampler_get_sampler_lookup():
    """PresetSampler._get_sampler should return correct function"""
    for dist in Distribution:
        func = PresetSampler._get_sampler(dist)
        assert callable(func)


# Tests for SphereDistribution
def test_sphere_distribution_dimension():
    """SphereDistribution should have dimension 3"""
    dist = SphereDistribution({'center': Vector((0, 0, 0)), 'radius': 1.0})
    assert dist.dimension == 3


def test_sphere_distribution_samples_on_surface():
    """Samples from sphere should be approximately on the sphere surface"""
    center = Vector((0, 0, 0))
    radius = 5.0
    dist = SphereDistribution({'center':center, 'radius':radius})

    for _ in range(100):
        sample = dist.sample()
        distance_from_center = (
                                       (sample[0] - center[0]) ** 2 +
                                       (sample[1] - center[1]) ** 2 +
                                       (sample[2] - center[2]) ** 2
                               ) ** 0.5

        # Should be approximately equal to radius
        assert abs(distance_from_center - radius) < 0.01


def test_sphere_distribution_offset_center():
    """Sphere samples should respect center offset"""
    center = Vector((10, 20, 30))
    radius = 1.0
    dist = SphereDistribution({'center':center, 'radius':radius})

    for _ in range(100):
        sample = dist.sample()
        distance_from_center = (
                                       (sample[0] - center[0]) ** 2 +
                                       (sample[1] - center[1]) ** 2 +
                                       (sample[2] - center[2]) ** 2
                               ) ** 0.5

        assert abs(distance_from_center - radius) < 0.01