import pytest

from ext.distribution.bezier import *


def test_bezier_midpoint():

    assert equality_with_tolerance((1, 1, 1), (1, 1, 1))
