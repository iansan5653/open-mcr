"""Functions for establishing and reading the grid."""

import geometry_utils
import math
import typing


class Grid:
    corners: geometry_utils.Polygon
    horizontal_cells: int
    vertical_cells: int
    _to_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                    Point]
    _from_grid_basis: typing.Callable[[geometry_utils.Point], geometry_utils.
                                      Point]

    def __init__(self, corners, horizontal_cells: int, vertical_cells: int):
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

    def __init__(self, horizontal_start: int, vertical_start: int,
                 is_vertical: bool, num_cells: int):
        self.vertical_start: int
        self.horizontal_start: int
        self.is_vertical: bool
        self.num_cells: int

    def read_value(self):
        pass


class AlphabetGridRange(GridRange):
    def __init__(self, horizontal_start: int, vertical_start: int):
        super(horizontal_start, vertical_start, True, 26)


class NumericGridRange(GridRange):
    def __init__(self, horizontal_start: int, vertical_start: int):
        super(horizontal_start, vertical_start, True, 10)


class AnswerGridRange(GridRange):
    def __init__(self, horizontal_start: int, vertical_start: int):
        super(horizontal_start, vertical_start, False, 5)


class FormCodeGridRange(GridRange):
    def __init__(self, horizontal_start: int, vertical_start: int):
        super(horizontal_start, vertical_start, False, 6)


GridGroup = typing.List[GridRange]


def make_alphabet_group(grid: Grid, horizontal_start: int, vertical_start: int,
                        char_length: int, field_length) -> GridGroup:
    return [
        AlphabetGridRange(horizontal_start + i * grid.horizontal_cell_size,
                          vertical_start, False, char_length)
        for i in field_length
    ]
