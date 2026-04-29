"""


"""
from collections import defaultdict

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .io_strategy import IOStrategy


class LabelingFormatRegistry:
    """Registry of all available operations."""

    # We use dictionaries in case the labeling gets more complicated and multiple
    # entities are required.
    _formats = defaultdict(dict)

    @classmethod
    def register_strategy(cls, format_lbl: str):
        def decorator(format_cls):
            cls._formats[format_lbl]['strategy'] = format_cls
            return format_cls
        return decorator

    @staticmethod
    def register_new(
        format_name: str,
        strategy,
    ) -> None:
        """

        :param format_name:
        :param strategy:
        :return:
        """

        if not format_name or strategy is None:
            raise RuntimeError(f"Cannot register new format {format_name} with {strategy}")
        # remember that _formats is a defaultdict, so we can write this without problems.
        if not issubclass(strategy, IOStrategy):
            raise RuntimeError(f"The format {format_name} requires an instance"
               f" of a {IOStrategy.__name__} class")

        LabelingFormatRegistry._formats[format_name]['strategy'] = strategy

    @classmethod
    def get_strategy(cls, lbl_type: str) -> type['IOStrategy']:
        return cls._formats.get(lbl_type).get('strategy')