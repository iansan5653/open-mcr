"""Functions for establishing and reading the grid."""

import abc
import typing

import cv2
import numpy as np
from numpy import ma

import alphabet
import geometry_utils
import grid_info
import image_utils
import list_utils

""" Percent fill past which a grid cell is considered filled. If the empty Ws
are being read as filled, increase this."""
GRID_CELL_FILL_THRESHOLD = 0.59
""" This is what determines the circle size of the grid cell mask. If it is 1.0, 
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
GRID_CELL_CROP_FRACTION = 0.4

# TODO: Import from geometry_utils when pyright#284 is fixed.
Polygon = typing.List[geometry_utils.Point]


class Grid:
    corners: Polygon
    horizontal_cells: int
    vertical_cells: int
    _to_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                    Point]
    _from_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                      Point]
    image: np.ndarray

    def __init__(self, corners: geometry_utils.Polygon, horizontal_cells: int,
                 vertical_cells: int, image: np.ndarray):
        """Initiate a new Grid. Corners should be clockwise starting from the
        top left - if not, the grid will have unexpected behavior. """
        self.corners = corners
        self.horizontal_cells = horizontal_cells
        self.vertical_cells = vertical_cells
        self._to_grid_basis, self._from_grid_basis = geometry_utils.create_change_of_basis(
            corners[0], corners[3], corners[2])

        self.horizontal_cell_size = 1 / self.horizontal_cells
        self.vertical_cell_size = 1 / self.vertical_cells

        self.image = image

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

    def get_cell_shape(self, across: int, down: int) -> geometry_utils.Polygon:
        """Get the shape of a cell using it's 0-based index. Returns the contour
        in CW direction starting with the top left cell."""
        return [
            self._from_grid_basis(p)
            for p in self._get_cell_shape_in_basis(across, down)
        ]

    def get_unmasked_cell_matrix(self, across: int, down: int) -> np.ndarray:
        [top_left_point, _, bottom_right_point,
         _] = self.get_cell_shape(across, down)
        # +1 because indexing doesn't include the last number (ie, [1,2,3,4][1:3] ->
        # [2,3]) and we want that last row / column.
        x_range = (int(top_left_point.x), int(bottom_right_point.x) + 1)
        y_range = (int(top_left_point.y), int(bottom_right_point.y) + 1)
        return self.image[y_range[0]:y_range[1], x_range[0]:x_range[1]]

    def get_masked_cell_matrix(self, across: int, down: int) -> ma.MaskedArray:
        unmasked = self.get_unmasked_cell_matrix(across, down)
        mask = np.ones(unmasked.shape)
        unit_dimension = sum(mask.shape) / 2
        center = (round(mask.shape[0] / 2), round(mask.shape[1] / 2))
        circle_radius = (unit_dimension / 2) * (1 -
                                                (GRID_CELL_CROP_FRACTION / 2))
        cv2.circle(mask, center, int(circle_radius), (0, 0, 0), -1)
        masked = ma.masked_array(unmasked, mask)
        return masked


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
    def read_value(self, threshold: float
                   ) -> typing.Union[typing.List[str], typing.List[int]]:
        ...

    def _read_value_indexes(self, threshold: float) -> typing.List[int]:
        filled = []
        for i, matrix in enumerate(self.get_cell_matrixes()):
            is_filled = image_utils.get_fill_percent(matrix) > threshold
            if is_filled:
                filled.append(i)
        return filled

    def get_cell_matrixes(self) -> typing.List[ma.MaskedArray]:
        results: typing.List[ma.MaskedArray] = []
        is_vertical = self.orientation is geometry_utils.Orientation.VERTICAL
        for i in range(self.num_cells):
            x = self.horizontal_start if is_vertical else self.horizontal_start + i
            y = self.vertical_start if not is_vertical else self.vertical_start + i

            # Have to crop the edges to avoid getting the borders of the write-in
            # squares in the cells
            matrix = self.grid.get_masked_cell_matrix(x, y)

            results.append(matrix)
        return results

    def get_all_fill_percents(self) -> typing.List[float]:
        results = [
            image_utils.get_fill_percent(square)
            for square in self.get_cell_matrixes()
        ]
        return results


class NumberGridField(_GridField):
    """A number grid field is one set of grid cells that represents a digit."""
    def read_value(self, threshold: float) -> typing.List[int]:
        return super()._read_value_indexes(threshold)


class LetterGridField(_GridField):
    """A number grid field is one set of grid cells that represents a letter."""
    def read_value(self, threshold: float) -> typing.List[str]:
        return [
            alphabet.letters[i] for i in super()._read_value_indexes(threshold)
        ]


class _GridFieldGroup(abc.ABC):
    """A grid field group is a group of grid fields, ie a word. Do not use
    directly."""

    fields: typing.Sequence[_GridField]

    @abc.abstractclassmethod
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 num_fields: int, field_length: int,
                 field_orientation: geometry_utils.Orientation):
        ...

    def read_value(
            self, threshold: float
    ) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
        return [field.read_value(threshold) for field in self.fields]

    def get_all_fill_percents(self) -> typing.List[typing.List[float]]:
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

    def read_value(self, threshold: float) -> typing.List[typing.List[int]]:
        return typing.cast(typing.List[typing.List[int]],
                           super().read_value(threshold))


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

    def read_value(self, threshold: float) -> typing.List[typing.List[str]]:
        return typing.cast(typing.List[typing.List[str]],
                           super().read_value(threshold))


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


def read_field(
        field: grid_info.Field, grid: Grid, threshold: float
) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    return get_group_from_info(grid_info.fields_info[field],
                               grid).read_value(threshold)


def read_answer(
        question: int, grid: Grid, threshold: float
) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    return get_group_from_info(grid_info.questions_info[question],
                               grid).read_value(threshold)


def field_group_to_string(
        values: typing.List[typing.Union[typing.List[str], typing.List[int]]]):
    result_strings: typing.List[str] = []
    for value in values:
        if len(value) == 0:
            result_strings.append(' ')
        elif len(value) == 1:
            result_strings.append(str(value[0]))
        else:
            value_as_strings = [str(el) for el in value]
            result_strings.append(f'[{"|".join(value_as_strings)}]')
    return "".join(result_strings).strip()


def read_field_as_string(field: grid_info.Field, grid: Grid,
                         threshold: float) -> str:
    """Shortcut to read a field and format it as a string, given just the key and
    the grid object. """
    return field_group_to_string(read_field(field, grid, threshold))


def read_answer_as_string(question: int, grid: Grid, multi_answers_as_f: bool,
                          threshold: float) -> str:
    """Shortcut to read a question's answer and format it as a string, given
    just the question number and the grid object. """
    answer = field_group_to_string(read_answer(question, grid, threshold))
    if not multi_answers_as_f or "|" not in answer:
        return answer
    else:
        return "F"


def calculate_bubble_fill_threshold(grid: Grid) -> float:
    """Dynamically calculate the threshold to use for determining if a bubble is
    filled or unfilled.

    This is a time consuming function so it should only be called once per page.
    It works by getting the fill percentages of all the values in all the name
    fields, sorting them, and finding the largest increase in fill percent
    between all the values in the highest 1/4 (assumes all the filled bubbles
    are less than 1/4 of all the bubbles). It then returns the average of the
    two values that were subtracted to make the largest increase.
    """
    # This function makes the following assumptions:
    # A. At least one bubble in first, last, or middle name is full.
    # B. Less than a tenth of the bubbles in first, last, and middle name are
    #    full. For this to be untrue, an average of 2.6 bubbles per field would
    #    be filled which doesn't make sense for anyone to do.
    # If these are not true, the values for the entire sheet will be useless.
    # However, these are most likely safe assumptions.
    fill_percents = [
        np.array(get_group_from_info(grid_info.fields_info[field], grid).get_all_fill_percents()).flatten()
        for field in [grid_info.Field.LAST_NAME, grid_info.Field.FIRST_NAME, grid_info.Field.MIDDLE_NAME]
    ]
    sorted_and_flattened = np.sort(np.concatenate(fill_percents))
    last_chunk = sorted_and_flattened[-round(sorted_and_flattened.size / 10):]
    differences = [
        last_chunk[i + 1] - last_chunk[i] for i in range(last_chunk.size - 1)
    ]
    biggest_diff_index = list_utils.find_greatest_value_indexes(
        differences, 1)[0]
    return (last_chunk[biggest_diff_index] +
            last_chunk[biggest_diff_index + 1]) / 2
