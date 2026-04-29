from .computation import CompiledSampler

from typing import List, Dict
from dataclasses import dataclass
from mathutils import Vector
from math import pi, sqrt, cos, sin
from random import random, choices



@dataclass
class Bezier2PSegment:
    """ """
    p0: Vector
    left_handle: Vector
    right_handle: Vector
    p1: Vector


@dataclass
class Spline:
    """ """
    segments: list[Bezier2PSegment]


@dataclass
class BezierCurve:
    """ """
    splines: list[Spline]

    @staticmethod
    def from_blender_curve(bpy_curve) -> 'BezierCurve':
        """

        :param bpy_curve: A Bezier Curve blender object
        :return:
        """
        spline_list = list()
        curve = BezierCurve(spline_list)

        matrix = bpy_curve.matrix_world

        for spline in bpy_curve.data.splines:

            if spline.type != 'BEZIER':
                continue

            segments = list()
            for i in range(len(spline.bezier_points) - 1):
                # We explicitly take into account the curve's world matrix to handle
                # scales and rotations.
                p0 =  matrix @ spline.bezier_points[i].co
                handle_left =  matrix @ spline.bezier_points[i].handle_right
                handle_right =  matrix @ spline.bezier_points[i + 1].handle_left
                p1 =  matrix @ spline.bezier_points[i + 1].co

                segments.append(Bezier2PSegment(
                    p0, handle_left, handle_right, p1))
            spline_list.append(Spline(segments))
        return curve


def evaluate_bezier_segment(p0, h0_right, h1_left, p1, t) -> Vector:
    """

    :param p0:
    :param h0_right:
    :param h1_left:
    :param p1:
    :param t:
    :return:
    """
    # From the definition of a (cubic) Bezièr curve.
    # https://en.wikipedia.org/wiki/B%C3%A9zier_curve
    mt = 1 - t
    return mt ** 3 * p0 + 3 * mt ** 2 * t * h0_right + 3 * mt * t ** 2 * h1_left + t ** 3 * p1


def evaluate_2p_bezier_seg(p: Bezier2PSegment, t) -> Vector:
    """

    :param p:
    :param t:
    :return:
    """
    # From the definition of a (cubic) Bezièr curve.
    # https://en.wikipedia.org/wiki/B%C3%A9zier_curve
    mt = 1 - t
    return mt ** 3 * p.p0 + 3 * mt ** 2 * t * p.right_handle + 3 * mt * t ** 2 * p.left_handle + t ** 3 * p.p1


def segment_length(p0, h0_right, h1_left, p1, samples=10):
    """ Approximate segment length via sampling """
    total = 0
    prev_point = p0
    for i in range(1, samples + 1):
        t = i / samples
        point = evaluate_bezier_segment(p0, h0_right, h1_left, p1, t)
        total += (point - prev_point).length
        prev_point = point
    return total


def bezier_segment_length(s: Bezier2PSegment, samples=10):
    """ """
    return segment_length(s.p0, s.right_handle, s.left_handle, s.p1, samples)


def spline_length(spl: Spline):
    return sum(bezier_segment_length(seg) for seg in spl.segments)


def normalize_weights(weights: List[float]) -> None:
    tot = sum(weights)
    for i in range(len(weights)):
        weights[i] /= tot
    return


class BezierDistribution:

    def __init__(self, curve: BezierCurve) -> None:
        """

        :param curve:
        """
        self.curve = curve

        self.spline_weight = []
        self.segment_mapped_weights: dict[int, list[float]] = dict()

        self._compile()

    def _compile(self) -> None:
        """

        :return:
        """
        self.segment_mapped_weights = {
            i: [bezier_segment_length(seg) for seg in spline.segments]
            for i, spline in enumerate(self.curve.splines)
        }
        self.spline_weight = [sum(segments, 0.0) for _, segments in self.segment_mapped_weights.items()]

        # Normalize the weights so that we can use the default random library
        # to sample a random index value (first to sample a spline, then to sample
        # a segment and finally to sample a point)
        normalize_weights(self.spline_weight)
        for spline in self.segment_mapped_weights:
            normalize_weights(self.segment_mapped_weights[spline])

    @property
    def dimension(self) -> int:
        """ Get the dimension of the Bezier distribution, assumed to be 3 (embeddeed in 3d)"""
        # All bezier are assumed to be embedded in 3d space, independently of their
        # collinearity.
        return 3

    def sample(self) -> List[float]:
        """

        :return:
        """

        if not self.spline_weight or not self.segment_mapped_weights:
            return [0.0, 0.0, 0.0]

        spline_index = choices(range(len(self.spline_weight)), weights=self.spline_weight, k=1)
        spline_index = spline_index[0]
        # We now extract the spline which was selected
        spline: Spline = self.curve.splines[spline_index]
        if not self.segment_mapped_weights[spline_index]:
            return [0.0, 0.0, 0.0]

        seg_index = choices(
            range(len(self.segment_mapped_weights[spline_index])), weights=self.segment_mapped_weights[spline_index],
            k=1)
        seg_index = seg_index[0]
        # We now extract the segment that was selected.
        segment = spline.segments[seg_index]

        # Evaluate a random point (THE RANDOM VALUE IS NOT the line parameters, this is somewhat biased)
        val = random()
        point = evaluate_2p_bezier_seg(segment, val)

        return [point[0], point[1], point[2]]

