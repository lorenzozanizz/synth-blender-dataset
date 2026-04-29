"""

"""
from typing import Union, List
from abc import abstractmethod, ABCMeta
from random import gauss, random, uniform, choices
from colorsys import hsv_to_rgb


# Simple alias for an RGB tuple and RGBa tuple
rgb_color = tuple[float, float, float]
rgba_color = tuple[float, float, float, float]

class ColorSampler(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def sample_color(
            use_alpha: bool = False, **kwargs) -> Union[rgba_color, rgb_color]:
        pass

class UniformColorSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, **kwargs) -> Union[rgba_color, rgba_color]:
        rng = (random(), random(), random())
        if use_alpha:
            return rng[0], rng[1], rng[2], random()
        else:
            return rng

class UniformHSVColorSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, **kwargs) -> rgb_color:
        h = random()  # Full hue circle
        s = uniform(0.5, 1.0)  # Saturation range
        v = uniform(0.7, 1.0)  # Value range
        return hsv_to_rgb(h, s, v)

class GaussianRGBSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, base_color: rgb_color = (1,1,1), variance=1) -> rgb_color:
        r = max(0.0, min(1.0, gauss(base_color[0], variance)))
        g = max(0.0, min(1.0, gauss(base_color[1], variance)))
        b = max(0.0, min(1.0, gauss(base_color[2], variance)))
        return r, g, b


class PaletteSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, palette=None) -> rgb_color:
        if palette is None:
            palette = list()
        colors = [item.color for item in palette]
        weights = [item.weight for item in palette]
        return choices(colors, weights=weights, k=1)[0]


class PresetColorSampler:
    """Base sampler interface"""

    def __init__(self):
        pass

    @property
    def has_alpha(self) -> bool:
        """Return dimensionality of samples"""
        return False

    def sample(self) -> List[float]:
        """Sample a vector of shape (dimension,)"""
        pass
