"""Functions for establishing and reading the grid."""

import geometry_utils
import math
import typing
import image_utils
import numpy as np
from alphabet import letters


class Grid:
    corners: geometry_utils.Polygon
    horizontal_cells: int
    vertical_cells: int
    _to_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                    Point]
    _from_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                      Point]
    image: np.ndarray

    def __init__(self, corners, horizontal_cells: int, vertical_cells: int, image):
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

    def get_cell_shape(self, across: int, down: int) -> geometry_utils.Polygon:
        points_in_basis = [
            geometry_utils.Point(across * self.horizontal_cell_size,
                                 down * self.horizontal_cell_size),
            geometry_utils.Point((across + 1) * self.horizontal_cell_size,
                                 down * self.horizontal_cell_size),
            geometry_utils.Point((across + 1) * self.horizontal_cell_size,
                                 (down + 1) * self.horizontal_cell_size),
            geometry_utils.Point(across * self.horizontal_cell_size,
                                 (down + 1) * self.horizontal_cell_size),
        ]
        return [self._from_grid_basis(p) for p in points_in_basis]

    def get_cell_center(self, across: int, down: int) -> geometry_utils.Point:
        return self._from_grid_basis(
            geometry_utils.Point((across + 0.5) * self.horizontal_cell_size,
                                 (down + 0.5) * self.horizontal_cell_size))

    def get_all_centers(self) -> geometry_utils.Polygon:
        result = []
        for x in range(self.horizontal_cells):
            for y in range(self.vertical_cells):
                result.append(self.get_cell_center(x, y))
        return result

    def get_all_shapes(self) -> typing.List[geometry_utils.Polygon]:
        result = []
        for x in range(self.horizontal_cells):
            for y in range(self.vertical_cells):
                result.append(self.get_cell_shape(x, y))
        return result


class GridRange:
    horizontal_start_index: float
    vertical_start_index: float
    is_vertical: bool = True
    num_cells: int
    grid: Grid

    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int,
                 is_vertical: bool, num_cells: int):
        self.vertical_start = vertical_start
        self.horizontal_start = horizontal_start
        self.is_vertical = is_vertical
        self.num_cells = num_cells
        self.grid = grid

    def read_value(self):
        filled = []
        for i in range(self.num_cells):
            x = self.horizontal_start if self.is_vertical else self.horizontal_start + i
            y = self.vertical_start if not self.is_vertical else self.vertical_start + i

            square = self.grid.get_cell_shape(x, y)
            is_filled = image_utils.get_fill_percent(self.grid.image, square) > 0.2
            if is_filled:
                filled.append(i)

        return filled


class AlphabetGridRange(GridRange):
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int):
        super().__init__(grid, horizontal_start, vertical_start, True, 26)

    def read_value(self):
        values = super().read_value()
        return [letters[index] for index in values]


class NumericGridRange(GridRange):
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int):
        super().__init__(grid, horizontal_start, vertical_start, True, 10)


class AnswerGridRange(GridRange):
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int):
        super().__init__(grid, horizontal_start, vertical_start, False, 5)


class FormCodeGridRange(GridRange):
    def __init__(self, grid: Grid, horizontal_start: int, vertical_start: int):
        super.__init__(grid, horizontal_start, vertical_start, False, 6)


GridGroup = typing.List[GridRange]


def make_alphabet_group(grid: Grid, horizontal_start: int, vertical_start: int,
                        field_length) -> GridGroup:
    return [
        AlphabetGridRange(grid, horizontal_start + i, vertical_start)
        for i in range(field_length)
    ]