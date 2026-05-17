""" Other utility functions which are more general, like for iteration and python constructs.

Functions:
    reverse_chained: Chains together a set of iterables and computing the overall reversed.

"""
from typing import Reversible, Any, Iterable


class MultiContext:
    def __init__(self, *contexts):
        self.contexts = contexts

    def __enter__(self):
        for ctx in self.contexts:
            ctx.__enter__()
        return self

    def __exit__(self, *args):
        for ctx in reversed(self.contexts):
            ctx.__exit__(*args)


def reverse_chained(iterables: Reversible[Reversible[Any]]) -> Iterable[Any]:
    """ Reverse the chain without materializing all items """
    for iterable in reversed(iterables):
        # From py-lint advice lol0
        yield from reversed(list(iterable))