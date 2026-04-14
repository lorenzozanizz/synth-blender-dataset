from .operations import PipelineOperation
from ..constants import PipeNames, WidgetSerializationKeys, DISTRO_EDITOR_NAME

from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Union

import bpy

wsk = WidgetSerializationKeys

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

class NumericPropertyValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        axi_ok = AxisTargetValidator.validate(config[wsk.AXIS.value])
        obj_ok = ObjectTargeterValidator.validate(config[wsk.OBJECT.value])
        dis_ok = NodeDistributionSelectorValidator.validate(config[wsk.NODE.value])
        return axi_ok and obj_ok and dis_ok

@ValidatorRegistry.register(PipeNames.SCALE.value)
class ScaleValidator(NumericPropertyValidator):
    pass

@ValidatorRegistry.register(PipeNames.POSITION.value)
class PositionValidator(NumericPropertyValidator):
    pass

@ValidatorRegistry.register(PipeNames.ROTATION.value)
class RotationValidator(NumericPropertyValidator):
    pass

@ValidatorRegistry.register(PipeNames.MOVE.value)
class MoveValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        return False

@ValidatorRegistry.register(PipeNames.VISIBILITY.value)
class VisibilityValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation,  config: dict) -> bool:
        obj_ok = ObjectTargeterValidator.validate(config[wsk.OBJECT.value])
        dis_ok = SimplifiedDistributionSelectorValidator.validate(config[wsk.SIMPLE.value])
        return obj_ok and dis_ok


@ValidatorRegistry.register(PipeNames.MATERIAL.value)
class MaterialValidator(PipeValidator):

    @staticmethod
    def validate(pipe: PipelineOperation, config: dict) -> bool:
        obj_ok = ObjectTargeterValidator.validate(config[wsk.OBJECT.value])
        mat_ok = MaterialSelectorValidator.validate(config[wsk.MATERIAL.value])
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
        do_x = partial_config[wsk.AXIS_RANDOMIZE_PREFIX_X.value]
        do_y = partial_config[wsk.AXIS_RANDOMIZE_PREFIX_Y.value]
        do_z = partial_config[wsk.AXIS_RANDOMIZE_PREFIX_Z.value]
        return do_x or do_y or do_z


#
class ObjectTargeterValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:
        # We simply ensure that all the objects do exist in the bpy data.
        objects = partial_config[wsk.OBJECT_NAMES.value]
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

        use_tree = partial_config['use_tree']
        if use_tree:
            name = partial_config['distribution]']
            tree = next(
                (ng for ng in bpy.data.node_groups
                 if ng.bl_idname == DISTRO_EDITOR_NAME and ng.name == name),
                None
            )
            if tree is None:
                return False
        else:
            preset = partial_config['preset']
            if preset.lower() == "None":
                return False
        return True

#
class SimplifiedDistributionSelectorValidator(WidgetValidator):

    @staticmethod
    def validate(partial_config: dict) -> bool:

        return True


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
        materials = partial_config[wsk.MATERIAL_LIST.value]
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
