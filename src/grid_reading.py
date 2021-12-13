"""Functions for establishing and reading the grid."""

# pyright: reportIncompatibleMethodOverride=false

import abc
import pathlib
import typing as tp

import cv2
import numpy as np
from numpy import ma

import alphabet
import geometry_utils
import grid_info
import image_utils
import list_utils

""" This is what determines the circle size of the grid cell mask. If it is 0,
the circle touches all edges of the grid cell. If it is 0.5, the circle is 50%
of the width and height of the cell (centered at the center of the cell.)

Notes:
 * Remember that the grid is not perfect.
 * If this is too large, you risk the circle enclosing part of another bubble
 or extraneous data.
 * If this is too small, it won't include the entire bubble. We want to include
 the entire bubble including the border, because all the bubbles are known to be
 the same size so if we include the entire bubble then we have around the same
 fill % for all of them.
"""
GRID_CELL_CROP_FRACTION = 0.25

# TODO: Import from geometry_utils when pyright#284 is fixed.
Polygon = tp.List[geometry_utils.Point]


class Grid:
    corners: Polygon
    horizontal_cells: int
    vertical_cells: int
    image: np.ndarray
    basis_transformer: geometry_utils.ChangeOfBasisTransformer

    def __init__(self,
                 corners: geometry_utils.Polygon,
                 horizontal_cells: int,
                 vertical_cells: int,
                 image: np.ndarray,
                 save_path: tp.Optional[pathlib.PurePath] = None):
        """Initiate a new Grid. Corners should be clockwise starting from the
        top left - if not, the grid will have unexpected behavior.

        If `save_path` is provided, will save the resulting image to this location
        as "grid.jpg". Used for debugging purposes."""
        self.corners = corners
        self.horizontal_cells = horizontal_cells
        self.vertical_cells = vertical_cells
        self.basis_transformer = geometry_utils.ChangeOfBasisTransformer(
            corners[0], corners[3], corners[2])

        self.horizontal_cell_size = 1 / self.horizontal_cells
        self.vertical_cell_size = 1 / self.vertical_cells

        self.image = image

        if save_path:
            image_utils.save_image(save_path / "grid.jpg", self.draw_grid())

    def _get_cell_shape_in_basis(self, across: int,
                                 down: int) -> geometry_utils.Polygon:
        return [
            geometry_utils.Point(across * self.horizontal_cell_size,
                                 down * self.vertical_cell_size),
            geometry_utils.Point((across + 1) * self.horizontal_cell_size,
                                 down * self.vertical_cell_size),
            geometry_utils.Point((across + 1) * self.horizontal_cell_size,
                                 (down + 1) * self.vertical_cell_size),
            geometry_utils.Point(across * self.horizontal_cell_size,
                                 (down + 1) * self.vertical_cell_size),
        ]


    def get_cell_range(self, across: int, down: int) -> tp.Tuple[tp.Tuple[float, float], tp.Tuple[float, float]]:
        """Get the range of x and y-dimensions that this cell touches, in the basis that the cell
        is given.
        
        Returns tuple of ((min_x, max_x), (min_y, max_y))"""
        cell = self.get_cell_shape(across, down)
        # Cannot just use the top-left and bottom-right points according to the polygon - what if
        # the cell is rotated 30 degrees? We want to use the absolute max and min coordinates.
        x_coords = [point.x for point in cell]
        y_coords = [point.y for point in cell]
        return (min(x_coords), max(x_coords)), (min(y_coords), max(y_coords))

    def get_cell_shape(self, across: int, down: int) -> geometry_utils.Polygon:
        """Get the shape of a cell using it's 0-based index. Returns the contour
        in CW direction starting with the top left cell."""
        return self.basis_transformer.poly_from_basis(self._get_cell_shape_in_basis(across, down))

    def get_unmasked_cell_matrix(self, across: int, down: int) -> np.ndarray:
        """Get the matrix of pixels in the grid cell area. Note if the grid is rotated, this will
        include pixels outside the cell since the cell will be a diamond and this will be a
        rectangle."""
        ((min_x, max_x), (min_y, max_y)) = self.get_cell_range(across, down)
        # Add 1 for inclusive indexing. Numpy will not accept even rounded floats as indexes.
        return self.image[
            int(round(min_y)):int(round(max_y + 1)),
            int(round(min_x)):int(round(max_x + 1))
]

    def get_cell_center(self, across: int, down: int) -> geometry_utils.Point:
        """Get the center point of the cell."""
        ((min_x, max_x), (min_y, max_y)) = self.get_cell_range(across, down)
        return geometry_utils.Point(min_x + ((max_x - min_x) / 2),
                                    min_y + ((max_y - min_y) / 2))

    def get_cell_circle(self, across: int,
                        down: int) -> tp.Tuple[geometry_utils.Point, float]:
        ((min_x, max_x), (min_y, max_y)) = self.get_cell_range(across, down)
        # If the cell is not perfectly square, base the circle size on the average dimension
        average_dimension = ((max_x - min_x) + (max_y - min_y)) / 2
        diameter = average_dimension * (1 - GRID_CELL_CROP_FRACTION)
        center = self.get_cell_center(across, down)
        return (center, diameter / 2)

    def get_masked_cell_matrix(self, across: int, down: int) -> ma.MaskedArray:
        """Get the matrix of pixels in the cell area, masked down to just the cell circle."""
        unmasked = self.get_unmasked_cell_matrix(across, down)
        mask = np.ones(unmasked.shape)
        unit_dimension = sum(mask.shape) / 2
        center = (round(mask.shape[0] / 2), round(mask.shape[1] / 2))
        circle_radius = (unit_dimension / 2) * (1 -
                                                (GRID_CELL_CROP_FRACTION / 2))
        cv2.circle(mask, center, int(circle_radius), (0, 0, 0), -1)
        masked = ma.masked_array(unmasked, mask)
        return masked

    def draw_grid(self):
        """Draws the grid on the image, returning a copy with red dots at grid
        points."""
        image = image_utils.bw_to_bgr(self.image)
        for x in range(self.horizontal_cells):
            for y in range(self.vertical_cells):
                points = self.get_cell_shape(x, y)
                for point in points:
                    cv2.circle(image,
                               (int(round(point.x)), int(round(point.y))), 2,
                               (0, 0, 255), -1)
                center, radius = self.get_cell_circle(x, y)
                cv2.circle(image, (int(round(center.x)), int(round(center.y))),
                           int(round(radius)), (255, 0, 0), 1)
        return image


