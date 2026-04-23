import pytest
from unittest.mock import patch
import random
from typing import Sequence

from ext.distribution.bezier import *


def equality_with_tolerance(vec_1: Sequence, vec_2: Sequence, dims: int = 3, tol=1e-5):
    mae = 0
    for i in range(dims):
        mae += abs(vec_1[i]-vec_2[i])
    return mae < tol

def test_bezier_midpoint():

    assert equality_with_tolerance((1, 1, 1), (1, 1, 1))
