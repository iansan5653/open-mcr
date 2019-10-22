"""Functions for establishing and reading the grid."""

import abc
import math
import typing

import numpy as np

import alphabet
import geometry_utils
import grid_info
import image_utils

""" Percent fill past which a grid cell is considered filled."""
GRID_CELL_FILL_THRESHOLD = 0.54
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
    image: np.array

    def __init__(self, corners: geometry_utils.Polygon, horizontal_cells: int,
                 vertical_cells: int, image: np.array):
        """Initiate a new Grid. Corners should be clockwise starting from the
        top left - if not, the grid will have unexpected behavior. """
        self.corners = corners
        self.horizontal_cells = horizontal_cells
        self.vertical_cells = vertical_cells
        [a, b] = corners[0:2]
        theta = math.atan2(b.y - a.y, b.x - a.x)
        self._to_grid_basis, self._from_grid_basis = geometry_utils.create_change_of_basis(
            corners[0], theta)

        corners_in_basis = [self._to_grid_basis(c) for c in corners]
        self.width = corners_in_basis[1].x
        self.height = corners_in_basis[3].y

        self.horizontal_cell_size = self.width / self.horizontal_cells
        self.vertical_cell_size = self.height / self.vertical_cells

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

    def get_cropped_cell_shape(self, across: int, down: int,
                               crop_fraction: float) -> geometry_utils.Polygon:
        uncropped = self._get_cell_shape_in_basis(across, down)
        top_left, bottom_right = geometry_utils.crop_rectangle(
            uncropped[0], uncropped[2], crop_fraction)
        shape = [
            top_left,
            geometry_utils.Point(bottom_right.x, top_left.y), bottom_right,
            geometry_utils.Point(top_left.x, bottom_right.y)
        ]
        return [self._from_grid_basis(p) for p in shape]

    def get_cell_center(self, across: int, down: int) -> geometry_utils.Point:
        """Get the center point of a cell using it's 0-based index."""
        return self._from_grid_basis(
            geometry_utils.Point((across + 0.5) * self.horizontal_cell_size,
                                 (down + 0.5) * self.horizontal_cell_size))


class _GridField(abc.ABC):
    """A grid field is one set of grid cells that represents a value, ie a single
    letter or number. Do not use directly."""

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
    def read_value(self) -> typing.Union[typing.List[str], typing.List[int]]:
        ...

    def _read_value_indexes(self) -> typing.List[int]:
        filled = []
        for i, square in enumerate(self.get_cell_shapes()):
            is_filled = image_utils.get_fill_percent(
                self.grid.image, square[0],
                square[2]) > GRID_CELL_FILL_THRESHOLD
            if is_filled:
                filled.append(i)
        return filled

    def get_cell_shapes(self) -> typing.List[Polygon]:
        results: typing.List[Polygon] = []
        is_vertical = self.orientation is geometry_utils.Orientation.VERTICAL
        for i in range(self.num_cells):
            x = self.horizontal_start if is_vertical else self.horizontal_start + i
            y = self.vertical_start if not is_vertical else self.vertical_start + i

            # Have to crop the edges to avoid getting the borders of the write-in
            # squares in the cells
            square = self.grid.get_cropped_cell_shape(x, y,
                                                      GRID_CELL_CROP_FRACTION)

            results.append(square)
        return results


class NumberGridField(_GridField):
    """A number grid field is one set of grid cells that represents a digit."""
    def read_value(self) -> typing.List[int]:
        return super()._read_value_indexes()


class LetterGridField(_GridField):
    """A number grid field is one set of grid cells that represents a letter."""
    def read_value(self) -> typing.List[str]:
        return [alphabet.letters[i] for i in super()._read_value_indexes()]


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
            self
    ) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
        return [field.read_value() for field in self.fields]


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

    def read_value(self) -> typing.List[typing.List[int]]:
        return typing.cast(typing.List[typing.List[int]], super().read_value())


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

    def read_value(self) -> typing.List[typing.List[str]]:
        return typing.cast(typing.List[typing.List[str]], super().read_value())


def get_group_from_info(info: grid_info.GridGroupInfo, grid: Grid) -> _GridFieldGroup:
    if info.fields_type is grid_info.FieldType.LETTER:
        return LetterGridFieldGroup(grid, info.horizontal_start,
                                    info.vertical_start, info.num_fields,
                                    info.field_length,
                                    info.field_orientation)
    else:
        return NumberGridFieldGroup(grid, info.horizontal_start,
                                    info.vertical_start, info.num_fields,
                                    info.field_length,
                                    info.field_orientation)


def read_field(
        field: grid_info.Field, grid: Grid
) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    return get_group_from_info(grid_info.fields_info[field], grid).read_value()


def read_answer(
        question: int, grid: Grid
) -> typing.List[typing.Union[typing.List[str], typing.List[int]]]:
    """Shortcut to read a field given just the key for it and the grid object."""
    return get_group_from_info(grid_info.questions_info[question], grid).read_value()


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


def read_field_as_string(field: grid_info.Field, grid: Grid) -> str:
    """Shortcut to read a field and format it as a string, given just the key and
    the grid object. """
    return field_group_to_string(read_field(field, grid))


def read_answer_as_string(question: int, grid: Grid, multi_answers_as_f: bool) -> str:
    """Shortcut to read a question's answer and format it as a string, given
    just the question number and the grid object. """
    answer = field_group_to_string(read_answer(question, grid))
    if not multi_answers_as_f or "|" not in answer:
        return answer
    else:
        return "F"
