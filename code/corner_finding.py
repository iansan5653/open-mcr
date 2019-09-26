import math
import typing
from pathlib import Path, PurePath

import cv2
import numpy as np

from . import math_utils
from . import list_utils
from . import image_utils
from . import geometry_utils


def is_l_mark(contour):
    """Check if the contour is potentially a valid l mark."""
    if len(contour) != 6:
        return False, ()

    if not geometry_utils.all_approx_square(contour):
        return False, ()

    side_lengths = geometry_utils.calc_side_lengths(contour)
    longest_sides_indexes = list_utils.find_greatest_value_indexes(side_lengths, 2)

    if not list_utils.is_adjacent_indexes(*longest_sides_indexes, side_lengths):
        return False, ()

    # The longest sides should be about twice the length of the other sides
    unit_lengths = math_utils.divide_some(side_lengths, longest_sides_indexes, 2)
    if not math_utils.all_approx_equal(unit_lengths):
        return False, ()

    return True, (math_utils.mean(unit_lengths), longest_sides_indexes)


def is_square(contour):
    """Check if the contour is potentially a valid l mark."""
    if len(contour) != 4:
        return False, ()

    if not geometry_utils.all_approx_square(contour):
        return False, ()

    side_lengths = geometry_utils.calc_side_lengths(contour)
    if not math_utils.all_approx_equal(side_lengths):
        return False, ()

    return True, (math_utils.mean(side_lengths))


def find_corner_marks(image):
    all_polygons = image_utils.find_polygons(image)
    valid_polygons = []
    for poly in all_polygons:
        flat = list_utils.unnest(poly)
        if geometry_utils.all_approx_square(flat):
            valid_polygons.append(flat)

    for poly in valid_polygons:
        is_l, l_info = is_l_mark(poly)
        if not is_l:
            continue
        
        longest_sides_point_indexes = list_utils.arrange_like_rays([[i, list_utils.next_index(poly, i)] for i in l_info[1]])
        offset_points_indexes = [list_utils.continue_index(poly, *indexes) for indexes in longest_sides_point_indexes]

        




sample_img_location = Path(
    __file__).parent.parent / "examples" / "left_corner_marks" / "11.png"
sample_image = get_image(sample_img_location)
all_polygons = find_polygons(sample_image)
top_left_mark = find_top_left_corner_mark(all_polygons)
red = (0, 0, 255)
cv2.drawContours(sample_image, [top_left_mark], -1, red, 1)
all_squares = find_squares(all_polygons)
blue = (255, 0, 0)
cv2.drawContours(sample_image, all_squares, -1, blue, 1)
cv2.imshow("image", sample_image)
cv2.waitKey(0)
