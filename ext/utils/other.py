""" Other utility functions which are more general, like for iteration and python constructs.

Functions:
    reverse_chained: Chains together a set of iterables and computing the overall reversed.

"""
from typing import Reversible, Any, Iterable


def reverse_chained(iterables: Reversible[Reversible[Any]]) -> Iterable[Any]:
    """ Reverse the chain without materializing all items """
    for iterable in reversed(iterables):
        # From py-lint advice lol0
        yield from reversed(list(iterable))