from enum import Enum


# Use a common sampling raw distribution for all kinds of entries, in this way
# we can apply the seed to this single RNG and obtain reproducibility.
class Distribution(Enum):
    """

    """

    BERNOULLI = "Bernoulli"
    UNIFORM = "Uniform"
    BETA = "Beta"
    GEOMETRIC = "Geometric"
    BINOMIAL = "Binomial"
    GAUSSIAN = "Gaussian"

    MULTIVARIATE_UNIFORM = "Multivariate Uniform"
    MULTIVARIATE_GAUSSIAN = "Multivariate Gaussian"
    MULTIVARIATE_ISOTROPIC_GAUSSIAN = "Multivariate Isotropic Gaussian"

# One dimensional distributions to be used when the datatype to be randomized is scalar
ONE_D_DISTRIBUTIONS = (
    Distribution.UNIFORM, Distribution.GEOMETRIC, Distribution.GAUSSIAN,
    Distribution.BETA, Distribution.BINOMIAL, Distribution.BERNOULLI
)

# These are the distributions available for multidimensional distributions. In reality, it is
# also possible to change this to have 2D and 3D separately
UPPER_D_DISTRIBUTIONS = (
    Distribution.MULTIVARIATE_UNIFORM, Distribution.MULTIVARIATE_GAUSSIAN, Distribution.MULTIVARIATE_ISOTROPIC_GAUSSIAN
)

class Sampler:

    def __init__(self, distribution: Distribution):
        self.distribution = distribution

    def seed(self, seed):
        pass

""" 
The rationale is that the Distribution tree is compiled into a set of these subclasses so that the
extraction of data can happen without interrogating the bpy data component every time. 


"""

class CompiledSampler:
    pass