class _GridField(abc.ABC):
    """A grid field is one set of grid cells that represents a value, ie a single
    letter or number."""

    horizontal_start_index: float
    vertical_start_index: float
    orientation: geometry_utils.Orientation
    num_cells: int
    grid: Grid

    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 orientation: geometry_utils.Orientation, num_cells: int):
        self.vertical_start = vertical_start
        self.horizontal_start = horizontal_start
        self.orientation = orientation
        self.num_cells = num_cells
        self.grid = grid

    @abc.abstractclassmethod
    def read_value(self, threshold: float, fill_percents: tp.List[float]
                   ) -> tp.Union[tp.List[str], tp.List[int]]:
        ...

    def _read_value_indexes(self, threshold: float,
                            fill_percents: tp.List[float]) -> tp.List[int]:
        filled = [
            i for i in range(self.num_cells) if fill_percents[i] > threshold
        ]
        return filled

    def get_cell_matrixes(self) -> tp.List[ma.MaskedArray]:
        results: tp.List[ma.MaskedArray] = []
        is_vertical = self.orientation is geometry_utils.Orientation.VERTICAL
        for i in range(self.num_cells):
            x = self.horizontal_start if is_vertical else self.horizontal_start + i
            y = self.vertical_start if not is_vertical else self.vertical_start + i

            # Have to crop the edges to avoid getting the borders of the write-in
            # squares in the cells
            matrix = self.grid.get_masked_cell_matrix(x, y)

            results.append(matrix)
        return results

    def get_all_fill_percents(self) -> tp.List[float]:
        results = [
            image_utils.get_fill_percent(square)
            for square in self.get_cell_matrixes()
        ]
        return results


