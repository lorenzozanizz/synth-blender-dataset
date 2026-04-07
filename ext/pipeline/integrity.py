from .operations import PipelineOperation
from ..constants import PipeNames

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Union

class PipeValidator(metaclass=ABCMeta):
    """

    """
    @staticmethod
    @abstractmethod
    def validate(pipe: PipelineOperation) -> bool:
        pass


class ValidatorRegistry:
    """Registry of all available operations."""

    _operations = {}

    @classmethod
    def register(cls, op_type: str):
        def decorator(drawer_cls):
            cls._operations[op_type] = drawer_cls
            return drawer_cls
        return decorator

    @classmethod
    def get(cls, operation_type: str) -> Union[PipeValidator, None]:
        """Get an operation instance by type."""
        if operation_type not in cls._operations:
            return None
        return cls._operations[operation_type]()

    @classmethod
    def get_all_types(cls) -> list:
        """Get all available operation types."""
        return list(cls._operations.keys())

@ValidatorRegistry.register(PipeNames.SCALE.value)
class ScaleValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.POSITION.value)
class PositionValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.MOVE.value)
class MoveValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.ROTATION.value)
class RotationValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.VISIBILITY.value)
class VisibilityValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.MATERIAL.value)
class MaterialValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.TEXTURE.value)
class TextureValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False


@ValidatorRegistry.register(PipeNames.INTENSITY.value)
class IntensityValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.METALLIC.value)
class MetallicValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False


@ValidatorRegistry.register(PipeNames.ROUGHNESS.value)
class RoughnessValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation) -> bool:
        return False

class WidgetValidator(metaclass=ABCMeta):
    """

    """
    @staticmethod
    @abstractmethod
    def validate(partial_config: dict) -> bool:
        pass


class AxisTarget(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class ObjectTargeter(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class ImageTextureTargeter(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class PathListSelector(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class NodeDistributionSelector(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class SimplifiedDistributionSelector(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class PositionListSelector(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class MaterialSelector(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class PropertyTargeter(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


class ValueTargeter(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


class WidgetSerializationLabels(Enum):

    class NodeDistribution(Enum):

        TYPE = "Type"
        OFFSET = "Offset"
