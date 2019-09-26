"""List processing and handling utilities."""

import math


def find_greatest_value_indexes(values, n):
    """Find the indices of the greatest `n` numbers in `items`.

    Returns:
        A list where the first element is the index of the greatest item and the
        second element is the index of the second-greatest item and so on.
    """
    items_copy = values.copy()
    indexes = []
    for i in range(n):
        max_index = find_max_value_index(items_copy)
        indexes.append(max_index)
        items_copy[max_index] = -math.inf
    return indexes


def find_max_value_index(values):
    """Returns the index of the greatest value in `items`."""
    max_value = -math.inf
    max_index = -1
    for i, value in enumerate(values):
        if value > max_value:
            max_value = value
            max_index = i
    return max_index


def is_adjacent_indexes(items, index_a, index_b):
    """Check that the given indices are next to each other or are the first and
  last indices in the list. Order of a and b do not matter."""
    return next_index(items, index_a) == index_b or prev_index(
        items, index_a) == index_b


def unnest(nested):
    """Flatten a list in the form `[[[a,b]], [[c,d]], [[e,f]]]` to `[[a,b], [c,d], [e,f]]`."""
    return [e[0] for e in nested]


def call_on_some(items, indexes, fn):
    """Return a copy of the list with the results of `fn` called on the items in
    `items` with the indexes in `indexes`. Other items remain the same."""
    return [el if i not in indexes else fn(el) for i, el in enumerate(items)]


def next_index(items, index):
    """Return the next index up in the list, looping back to the beginning if needed."""
    return index + 1 if index + 1 < len(items) else 0


def prev_index(items, index):
    """Return the previous index up in the list, looping back to the end if needed."""
    return index - 1 if index - 1 >= 0 else len(items) - 1


def continue_index(items, index_a, index_b):
    """Get the next index in the direction a nd b are going (if b >= a, then returns
    the next index, otherwise, returns the previous). """
    if index_b >= index_a:
        return next_index(items, index_b)
    return prev_index(items, index_b)


def arrange_like_rays(pair_a, pair_b):
    """Given two pairs of numbers, arrange them such that the common value in
    the pairs is the second item in the first pair and the first item in the
    second, like rays that share a vertex. If the pairs have no numbers in common,
    nothing will happen. """
    shared = next((a for a, b in zip(pair_a, pair_b) if a == b), None)
    if shared is not None:
        pair_a_ = pair_a if pair_a[1] == shared else list(reversed(pair_a))
        pair_b_ = pair_b if pair_b[0] == shared else list(reversed(pair_b))
        return pair_a_, pair_b_
    else:
        return pair_a, pair_b
