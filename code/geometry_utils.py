"""General geometry-related math utilities."""

import cv2
import math
import math_utils
import list_utils
import typing
import numpy as np
import enum


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
    return np.array([[[point.x, point.y]] for point in polygon])


def approx_poly(contour: np.array) -> Polygon:
    """Approximate the simple polygon for the contour. Returns a polygon in
    clockwise order."""
    perimeter = cv2.arcLength(contour, True)
    simple = cv2.approxPolyDP(contour, 0.05 * perimeter, True)
    polygon = contour_to_polygon(simple)
    return polygon_to_clockwise(polygon)


def polygon_to_clockwise(polygon: Polygon) -> Polygon:
    """Returns the given polygon in clockwise direction."""
    clockwise = cv2.contourArea(polygon_to_contour(polygon), True) >= 0
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


def get_perpendicular_line(line: Line,
                           point: typing.Optional[Point] = None) -> Line:
    """Given a slope and a point, returns a line passing through the point with a perpendicular slope."""
    return rotate_line(line, math.pi / 2, point)


def rotate_line(line: Line, theta: float,
                point: typing.Optional[Point] = None) -> Line:
    """Given a slope and a point, return the line with slope rotated `theta`
    radians CCW and passing through `point`.

    NOTE: If `point` is not on `line`, the line will be move so that it is. This
    is NOT a rotation about `point` unless `point` already falls on `line`.

    If `point` is not provided, will rotate about `line.point`.
    """
    new_angle = math.atan(line.slope) + theta
    new_slope = math.tan(new_angle)
    return Line(new_slope, point if point is not None else line.point)


def calc_angle_between(line_a: Line, line_b: Line) -> float:
    """Given two lines, calculate the CCW positive angle between them."""
    angle_a = math.atan(line_a.slope)
    angle_b = math.atan(line_b.slope)
    return abs(angle_a - angle_b)


InequalityLine = typing.Tuple[Line, math_utils.InequalityTypes]


def is_in_inequalities(point: Point,
                       inequalities: typing.List[InequalityLine]) -> bool:
    """For a all provided inequality comparisons defined by lines, checks if
    the given point satisfies all of them."""
    for inequality in inequalities:
        compare_value = inequality[0](point.x)

        if ((inequality[1] is math_utils.InequalityTypes.GT
             and point.y <= compare_value)
                or (inequality[1] is math_utils.InequalityTypes.GTE
                    and point.y < compare_value)
                or (inequality[1] is math_utils.InequalityTypes.LT
                    and point.y >= compare_value)
                or (inequality[1] is math_utils.InequalityTypes.LTE
                    and point.y > compare_value)
                or (inequality[1] is math_utils.InequalityTypes.NE
                    and point.y == compare_value)):
            return False
    return True


def create_range_check_fn(*inequalities: typing.List[InequalityLine]):
    return lambda point: is_in_inequalities(point, inequalities
                                            )  # type: ignore


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


def create_change_of_basis(
        new_origin: Point,
        theta: float) -> typing.Tuple[typing.Callable[[Point], Point], typing.
                                      Callable[[Point], Point]]:
    """Returns functions that will convert points from the current coordinate
    system to a new one where the origin is translated to `new_origin` and the
    axis are rotated `theta` radians CCW.

    Returns:
        A tuple where the first element is a function that converts
            points to the new system, and the second is a function that converts
            them back.
    """
    origin = Point(0, 0)

    def to_basis(point: Point) -> Point:
        translated = Point(point.x - new_origin.x, point.y - new_origin.y)
        r = calc_2d_dist(origin, translated)
        phi = math.atan2(translated.y, translated.x)
        to_phi = phi - theta
        return Point(r * math.cos(to_phi), r * math.sin(to_phi))

    def from_basis(point: Point) -> Point:
        r = calc_2d_dist(origin, point)
        phi = math.atan2(point.y, point.x)
        to_phi = phi + theta
        rotated = Point(r * math.cos(to_phi), r * math.sin(to_phi))
        return Point(rotated.x + new_origin.x, rotated.y + new_origin.y)

    return to_basis, from_basis


def guess_centroid(quadrilateral: Polygon) -> Point:
    """Guesses an approximate centroid. Works well for squares."""
    xs = [p.x for p in quadrilateral]
    ys = [p.y for p in quadrilateral]
    return Point(math_utils.mean([max(xs), min(xs)]),
                 math_utils.mean([max(ys), min(ys)]))


class Corner(enum.Enum):
    TL = (1, 0)
    TR = (1, 1)
    BR = (0, 1)
    BL = (0, 0)


class Orientation(enum.Enum):
    VERTICAL = enum.auto()
    HORIZONTAL = enum.auto()


def get_corner(square: Polygon, corner: Corner) -> Point:
    """Gets the point representing the given corner of the square. Square should
    be pretty close to vertical - horizontal. """
    xs = [p.x for p in square]
    highest_xs = list_utils.find_greatest_value_indexes(xs, 2)
    side_points = [
        p for i, p in enumerate(square)
        if (corner.value[0] == 1 and i in highest_xs) or (
            corner.value[0] == 0 and i not in highest_xs)
    ]
    side_ys = [p.y for p in side_points]
    [highest_y] = list_utils.find_greatest_value_indexes(side_ys, 1)
    corner_point = side_points[highest_y] if (
        corner.value[1] == 1) else side_points[list_utils.next_index(
            side_points, highest_y)]
    return corner_point


def crop_rectangle(top_left_corner: Point, bottom_right_corner: Point,
                   crop_fraction: float) -> typing.Tuple[Point, Point]:
    """Given a rectangle which aligns with the grid, crops away `crop_fraction`
    of the height and width from the edges, preserving the center.

    NOTE: Assumes the rectangle is aligned with the grid. Will not work for other
    shapes.

    Returns the new top left and bottom right corners.
    """
    height = abs(top_left_corner.y - bottom_right_corner.y)
    dy = crop_fraction * height / 2
    width = abs(top_left_corner.x - bottom_right_corner.x)
    dx = crop_fraction * width / 2
    return Point(top_left_corner.x + dx,
                 top_left_corner.y + dy), Point(bottom_right_corner.x - dx,
                                                bottom_right_corner.y - dy)
