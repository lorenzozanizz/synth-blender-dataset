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