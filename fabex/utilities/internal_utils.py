from math import (
    cos,
    sqrt,
)

import numpy as np

from .numba_utils import jit


@jit(nopython=True, parallel=True, fastmath=True, cache=True)
def _internal_x_y_distance_to(ourpoints, theirpoints, cutoff):
    v1 = ourpoints[0]
    v2 = theirpoints[0]
    minDistSq = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
    cutoffSq = cutoff**2
    for v1 in ourpoints:
        for v2 in theirpoints:
            distSq = (v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2
            if distSq < cutoffSq:
                return sqrt(distSq)
            minDistSq = min(distSq, minDistSq)
    return sqrt(minDistSq)


# don't make this @jit parallel, because it sometimes gets called with small N
# and the overhead of threading is too much.
@jit(nopython=True, fastmath=True, cache=True)
def _optimize_internal(points, keep_points, e, protect_vertical, protect_vertical_limit):
    # inlined so that numba can optimize it nicely
    def _mag_sq(v1):
        return v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2

    def _dot_pr(v1, v2):
        return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]

    def _applyVerticalLimit(v1, v2, cos_limit):
        """Test Path Segment on Verticality Threshold, for Protect_vertical Option"""
        z = abs(v1[2] - v2[2])
        if z > 0:
            # don't use this vector because dot product of 0,0,1 is trivially just v2[2]
            #            vec_up = np.array([0, 0, 1])
            vec_diff = v1 - v2
            vec_diff2 = v2 - v1
            vec_diff_mag = np.sqrt(_mag_sq(vec_diff))
            # dot product = cos(angle) * mag1 * mag2
            cos1_times_mag = vec_diff[2]
            cos2_times_mag = vec_diff2[2]
            if cos1_times_mag > cos_limit * vec_diff_mag:
                # vertical, moving down
                v1[0] = v2[0]
                v1[1] = v2[1]
            elif cos2_times_mag > cos_limit * vec_diff_mag:
                # vertical, moving up
                v2[0] = v1[0]
                v2[1] = v1[1]

    cos_limit = cos(protect_vertical_limit)
    prev_i = 0
    for i in range(1, points.shape[0] - 1):
        v1 = points[prev_i]
        v2 = points[i + 1]
        vmiddle = points[i]

        line_direction = v2 - v1
        line_length = sqrt(_mag_sq(line_direction))
        if line_length == 0:
            # don't keep duplicate points
            keep_points[i] = False
            continue
        # normalize line direction
        line_direction *= 1.0 / line_length  # N in formula below
        # X = A + tN (line formula) Distance to point P
        # A = v1, N = line_direction, P = vmiddle
        # distance = || (P - A) - ((P-A).N)N ||
        point_offset = vmiddle - v1
        distance_sq = _mag_sq(
            point_offset - (line_direction * _dot_pr(point_offset, line_direction))
        )
        # compare on squared distance to save a sqrt
        if distance_sq < e * e:
            keep_points[i] = False
        else:
            keep_points[i] = True
            if protect_vertical:
                _applyVerticalLimit(points[prev_i], points[i], cos_limit)
            prev_i = i
