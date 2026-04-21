def reverse_chained(iterables):
    """Reverse the chain without materializing all items """
    for iterable in reversed(iterables):
        for item in reversed(list(iterable)):
            yield item