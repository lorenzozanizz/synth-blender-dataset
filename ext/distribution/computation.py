from enum import Enum


# Use a common sampling raw distribution for all kinds of entries, in this way
# we can apply the seed to this single RNG and obtain reproducibility.

RECOGNIZED_DISTRIBUTIONS = ("normal", "poisson", "uniform", "gamma", "custom")

class Distribution(Enum):
    BERNOULLI = "Bernoulli"
    UNIFORM = "Uniform"
    MULTIVARIATE_UNIFORM = "Multivariate Uniform"
    BETA = "Beta"
    GEOMETRIC = "Geometric"
    BINOMIAL = "Binomial"
    GAUSSIAN = "Gaussian"
    MULTIVARIATE_GAUSSIAN = "Multivariate Gaussian"
    MULTIVARIATE_ISOTROPIC_GAUSSIAN = "Multivariate Isotropic Gaussian"

ONE_D_DISTRIBUTIONS = (
    Distribution.UNIFORM,
    Distribution.GEOMETRIC,
    Distribution.GAUSSIAN,
    Distribution.BETA,
    Distribution.BINOMIAL
)

UPPER_D_DISTRIBUTIONS = (
    Distribution.MULTIVARIATE_UNIFORM,
    Distribution.MULTIVARIATE_GAUSSIAN,
    Distribution.MULTIVARIATE_ISOTROPIC_GAUSSIAN
)

class Sampler:

    def __init__(self, distribution: Distribution):
        self.distribution = distribution

    def seed(self, seed):
        pass