class NumberGridField(_GridField):
    """A number grid field is one set of grid cells that represents a digit."""
    def read_value(self, threshold: float,
                   fill_percents: tp.List[float]) -> tp.List[int]:
        return super()._read_value_indexes(threshold, fill_percents)


class LetterGridField(_GridField):
    """A number grid field is one set of grid cells that represents a letter."""
    def read_value(self, threshold: float,
                   fill_percents: tp.List[float]) -> tp.List[str]:
        return [
            alphabet.letters[i]
            for i in super()._read_value_indexes(threshold, fill_percents)
        ]


class _GridFieldGroup(abc.ABC):
    """A grid field group is a group of grid fields, ie a word. Do not use
    directly."""

    fields: tp.Sequence[_GridField]

    @abc.abstractclassmethod
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 num_fields: int, field_length: int,
                 field_orientation: geometry_utils.Orientation):
        ...

    def read_value(self, threshold: float,
                   fill_percents: tp.List[tp.List[float]]
                   ) -> tp.List[tp.Union[tp.List[str], tp.List[int]]]:
        """Calculate the field value using precalculated fill percents."""
        return [
            field.read_value(threshold, fill_percents[i])
            for i, field in enumerate(self.fields)
        ]

    def get_all_fill_percents(self) -> tp.List[tp.List[float]]:
        return [field.get_all_fill_percents() for field in self.fields]


class NumberGridFieldGroup(_GridFieldGroup):
    """A number grid field group is one group of fields that represents an
    entire number."""
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 num_fields: int, field_length: int,
                 field_orientation: geometry_utils.Orientation):
        fields_vertical = field_orientation is geometry_utils.Orientation.VERTICAL
        self.fields = [
            NumberGridField(
                grid,
                horizontal_start + i if fields_vertical else horizontal_start,
                vertical_start + i if not fields_vertical else vertical_start,
                field_orientation, field_length) for i in range(num_fields)
        ]

    def read_value(self, threshold: float,
                   fill_percents: tp.List[tp.List[float]]
                   ) -> tp.List[tp.List[int]]:
        return tp.cast(tp.List[tp.List[int]],
                       super().read_value(threshold, fill_percents))


class LetterGridFieldGroup(_GridFieldGroup):
    """A letter grid field group is one group of fields that represents an
    entire string."""
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 num_fields: int, field_length: int,
                 field_orientation: geometry_utils.Orientation):
        fields_vertical = field_orientation is geometry_utils.Orientation.VERTICAL
        self.fields = [
            LetterGridField(
                grid,
                horizontal_start + i if fields_vertical else horizontal_start,
                vertical_start + i if not fields_vertical else vertical_start,
                field_orientation, field_length) for i in range(num_fields)
        ]

    def read_value(self, threshold: float,
                   fill_percents: tp.List[tp.List[float]]
                   ) -> tp.List[tp.List[str]]:
        return tp.cast(tp.List[tp.List[str]],
                       super().read_value(threshold, fill_percents))


def get_group_from_info(info: grid_info.GridGroupInfo,
                        grid: Grid) -> _GridFieldGroup:
    if info.fields_type is grid_info.FieldType.LETTER:
        return LetterGridFieldGroup(grid, info.horizontal_start,
                                    info.vertical_start, info.num_fields,
                                    info.field_length, info.field_orientation)
    else:
        return NumberGridFieldGroup(grid, info.horizontal_start,
                                    info.vertical_start, info.num_fields,
                                    info.field_length, info.field_orientation)


