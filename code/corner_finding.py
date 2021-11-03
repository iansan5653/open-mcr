import typing

import numpy as np

import geometry_utils
import image_utils
import list_utils
import math_utils
import pathlib


class WrongShapeError(ValueError):
    pass


class CornerFindingError(RuntimeError):
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
            clockwise_polygon,
            list_utils.determine_which_is_next(polygon,
                                               *longest_sides_indexes))
        self.unit_length = math_utils.mean(unit_lengths)


class SquareMark:
    """An L-shaped polygon.

    Members:
        polygon: The list of points representing the mark. Points are stored in
            a clockwise direction.
        unit_length: The estimated grid square unit length that the mark is
            built with.
    """
    def __init__(self,
                 polygon: geometry_utils.Polygon,
                 target_size: typing.Optional[float] = None):
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
            raise WrongShapeError(
                "Side lengths are not equal or too far from target_size.")

        clockwise = geometry_utils.polygon_to_clockwise(polygon)
        if clockwise[0] is polygon[0]:
            self.polygon = clockwise
        else:
            self.polygon = list_utils.arrange_index_to_first(
                clockwise,
                len(clockwise) - 1)
        self.unit_length = math_utils.mean(side_lengths)


def find_corner_marks(image: np.ndarray,
                      save_path: typing.Optional[pathlib.PurePath] = None
                      ) -> geometry_utils.Polygon:

    all_polygons: typing.List[
        geometry_utils.Polygon] = image_utils.find_polygons(
            image, save_path=save_path)

    # Even though the LMark and SquareMark classes check length, it's faster to
    # filter out the shapes of incorrect length despite the increased time
    # complexity.
    hexagons: typing.List[geometry_utils.Polygon] = []
    quadrilaterals: typing.List[geometry_utils.Polygon] = []
    for poly in all_polygons:
        if len(poly) == 6:
            hexagons.append(poly)
        elif len(poly) == 4:
            quadrilaterals.append(poly)

    if save_path:
        image_utils.draw_polygons(image, hexagons, save_path / "all_hexagons.jpg")
        image_utils.draw_polygons(image, quadrilaterals, save_path / "all_quadrilaterals.jpg")

    for i in range(len(hexagons)):
        hexagon = hexagons[i]

        try:
            l_mark = LMark(hexagon)
        except WrongShapeError:
            continue

        # To construct the basis, we use points 0, 4, 5 of the L. The points are in CW order from
        # the top-left corner, so these are the top-left, bottom-left, and bottom-right-of-bottom-side
        # points. 
        basis_transformer = geometry_utils.ChangeOfBasisTransformer(
            l_mark.polygon[0], l_mark.polygon[5], l_mark.polygon[4])
        nominal_to_right_side = 50 - 0.5
        # Since the side of the L is twice as long as it is wide, divide y by two as the new-basis
        # system will be squashed
        nominal_to_bottom = ((64 - 0.5) / 2)
        # We can afford to allow a decently large error margin here since we are just searching for
        # reference points and the rough coordinate system established based on the L is very
        # sensitive to noise.
        x_tolerance = 0.2 * nominal_to_right_side
        y_tolerance = 0.2 * nominal_to_bottom


        top_right_squares = []
        bottom_left_squares = []
        bottom_right_squares = []

        if save_path:
            # Purely for diagnostic output - save the grid tolerance boxes to a file. This is
            # complicated, but useful for debugging and only is enabled when requested.
            # Nominal polygon of edges
            nominal_poly_new_basis = [
                geometry_utils.Point(0.0, 0.0),
                geometry_utils.Point(nominal_to_right_side, 0.0),
                geometry_utils.Point(nominal_to_right_side, nominal_to_bottom),
                geometry_utils.Point(0.0, nominal_to_bottom)
            ]
            # Boxes within which corner centroids can be found
            corner_tolerance_polys_new_basis = [
                [
                    geometry_utils.Point(x + x_tolerance, y - y_tolerance),
                    geometry_utils.Point(x + x_tolerance, y + y_tolerance),
                    geometry_utils.Point(x - x_tolerance, y + y_tolerance),
                    geometry_utils.Point(x - x_tolerance, y - y_tolerance)
                ] for [x, y] in [
                    [nominal_to_right_side, 0.5],
                    [nominal_to_right_side, nominal_to_bottom],
                    [0.5, nominal_to_bottom]
                ]
            ]
            polys = [basis_transformer.poly_from_basis(nominal_poly_new_basis), hexagon] + [
                basis_transformer.poly_from_basis(p) for p in corner_tolerance_polys_new_basis
            ]
            image_utils.draw_polygons(
                image,
                polys,
                save_path / f"grid_corner_tolerances_{i}.png",
                thickness=2
            )

        for quadrilateral in quadrilaterals:
            try:
                square = SquareMark(quadrilateral, l_mark.unit_length)
            except WrongShapeError:
                continue
            centroid = geometry_utils.guess_centroid(square.polygon)
            centroid_new_basis = basis_transformer.to_basis(centroid)

            if math_utils.is_within_tolerance(
                    centroid_new_basis.x, nominal_to_right_side,
                    x_tolerance) and math_utils.is_within_tolerance(
                        centroid_new_basis.y, 0.5, y_tolerance):
                top_right_squares.append(square)
            elif math_utils.is_within_tolerance(
                    centroid_new_basis.x, 0.5,
                    x_tolerance) and math_utils.is_within_tolerance(
                        centroid_new_basis.y, nominal_to_bottom, y_tolerance):
                bottom_left_squares.append(square)
            elif math_utils.is_within_tolerance(
                    centroid_new_basis.x, nominal_to_right_side,
                    x_tolerance) and math_utils.is_within_tolerance(
                        centroid_new_basis.y, nominal_to_bottom, y_tolerance):
                bottom_right_squares.append(square)

        if len(top_right_squares) == 0 or len(bottom_left_squares) == 0 or len(
                bottom_right_squares) == 0:
            continue

        # TODO: When multiple, either progressively decrease tolerance or
        # choose closest to centroid

        top_left_corner = l_mark.polygon[0]
        top_right_corner = geometry_utils.get_corner_wrt_basis(
            top_right_squares[0].polygon, geometry_utils.Corner.TR, basis_transformer)
        bottom_right_corner = geometry_utils.get_corner_wrt_basis(
            bottom_right_squares[0].polygon, geometry_utils.Corner.BR, basis_transformer)
        bottom_left_corner = geometry_utils.get_corner_wrt_basis(
            bottom_left_squares[0].polygon, geometry_utils.Corner.BL, basis_transformer)

        grid_corners = [
            top_left_corner,     top_right_corner,
            bottom_right_corner, bottom_left_corner
        ]   

        if save_path:
            image_utils.draw_polygons(image, [grid_corners], save_path / "grid_limits.jpg")

        return grid_corners
    raise CornerFindingError("Couldn't find document corners.")
