import math
import pathlib

import cv2

import math_utils
import list_utils
import image_utils
import geometry_utils


def is_l_mark(contour):
    """Check if the contour is potentially a valid l mark."""
    if len(contour) != 6:
        return False, ()

    if not geometry_utils.all_approx_square(contour):
        return False, ()

    side_lengths = geometry_utils.calc_side_lengths(contour)
    longest_sides_indexes = list_utils.find_greatest_value_indexes(
        side_lengths, 2)

    if not list_utils.is_adjacent_indexes(
            side_lengths,
            *longest_sides_indexes,
    ):
        return False, ()

    # The longest sides should be about twice the length of the other sides
    unit_lengths = math_utils.divide_some(side_lengths, longest_sides_indexes,
                                          2)
    if not math_utils.all_approx_equal(unit_lengths):
        return False, ()

    return True, (math_utils.mean(unit_lengths), longest_sides_indexes)


def is_square(contour, size=None):
    """Check if the contour is potentially a valid l mark."""
    if len(contour) != 4:
        return False, ()

    if not geometry_utils.all_approx_square(contour):
        return False, ()

    side_lengths = geometry_utils.calc_side_lengths(contour)
    if not math_utils.all_approx_equal(side_lengths, size):
        return False, ()

    return True, (math_utils.mean(side_lengths))


def find_corner_marks(image):
    all_polygons = image_utils.find_polygons(image)
    valid_polygons = []

    for poly in all_polygons:
        flat = list_utils.unnest(poly)
        if (len(poly) == 4
                or len(poly) == 6) and geometry_utils.all_approx_square(flat):
            valid_polygons.append(flat)

    for poly in valid_polygons:
        is_l, l_info = is_l_mark(poly)
        if not is_l:
            continue

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

        if len(potential_right_corners) > 0:
            return poly, potential_right_corners
    return []


def is_l_flipped(horizontal_long_ray_points, next_point):
    corner = horizontal_long_ray_points[0]
    end = horizontal_long_ray_points[1]
    return (corner[0] < end[0]
            and next_point[1] > end[1]) or (corner[0] > end[1]
                                            and next_point[1] < end[1])


sample_img_location = pathlib.Path(
    "C:\\Users\\Ian Sanders\\Git Repositories\\scantron-reading\\examples\\left_corner_marks\\11.png"
)
sample_image = image_utils.get_image(sample_img_location)
l_mark, right_squares = find_corner_marks(sample_image)
for point in l_mark:
    cv2.circle(sample_image, tuple(point), 2, (255, 0, 0))
for square in right_squares:
    for point in square:
        cv2.circle(sample_image, tuple(point), 2, (0, 0, 255))
cv2.imshow("image", sample_image)
cv2.waitKey(0)
