def reverse_chained(iterables):
    """Reverse the chain without materializing all items """
    for iterable in reversed(iterables):
        # From py-lint advice lol
        yield from reversed(list(iterable))