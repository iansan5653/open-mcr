"""General geometry-related math utilities."""

import cv2
import math
from . import math_utils
from . import list_utils


def approx_poly(contour):
    """Approximate the simple polygon for the contour."""
    perimeter = cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, 0.1 * perimeter, True)


def calc_2d_dist(point_a, point_b):
    """Calculate the Euclidean distance between two 2d points."""
    return math.sqrt((point_a[0] - point_b[0])**2 +
                     (point_a[1] - point_b[1])**2)


def calc_angle(end_a, shared, end_b):
    """Calculate the internal angle between the two vectors (always in 0-180 range)."""
    mag_a = calc_2d_dist(shared, end_a)
    mag_b = calc_2d_dist(shared, end_b)
    dist_ab = calc_2d_dist(end_a, end_b)
    cosine = (mag_a**2 + mag_b**2 - dist_ab**2) / (2 * mag_a * mag_b)
    angle = abs(math.acos(cosine))
    return angle if angle <= 180 else angle - 180


def calc_corner_angles(contour):
    """For a list of points, returns a list of numbers, where each element with
    index `i` is the angle between points `i-1`, `i`, and `i+1`."""
    result = []
    for i, point in enumerate(contour):
        previous_point = contour[list_utils.prev_index(contour, i)]
        next_point = contour[list_utils.next_index(contour, i)]
        result.append(calc_angle(previous_point, point, next_point))
    return result


def calc_side_lengths(contour):
    """For a list of points, returns a list of numbers, where each element with
    index `i` is the distance from point `i` to point `i+1`."""
    result = []
    for i, point in enumerate(contour):
        next_point = contour[list_utils.next_index(contour, i)]
        result.append(calc_2d_dist(point, next_point))
    return result


def all_approx_square(contour):
    """Returns true if every angle in `contour` is approximately right (90deg)."""
    angles = calc_corner_angles(contour)
    return math_utils.all_approx_equal(angles, math.pi / 2)


def get_line(point_a, point_b):
    """Given two points, generate the point-slope of a line that passes through them."""
    run = (point_a[0] - point_b[0])
    slope = (point_a[1] - point_b[1]) / run if run != 0 else math.inf
    return slope, point_a


def get_perpendicular_line(slope, point):
    """Given a slope and a point, returns a line passing through the point with a perpendicular slope."""
    return rotate_line(slope, point, math.pi / 2)


def rotate_line(slope, point, theta):
    """Given a slope and a point, return the line with slope rotated `theta`
    radians CCW and passing through `point`."""
    new_angle = math.atan(slope) + theta
    new_slope = math.tan(new_angle)
    return new_slope, point


def calc_angle_between(slope_a, slope_b):
    """Given two slopes, calculate the CCW positive angle between them."""
    angle_a = math.atan(slope_a)
    angle_b = math.atan(slope_b)
    return math.abs(angle_a - angle_b)


def line_as_function(slope, point):
    """Given the point-slope form of a line, return a function that takes x
    values and returns y values. """
    return lambda x: slope * (x - point[0]) + point[1]


def is_between_lines(point, line_a, line_b):
    """Returns true if `point` is vertically between or on `line_a` and `line_b`."""
    if line_a[0] == math.inf or line_b[0] == math.inf:
        raise ValueError(
            "Cannot determine if point is between lines because at least one line is vertical."
        )
    y_a = line_as_function(*line_a)(point[0])
    y_b = line_as_function(*line_b)(point[0])
    return y_a <= point[1] <= y_b or y_a >= point[1] >= y_b


def is_in_box(point, lines):
    """Given a point and a set of lines, determines if point is in the box formed
    by those lines.

    Args:
        point: The x-y point to check.
        lines: A list of four lines in point-slope form. Must be in order; ie,
            opposite lines should not be next to each other in the list.
    """
    return is_between_lines(point, lines[0], lines[2]) and is_between_lines(
        point, lines[1], lines[3])

def most_horizontal_line_index(lines):
    """Returns the index of the most horizontal line."""
    lowest_slope = math.inf
    lowest_index = -1
    for i, line in enumerate(lines):
        slope = abs(line[1])
        if slope < lowest_slope:
            lowest_slope = slope
            lowest_index = i
    return lowest_index