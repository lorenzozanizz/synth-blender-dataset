from .operations import PipelineOperation
from ..constants import PipeNames, WidgetSerializationKeys

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Union

import bpy

class PipeValidator(metaclass=ABCMeta):
    """

    """
    @staticmethod
    @abstractmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
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
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.POSITION.value)
class PositionValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.MOVE.value)
class MoveValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.ROTATION.value)
class RotationValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.VISIBILITY.value)
class VisibilityValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.MATERIAL.value)
class MaterialValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        obj_ok = ObjectTargeterValidator.validate(config[WidgetSerializationKeys.OBJECT.value])
        mat_ok = MaterialSelectorValidator.validate(config[WidgetSerializationKeys.MATERIAL.value])
        return mat_ok and obj_ok

@ValidatorRegistry.register(PipeNames.TEXTURE.value)
class TextureValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        return False


@ValidatorRegistry.register(PipeNames.INTENSITY.value)
class IntensityValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.METALLIC.value)
class MetallicValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        return False


@ValidatorRegistry.register(PipeNames.ROUGHNESS.value)
class RoughnessValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        return False

class WidgetValidator(metaclass=ABCMeta):
    """

    """
    @staticmethod
    @abstractmethod
    def validate(partial_config: dict) -> bool:
        pass


class AxisTargetValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        """

        :param partial_config:
        :return:
        """
        do_x = partial_config
        do_y = partial_config
        do_z = partial_config
        return do_x or do_y or do_z


#
class ObjectTargeterValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        # We simply ensure that all the objects do exist in the bpy data.
        objects = partial_config[WidgetSerializationKeys.OBJECT_NAMES.value]
        # The pipe is noto OK if it has no target. "OK" means useful and working.
        if not objects:
            return False
        for name in objects:
            name: str
            # Note that this searches for objects in all the different scenes of the active
            # file, not just the current context.
            try:
                obj = bpy.data.objects[name]
            except KeyError:
                return False
            if not obj:
                return False
        return True


#
class ImageTextureTargeterValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class PathListSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class NodeDistributionSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class SimplifiedDistributionSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class PositionListSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


#
class MaterialSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        """

        :param partial_config:
        :return:
        """

        # We simply ensure that all the materials listed do exist in the bpy data.
        materials = partial_config[WidgetSerializationKeys.MATERIAL_LIST.value]
        if not materials:
            return False
        for mat in materials:
            mat: str
            try:
                tree = bpy.data.materials.get(mat)
            except KeyError:
                return False
            if not tree:
                return False
        return True



#
class PropertyTargeterValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass


class ValueTargeterValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        pass
