""" Utility math functions involving sampling and mathematic functions.
Functions:
    geometric: Samples a random variable from the geometric distribution, using the random module

Example:
    >>> from ext.utils.math_funcs import geometric
    >>> n = geometric(0.5) # random var from Geometric(p)
"""

import random

def geometric(p: float) -> int:
    """
    Sample from geometric distribution (number of trials until first success).
    p: probability of success on each trial [0, 1]
    Returns: number of trials (>=1)
    """
    trials = 1
    while random.random() >= p:
        trials += 1
    return trials