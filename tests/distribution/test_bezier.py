import pytest
from typing import Sequence, Union

from ext.distribution.bezier import *


def equality_with_tolerance(vec_1: Union[Vector, Sequence], vec_2: Union[Vector, Sequence], dims: int = 3, tol=1e-5) -> bool:
    """Check for equality between two vectors of dimension dims of numeric type
    within a certain tolerance.

    :param vec_1: The first vector
    :param vec_2: The second vector
    :param dims: The number of dimensions to check
    :param tol: The tolerance
    :return: True if the two vectors are equal, False otherwise
    """
    mae = 0
    for i in range(dims):
        mae += abs(vec_1[i] - vec_2[i])
    return mae < tol


# Tests for evaluate_bezier_segment
def test_bezier_segment_evaluation_at_start():
    """ Bezier curve at t=0 should equal p0 """
    p0 = Vector((0, 0, 0))
    h0_right = Vector((1, 1, 1))
    h1_left = Vector((2, 2, 2))
    p1 = Vector((3, 3, 3))

    result = evaluate_bezier_segment(p0, h0_right, h1_left, p1, 0)
    assert equality_with_tolerance(result, p0)


def test_bezier_segment_evaluation_at_end():
    """ Bezier curve at t=1 should equal p1 """
    p0 = Vector((0, 0, 0))
    h0_right = Vector((1, 1, 1))
    h1_left = Vector((2, 2, 2))
    p1 = Vector((3, 3, 3))

    result = evaluate_bezier_segment(p0, h0_right, h1_left, p1, 1)
    assert equality_with_tolerance(result, p1)


def test_bezier_segment_evaluation_at_midpoint():
    """ Bezier curve at t=0.5 should be within bounds """
    p0 = Vector((0, 0, 0))
    h0_right = Vector((1, 0, 0))
    h1_left = Vector((2, 0, 0))
    p1 = Vector((3, 0, 0))

    result = evaluate_bezier_segment(p0, h0_right, h1_left, p1, 0.5)
    # For a cubic Bezier, the midpoint should be between p0 and p1
    assert 0 <= result[0] <= 3
    assert result[1] == 0  # y should stay 0
    assert result[2] == 0  # z should stay 0


# Tests for evaluate_2p_bezier_seg
def test_2p_bezier_seg_at_start():
    """ Bezier segment at t=0 should equal p0 """
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        left_handle=Vector((2, 2, 2)),
        right_handle=Vector((1, 1, 1)),
        p1=Vector((3, 3, 3))
    )

    result = evaluate_2p_bezier_seg(seg, 0)
    assert equality_with_tolerance(result, seg.p0)


def test_2p_bezier_seg_at_end():
    """ Bezier segment at t=1 should equal p1 """
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        left_handle=Vector((2, 2, 2)),
        right_handle=Vector((1, 1, 1)),
        p1=Vector((3, 3, 3))
    )

    result = evaluate_2p_bezier_seg(seg, 1)
    assert equality_with_tolerance(result, seg.p1)


# Tests for segment_length and bezier_segment_length
def test_segment_length_straight_line():
    """ Length of straight line segment should be distance between endpoints """
    p0 = Vector((0, 0, 0))
    h0_right = Vector((1, 0, 0))  # Handles on the line
    h1_left = Vector((2, 0, 0))
    p1 = Vector((3, 0, 0))

    length = segment_length(p0, h0_right, h1_left, p1, samples=100)
    # Should be approximately 3
    assert 2.9 < length < 3.1


def test_bezier_segment_length_straight():
    """ Length of straight Bezier segment (similar to test above, but uses the bezier2segment class """
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 0, 0)),
        left_handle=Vector((2, 0, 0)),
        p1=Vector((3, 0, 0))
    )

    length = bezier_segment_length(seg, samples=100)
    assert 2.9 < length < 3.1


def test_segment_length_increases_with_samples():
    """ More samples should give more accurate (typically longer) length """
    p0 = Vector((0, 0, 0))
    h0_right = Vector((1, 1, 0))
    h1_left = Vector((2, 1, 0))
    p1 = Vector((3, 0, 0))

    length_10 = segment_length(p0, h0_right, h1_left, p1, samples=10)
    length_100 = segment_length(p0, h0_right, h1_left, p1, samples=100)

    # More samples should converge to more accurate value
    assert length_100 > length_10


# Tests for spline_length
def test_spline_length_single_segment():
    """ Spline with single segment should have same length as segment """
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 0, 0)),
        left_handle=Vector((2, 0, 0)),
        p1=Vector((3, 0, 0))
    )
    spline = Spline(segments=[seg])

    length = spline_length(spline)
    assert 2.9 < length < 3.1


def test_spline_length_multiple_segments():
    """Spline with multiple segments should be sum of segment lengths"""
    seg1 = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 0, 0)),
        left_handle=Vector((2, 0, 0)),
        p1=Vector((3, 0, 0))
    )
    seg2 = Bezier2PSegment(
        p0=Vector((3, 0, 0)),
        right_handle=Vector((4, 0, 0)),
        left_handle=Vector((5, 0, 0)),
        p1=Vector((6, 0, 0))
    )
    spline = Spline(segments=[seg1, seg2])

    length = spline_length(spline)
    # Two segments of length ~3 each = ~6
    assert 5.8 < length < 6.2


# Tests for BezierDistribution
def test_bezier_distribution_empty_curve():
    """BezierDistribution with empty curve should return zero vector"""
    curve = BezierCurve(splines=[])
    dist = BezierDistribution(curve)

    sample = dist.sample()
    assert equality_with_tolerance(sample, [0.0, 0.0, 0.0])


def test_bezier_distribution_dimension():
    """BezierDistribution should have dimension 3"""
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 1, 1)),
        left_handle=Vector((2, 2, 2)),
        p1=Vector((3, 3, 3))
    )
    spline = Spline(segments=[seg])
    curve = BezierCurve(splines=[spline])
    dist = BezierDistribution(curve)

    assert dist.dimension == 3


def test_bezier_distribution_sample_bounds():
    """Samples from BezierDistribution should be within curve bounds"""
    seg = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 0, 0)),
        left_handle=Vector((2, 0, 0)),
        p1=Vector((3, 0, 0))
    )
    spline = Spline(segments=[seg])
    curve = BezierCurve(splines=[spline])
    dist = BezierDistribution(curve)

    # Sample multiple times to check bounds
    for _ in range(100):
        sample = dist.sample()
        assert 0 <= sample[0] <= 3
        assert sample[1] == 0
        assert sample[2] == 0


def test_bezier_distribution_weights_normalized():
    """BezierDistribution weights should be normalized"""
    seg1 = Bezier2PSegment(
        p0=Vector((0, 0, 0)),
        right_handle=Vector((1, 0, 0)),
        left_handle=Vector((2, 0, 0)),
        p1=Vector((3, 0, 0))
    )
    seg2 = Bezier2PSegment(
        p0=Vector((3, 0, 0)),
        right_handle=Vector((4, 0, 0)),
        left_handle=Vector((5, 0, 0)),
        p1=Vector((6, 0, 0))
    )
    spline = Spline(segments=[seg1, seg2])
    curve = BezierCurve(splines=[spline])
    dist = BezierDistribution(curve)

    # Spline weights should sum to 1.0
    weight_sum = sum(dist.spline_weight)
    assert equality_with_tolerance([weight_sum], [1.0], dims=1)
