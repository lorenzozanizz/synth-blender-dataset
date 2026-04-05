"""

"""
from typing import Union
from abc import abstractmethod, ABCMeta
import random
from colorsys import hsv_to_rgb

import bpy

# Simple alias for an RGB tuple and RGBa tuple
rgb_color = tuple[Union[float, int], Union[float, int], Union[float, int]]
rgba_color = tuple[Union[float, int], Union[float, int], Union[float, int], Union[float, int]]

class ColorSampler(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def sample_color(use_alpha: bool = False, use_0_1_range: bool = False) -> Union[rgba_color, rgb_color]:
        pass

class UniformColorSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, use_0_1_range: bool = False) -> rgb_color:
        rng: tuple[float, float, float] = (random.random(), random.random(), random.random())
        alpha = random.random()
        if use_0_1_range:
            rng = tuple(int(channel*255) for channel in rng)
            alpha = int(alpha*255)
        if use_alpha:
            return (*rng, alpha)
        else:
            return rng


class UniformHSVColorSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, use_0_1_range: bool = False) -> rgb_color:
        h = random.random()  # Full hue circle
        s = random.uniform(0.5, 1.0)  # Saturation range
        v = random.uniform(0.7, 1.0)  # Value range
        return hsv_to_rgb(h, s, v)

class GaussianRGBSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, use_0_1_range: bool = False) -> rgb_color:
        r = max(0, min(1, random.gauss(base_color[0], variance)))
        g = max(0, min(1, random.gauss(base_color[1], variance)))
        b = max(0, min(1, random.gauss(base_color[2], variance)))
        return (r, g, b)


class PaletteSampler(ColorSampler):

    @staticmethod
    def sample_color(use_alpha: bool = False, use_0_1_range: bool = False) -> rgb_color:
        colors = [item.color for item in palette]
        weights = [item.weight for item in palette]
        return random.choices(colors, weights=weights, k=1)[0]

    @staticmethod
    def set_palette(palette, weights):
        pass

