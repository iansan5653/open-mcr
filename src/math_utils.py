"""General mathematics utilities."""

import enum
import typing as tp

import list_utils


class InequalityTypes(enum.Enum):
    """Represents all the possible inequality types.

    Members:
        GTE: Greater than or equal to (`>=`).
        LTE: Less than or equal to (`<=`).
        GT: Greater than (`>`).
        LT: Less than (`<`).
        NE: Not equal (`!=`).
    """
    GTE = enum.auto()
    LTE = enum.auto()
    GT = enum.auto()
    LT = enum.auto()
    NE = enum.auto()


def is_approx_equal(value_a: float, value_b: float,
                    tolerance: float = 0.1) -> bool:
    """Returns true if the difference of `a` and `b` is within tolerance * value_b."""
    return abs(value_a - value_b) <= (tolerance * value_b)


def is_within_tolerance(value_a: float, target: float,
                        tolerance: float) -> bool:
    """Returns true if a falls within target +- tolerance."""
    return value_a < target + tolerance and value_a > target - tolerance


def all_approx_equal(values: tp.List[float],
                     target: tp.Union[float, None] = None,
                     tolerance: float = 0.15) -> bool:
    """Returns `True` if every element in `values` is within `tolerance` of `target`.

    Args:
        values: List of numeric values to check for equality.
        target: Target value. If not provided, uses the mean to check if all list
        are approximately equal to themselves.
        tolerance: The tolerance for equality. 0.1 is 10% of the smaller value.
    """
    target_ = target if target is not None else mean(values)
    return all(
        [is_approx_equal(value, target_, tolerance) for value in values])


def mean(values: tp.Union[tp.List[int], tp.List[float], tp.List[bool]]
         ) -> float:
    """Returns the average of the list of numeric values."""
    return sum(values) / len(values)


def divide_some(values: tp.List[float], indexes: tp.List[int],
                divisor: float) -> tp.List[float]:
    """Returns a copy of `values` where items at `indices` are divided by `divisor`."""
    return list_utils.call_on_some(values, indexes, lambda x: x / divisor)
