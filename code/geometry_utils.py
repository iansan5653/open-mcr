"""General geometry-related math utilities."""

import cv2
import math
import .math_utils
import .list_utils
import typing
import numpy as np


class Point:
    x: float
    y: float

    """Represents a point on a 2d plane in x, y form."""
    def __init__(self, x: float, y: float):
        """Create a new Point."""
        self.x = x
        self.y = y


Polygon = typing.List[Point]


class Line:
    slope: float
    point: Point

    """Represents a line on a 2d plane in point-slope form."""
    def __init__(self, slope: float, point: Point):
        """Create a new Line."""
        self.point = point
        self.slope = slope

    def __call__(self, x: float) -> float:
        """Get the y-value associated with an x-value."""
        return (self.slope * (x - self.point.x)) + self.point.y


def contour_to_polygon(contour: np.array) -> Polygon:
    """Convert an OpenCV contour (a numpy array) to a list of points (a polygon)."""
    return [Point(vertex[0][0], vertex[0][1]) for vertex in contour]


def polygon_to_contour(polygon: Polygon) -> np.array:
    """Convert polygon (list of points) to an OpenCV contour (numpy array)."""
    return np.array([[(point.x, point.y)] for point in polygon])


def approx_poly(contour: np.array) -> Polygon:
    """Approximate the simple polygon for the contour. Returns a polygon in
    clockwise order."""
    perimeter = cv2.arcLength(contour, True)
    simple = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
    polygon = contour_to_polygon(simple)
    return polygon_to_clockwise(polygon)


def polygon_to_clockwise(polygon: Polygon) -> Polygon:
    """Returns the given polygon in clockwise direction."""
    clockwise = cv2.contourArea(polygon_to_contour(polygon)) <= 0
    if clockwise:
        return polygon
    else:
        return list(reversed(polygon))


def calc_2d_dist(point_a: Point, point_b: Point) -> float:
    """Calculate the Euclidean distance between two 2d points."""
    return math.sqrt((point_a.x - point_b.x)**2 + (point_a.y - point_b.y)**2)


def calc_angle(end_a: Point, shared: Point, end_b: Point) -> float:
    """Calculate the internal angle between the two vectors (always in 0-180 range)."""
    mag_a = calc_2d_dist(shared, end_a)
    mag_b = calc_2d_dist(shared, end_b)
    dist_ab = calc_2d_dist(end_a, end_b)
    cosine = (mag_a**2 + mag_b**2 - dist_ab**2) / (2 * mag_a * mag_b)
    angle = abs(math.acos(round(cosine, 4)))
    return angle if angle <= 180 else angle - 180


def calc_corner_angles(contour: Polygon) -> typing.List[float]:
    """For a list of points, returns a list of numbers, where each element with
    index `i` is the angle between points `i-1`, `i`, and `i+1`."""
    result = []
    for i, point in enumerate(contour):
        previous_point = contour[list_utils.prev_index(contour, i)]
        next_point = contour[list_utils.next_index(contour, i)]
        result.append(calc_angle(previous_point, point, next_point))
    return result


def calc_side_lengths(contour: Polygon) -> typing.List[float]:
    """For a list of points, returns a list of numbers, where each element with
    index `i` is the distance from point `i` to point `i+1`."""
    result = []
    for i, point in enumerate(contour):
        next_point = contour[list_utils.next_index(contour, i)]
        result.append(calc_2d_dist(point, next_point))
    return result


def all_approx_square(contour: Polygon) -> bool:
    """Returns true if every angle in `contour` is approximately right (90deg)."""
    angles = calc_corner_angles(contour)
    return math_utils.all_approx_equal(angles, math.pi / 2)


def line_from_points(point_a: Point, point_b: Point) -> Line:
    """Given two points, generate the point-slope of a line that passes through them."""
    run = (point_a.x - point_b.x)
    slope = (point_a.y - point_b.y) / run if run != 0 else math.inf
    return Line(slope, point_a)


def get_perpendicular_line(line: Line, point: typing.Optional[Point] = None) -> Line:
    """Given a slope and a point, returns a line passing through the point with a perpendicular slope."""
    return rotate_line(line, math.pi / 2, point)


def rotate_line(line: Line, theta: float, point: typing.Optional[Point] = None) -> Line:
    """Given a slope and a point, return the line with slope rotated `theta`
    radians CCW and passing through `point`.
    
    NOTE: If `point` is not on `line`, the line will be move so that it is. This
    is NOT a rotation about `point` unless `point` already falls on `line`.

    If `point` is not provided, will rotate about `line.point`.
    """
    new_angle = math.atan(line.slope) + theta
    new_slope = math.tan(new_angle)
    return Line(new_slope, point if point is not None else line.point)


def calc_angle_between(line_a: Line,
                       line_b: Line) -> float:
    """Given two lines or slopes, calculate the CCW positive angle between them."""
    angle_a = math.atan(line_a.slope)
    angle_b = math.atan(line_b.slope)
    return abs(angle_a - angle_b)

InequalityLine = typing.Tuple[Line, math_utils.InequalityTypes]
def is_in_inequalities(point: Point, inequalities: typing.List[InequalityLine]) -> bool:
    """For a all provided inequality comparisons defined by lines, checks if
    the given point satisfies all of them."""
    for inequality in inequalities:
        compare_value = inequality[0](point.x)

        if ((inequality[1] == math_utils.InequalityTypes.GT
             and point.y <= compare_value)
                or (inequality[1] == math_utils.InequalityTypes.GTE
                    and point.y < compare_value)
                or (inequality[1] == math_utils.InequalityTypes.LT
                    and point.y >= compare_value)
                or (inequality[1] == math_utils.InequalityTypes.LTE
                    and point.y > compare_value)
                or (inequality[1] == math_utils.InequalityTypes.NE
                    and point.y == compare_value)):
            return False
    return True


def create_range_check_fn(*inequalities: InequalityLine):
    return lambda point: is_in_inequalities(point, inequalities) # type: ignore


def offset_line(line: Line, offset_point: Point) -> Line:
    """Given a line and a point, return the parallel line passing through the
    point. """
    return Line(line.slope, offset_point)


def extend_ray(a: Point, b: Point, distance: float):
    """Return the point that is `distance` from `point_b` in the direction a->b."""
    theta = math.atan2((b.y - a.y), (b.x - a.x))
    dx = math.cos(theta) * distance
    dy = math.sin(theta) * distance
    return Point(b.x + dx, b.y + dy)


