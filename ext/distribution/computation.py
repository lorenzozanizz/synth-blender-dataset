from enum import Enum


# Use a common sampling raw distribution for all kinds of entries, in this way
# we can apply the seed to this single RNG and obtain reproducibility.

RECOGNIZED_DISTRIBUTIONS = ("normal", "poisson", "uniform", "gamma", "custom")

class DistributionType(Enum):
    NORMAL = 0
    POISSON = 1
    UNIFORM = 2
    CUSTOM = 4

class Sampler:

    def __init__(self, distribution: DistributionType):
        self.distribution = distribution

    def seed(self, seed):
        pass
