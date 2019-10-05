"""Functions for establishing and reading the grid."""

import geometry_utils
import math
import typing
import image_utils
import numpy as np
import enum
import alphabet
import abc
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


class FieldType(enum.Enum):
    LETTER = enum.auto()
    NUMBER = enum.auto()


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

    def read_value(self) -> typing.List[list]:
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
        return super().read_value()


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
        return super().read_value()


class GridGroupInfo():
    """Metadata about a set of grid cells (not tide to a specific grid or image)."""

    horizontal_start: int
    vertical_start: int
    num_fields: int
    field_length: int
    fields_type: FieldType
    field_orientation: geometry_utils.Orientation

    def __init__(self,
                 horizontal_start: int,
                 vertical_start: int,
                 num_fields: int = 1,
                 fields_type: FieldType = FieldType.NUMBER,
                 field_length: typing.Optional[int] = None,
                 field_orientation: geometry_utils.
                 Orientation = geometry_utils.Orientation.VERTICAL):
        self.horizontal_start = horizontal_start
        self.vertical_start = vertical_start
        self.num_fields = num_fields
        if field_length is not None:
            self.field_length = field_length
        elif fields_type is FieldType.LETTER:
            self.field_length = alphabet.LENGTH
        else:
            self.field_length = 10
        self.fields_type = fields_type
        self.field_orientation = field_orientation

    def get_group(self, grid: Grid) -> _GridFieldGroup:
        if self.fields_type is FieldType.LETTER:
            return LetterGridFieldGroup(grid, self.horizontal_start,
                                        self.vertical_start, self.num_fields,
                                        self.field_length,
                                        self.field_orientation)
        else:
            return NumberGridFieldGroup(grid, self.horizontal_start,
                                        self.vertical_start, self.num_fields,
                                        self.field_length,
                                        self.field_orientation)
