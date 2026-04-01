"""

"""
from .pipe_edit_widgets import *

from ..constants import PipeNames

from abc import ABC, abstractmethod
from typing import Union


class PipeSchemaRegistry:
    """Registry of all available operations."""

    _pipes_schema = {}

    @classmethod
    def register(cls, op_type: str):
        if op_type in cls._pipes_schema:
            raise RuntimeError(f"Duplicate operation type {op_type}")
        def decorator(drawer_cls):
            cls._pipes_schema[op_type] = drawer_cls
            return drawer_cls
        return decorator

    @classmethod
    def get(cls, operation_type: str) -> Union['PipeSchema', None]:
        """Get a schema instance by type."""
        if operation_type not in cls._pipes_schema:
            return None
        return cls._pipes_schema[operation_type]()

    @classmethod
    def get_all_types(cls) -> list:
        """Get all available schemas types."""
        return list(cls._pipes_schema.keys())


class ConfigExtractionUtils:
    """

    """
    pass


class PipeSchema(ABC):
    """

    """

    @staticmethod
    @abstractmethod
    def extract_config_from_ui(context, operation) -> dict:
        """

        :param context:
        :param operation:
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def apply_config_to_ui(context, operation, config) -> None:
        """

        :param context:
        :param operation:
        :param config:
        :return:
        """
        pass


@PipeSchemaRegistry.register(PipeNames.VISIBILITY.value)
class VisibilitySchema(PipeSchema):

    @staticmethod
    def extract_config_from_ui(context, operation) -> dict:
        ret = dict()
        for widget in (ObjectTargeter, SimplifiedDistributionSelector):
            ret.update(widget.extract_data(context))
        return ret

    @staticmethod
    def apply_config_to_ui(context, operation, config) -> None:
        if not config:
            for widget in (ObjectTargeter, SimplifiedDistributionSelector):
                widget.reset(context)
            return
        for widget in (ObjectTargeter, SimplifiedDistributionSelector):
            widget.setup_from_config(config, context)
