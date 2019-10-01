import math
import pathlib

import cv2

import .math_utils
import .list_utils
import .image_utils
import .geometry_utils

import typing
import numpy as np


class WrongShapeError(ValueError):
    pass


class LMark():
    """An L-shaped polygon.

    Members:
        polygon: The list of points representing the mark. Points are stored in
            a clockwise direction starting with the vertex shared by the longest
            sides.
        unit_length: The estimated grid square unit length that the mark is
            built with.
    """
    def __init__(self, polygon: geometry_utils.Polygon):
        """Create a new LMark. If the points don't form a valid LMark, raises a
        WrongShapeError."""
        if len(polygon) != 6:
            raise WrongShapeError("Incorrect number of points.")

        if not geometry_utils.all_approx_square(polygon):
            raise WrongShapeError("Corners are not square.")

        clockwise_polygon = geometry_utils.polygon_to_clockwise(polygon)
        side_lengths = geometry_utils.calc_side_lengths(clockwise_polygon)
        longest_sides_indexes = list_utils.find_greatest_value_indexes(
            side_lengths, n=2)

        if not list_utils.is_adjacent_indexes(side_lengths,
                                              *longest_sides_indexes):
            raise WrongShapeError("Longest sides are not adjacent.")

        # The longest sides should be about twice the length of the other sides
        unit_lengths = math_utils.divide_some(side_lengths,
                                              longest_sides_indexes, 2)
        if not math_utils.all_approx_equal(unit_lengths):
            raise WrongShapeError(
                "Longest sides are not twice the length of the other sides.")

        self.polygon = list_utils.arrange_index_to_first(
            clockwise_polygon, max(longest_sides_indexes))
        self.unit_length = math_utils.mean(unit_lengths)


class SquareMark:
    """An L-shaped polygon.

    Members:
        polygon: The list of points representing the mark. Points are stored in
            a clockwise direction.
        unit_length: The estimated grid square unit length that the mark is
            built with.
    """
    def __init__(self, polygon: geometry_utils.Polygon, target_size:typing.Optional[float]=None):
        """Create a new Square. If the points don't form a valid square, raises
        a WrongShapeError.

        Args:
            polygon: The polygon to check. Points will be stored such that the
                first point stored is the first point in this polygon, but the
                rest of the polygon may be reversed to clockwise.
            target_size: If provided, will check against this size when checking
                side lengths. Otherwise, it will just make sure they are equal.
        """
        if len(polygon) != 4:
            raise WrongShapeError("Incorrect number of points.")

        if not geometry_utils.all_approx_square(polygon):
            raise WrongShapeError("Corners are not square.")

        side_lengths = geometry_utils.calc_side_lengths(polygon)
        if not math_utils.all_approx_equal(side_lengths, target_size):
            raise WrongShapeError("Side lengths are not equal or too far from target_size.")

        clockwise = geometry_utils.polygon_to_clockwise(polygon)
        if clockwise[0] is polygon[0]:
            self.polygon = clockwise
        else:
            self.polygon = list_utils.arrange_index_to_first(clockwise, len(clockwise) - 1)
        self.unit_length = math_utils.mean(side_lengths)


