from .operations import PipelineOperation
from ..constants import PipeNames

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
        pass


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
            obj = bpy.data.objects[name]
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
            tree = bpy.data.materials.get(mat)
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


class WidgetSerializationKeys(Enum):


    DIMENSION = "dimension"

    MATERIAL = "materials"
    MATERIAL_LIST               = "materials"

    # Incomplete, a bit messy for now!
    PROPERTY = ""

    VALUE   = "value"
    VALUE_MATERIAL              = "material"
    VALUE_LABEL                 = "label"

    POSITION = "positions"
    POSITION_LIST               = "positions"

    SIMPLE  = "distribution"
    SIMPLE_PRESET_NAME          = "preset"
    SIMPLE_OFFSET_MODE          = "do_offset"
    SIMPLE_DISCRETIZE           = "do_discretize"
    SIMPLE_CLAMP                = "do_clamp"
    SIMPLE_CLAMPING_EXTREMES    = "clamping_factors"
    SIMPLE_PARAMETERS           = "parameters"

    NODE    = "distribution"
    NODE_USE_TREE               = "use_tree"
    NODE_DISTRIBUTION           = "distribution"

    PATH    = "textures"
    PATH_USE_FOLDER             = "use_folder"
    PATH_FILES                  = "files"
    PATH_FOLDER                 = "folder"

    TEXTURE = "node"
    TEXTURE_MATERIAL            = "material"
    TEXTURE_LABEL               = "label"

    OBJECT  = "target"
    OBJECT_NAMES                = "names"

    AXIS    = "axis"
    AXIS_DIMS                   = "dims"
    AXIS_RANDOMIZE_PREFIX_X     = "target_x"
    AXIS_RANDOMIZE_PREFIX_Y     = "target_Y"
    AXIS_RANDOMIZE_PREFIX_Z     = "target_Z"