def read_field(field: grid_info.Field, grid: Grid, threshold: float,
               form_variant: grid_info.FormVariant,
               fill_percents: tp.List[tp.List[float]]
               ) -> tp.Optional[tp.List[tp.Union[tp.List[str], tp.List[int]]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    grid_group_info = form_variant.fields[field]
    if grid_group_info is not None:
        return get_group_from_info(grid_group_info,
                                   grid).read_value(threshold, fill_percents)
    else:
        return None


def read_answer(question: int, grid: Grid, threshold: float,
                form_variant: grid_info.FormVariant,
                fill_percents: tp.List[tp.List[float]]
                ) -> tp.List[tp.Union[tp.List[str], tp.List[int]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    return get_group_from_info(form_variant.questions[question],
                               grid).read_value(threshold, fill_percents)


def field_group_to_string(
        values: tp.List[tp.Union[tp.List[str], tp.List[int]]]):
    result_strings: tp.List[str] = []
    for value in values:
        if len(value) == 0:
            result_strings.append(' ')
        elif len(value) == 1:
            result_strings.append(str(value[0]))
        else:
            value_as_strings = [str(el) for el in value]
            result_strings.append(f'[{"|".join(value_as_strings)}]')
    return "".join(result_strings).strip()


def read_field_as_string(field: grid_info.Field, grid: Grid, threshold: float,
                         form_variant: grid_info.FormVariant,
                         fill_percents: tp.List[tp.List[float]]
                         ) -> tp.Optional[str]:
    """Shortcut to read a field and format it as a string, given just the key and
    the grid object. """
    field_group = read_field(field, grid, threshold, form_variant,
                             fill_percents)
    if field_group is not None:
        return field_group_to_string(field_group)
    else:
        return None


def read_answer_as_string(question: int, grid: Grid, multi_answers_as_f: bool,
                          threshold: float,
                          form_variant: grid_info.FormVariant,
                          fill_percents: tp.List[tp.List[float]]) -> str:
    """Shortcut to read a question's answer and format it as a string, given
    just the question number and the grid object. """
    answer = field_group_to_string(
        read_answer(question, grid, threshold, form_variant, fill_percents))
    if not multi_answers_as_f or "|" not in answer:
        return answer
    else:
        return "F"


def calculate_bubble_fill_threshold(
        field_fill_percents: tp.Dict[grid_info.Field, tp.List[tp.List[float]]],
        answer_fill_percents: tp.List[tp.List[tp.List[float]]],
        form_variant: grid_info.FormVariant,
        save_path: tp.Optional[pathlib.PurePath] = None) -> float:
    """Dynamically calculate the threshold to use for determining if a bubble is
    filled or unfilled.

    This is a time consuming function so it should only be called once per page.
    It works by getting the fill percentages of all the values in all the
    fields, sorting them, and finding the largest increase in fill percent
    between all the values in the highest 1/4 (assumes all the filled bubbles
    are less than 1/4 of all the bubbles). It then returns the average of the
    two values that were subtracted to make the largest increase.

    If `save_path` is provided, saves debugging data to this location as
    "threshold_values.txt".
    """
    fill_percents_lists = list(
        field_fill_percents.values()) + answer_fill_percents
    fill_percents = [np.array(l).flatten() for l in fill_percents_lists]
    sorted_and_flattened = np.sort(np.concatenate(fill_percents))
    last_chunk = sorted_and_flattened[-round(sorted_and_flattened.size / 5):]
    differences = [
        last_chunk[i + 1] - last_chunk[i] for i in range(last_chunk.size - 1)
    ]
    biggest_diff_index = list_utils.find_greatest_value_indexes(
        differences, 1)[0]
    result = (last_chunk[biggest_diff_index] +
              last_chunk[biggest_diff_index + 1]) / 2
    if save_path:
        with open(str(save_path / "threshold_values.txt"), "w+") as file:
            file.writelines([str(sorted_and_flattened), "\n\n", str(result)])
    return result