def find_corner_marks_new(image: np.ndarray):
    all_polygons: typing.List[geometry_utils.Polygon] = image_utils.find_polygons(image)

    # Even though the LMark and SquareMark classes check length, it's faster to
    # filter out the shapes of incorrect length despite the increased time
    # complexity.
    hexagons: typing.List[geometry_utils.Polygon] = []
    quadrilaterals: typing.List[geometry_utils.Polygon] = []
    for poly in all_polygons:
        if len(poly) == 6: hexagons.append(poly)
        if len(poly) == 4: quadrilaterals.append(poly)
    
    for hexagon in hexagons:
        try:
            l_mark = LMark(hexagon)
        except WrongShapeError:
            continue

        skew_angle = math.radians(5)
        ab = geometry_utils.line_from_points(hexagon[0], hexagon[1])
        upper_limit = geometry_utils.rotate_line(ab, skew_angle, hexagon[1])
        ab_offset = geometry_utils.offset_line(ab, hexagon[2])
        lower_limit = geometry_utils.rotate_line(ab_offset, -skew_angle, hexagon[2])
        nominal_distance = 45.58 * l_mark.unit_length
        distance_tolerance = 0.1
        b_prime_close = geometry_utils.extend_ray(hexagon[0], hexagon[1], (1 - distance_tolerance) * nominal_distance)
        b_prime_far = geometry_utils.extend_ray(hexagon[0], hexagon[1], (1 + distance_tolerance) * nominal_distance)
        close_limit = geometry_utils.get_perpendicular_line(ab, b_prime_close)
        far_limit = geometry_utils.get_perpendicular_line(ab, b_prime_far)
        is_in_box = geometry_utils.create_range_check_fn(
            (upper_limit)
        )
        
    




def find_corner_marks(image):
    all_polygons = image_utils.find_polygons(image)
    valid_polygons = []

    for poly in all_polygons:
        flat = list_utils.unnest(poly)
        if (len(poly) == 4
                or len(poly) == 6) and geometry_utils.all_approx_square(flat):
            valid_polygons.append(flat)

    l_s = []
    sq_s = []

    for poly in valid_polygons:
        is_l, l_info = is_l_mark(poly)
        if not is_l:
            continue
        l_s.append(poly)

        matching_squares = [
            p for p in valid_polygons if is_square(p, l_info[0])[0]
        ]

        longest_sides_point_indexes = list_utils.arrange_like_rays(
            *[[i, list_utils.next_index(poly, i)] for i in l_info[1]])
        offset_points_indexes = [
            list_utils.continue_index(poly, *indexes)
            for indexes in longest_sides_point_indexes
        ]

        longest_sides_vertexes = [[poly[i] for i in side]
                                  for side in longest_sides_point_indexes]
        offset_points = [poly[i] for i in offset_points_indexes]
        longest_side_lines = [
            geometry_utils.get_line(*vertexes)
            for vertexes in longest_sides_vertexes
        ]
        most_horizontal_index = geometry_utils.most_horizontal_line_index(
            longest_side_lines)
        most_horizontal_line = longest_side_lines[most_horizontal_index]
        most_horizontal_line_points = longest_sides_vertexes[
            most_horizontal_index]
        offset_point = offset_points[most_horizontal_index]
        offset_line = (most_horizontal_line[0], offset_point)
        flipped = is_l_flipped(most_horizontal_line_points, offset_point)
        skew = math.radians(3) if not flipped else math.radians(-3)
        rotated_lines = [
            geometry_utils.rotate_line(most_horizontal_line[0],
                                       most_horizontal_line_points[1], skew),
            geometry_utils.rotate_line(offset_line[0], offset_point, -skew)
        ]

        potential_right_corners = [
            sq for sq in matching_squares
            if geometry_utils.is_between_lines(sq[0], *rotated_lines)
        ]

        for sq in potential_right_corners:
            sq_s.append(sq)
    return l_s, sq_s


def is_l_flipped(horizontal_long_ray_points, next_point):
    corner = horizontal_long_ray_points[0]
    end = horizontal_long_ray_points[1]
    return (corner[0] < end[0]
            and next_point[1] > end[1]) or (corner[0] > end[1]
                                            and next_point[1] < end[1])


sample_img_location = pathlib.Path(
    "C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\four.jpg"
)
sample_image = image_utils.get_image(sample_img_location)
l_mark, right_squares = find_corner_marks(sample_image)
for square in right_squares:
    for point in square:
        cv2.circle(sample_image, tuple(point), 2, (0, 0, 255))
for l in l_mark:
    for point in l:
        cv2.circle(sample_image, tuple(point), 2, (255, 0, 0))
cv2.imshow("image", sample_image)
cv2.waitKey(0)
