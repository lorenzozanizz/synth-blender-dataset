"""



"""

from .operation_registry import OperationRegistry
from .context import *

from ..constants import PipeNames, WidgetSerializationKeys
from ..utils.logger import UniqueLogger
from ..distribution.computation import SamplerCompiler

from typing import Any, List, Tuple
from abc import ABCMeta, abstractmethod

import bpy

wsk = WidgetSerializationKeys

class PipelineOperation(DoubleFramedPipe, metaclass=ABCMeta):
    """Base class for all pipeline operations."""

    operation_type: str  # "randomize_position", "randomize_rotation", etc.

    @abstractmethod
    def compile(self, config: dict):
        """

        :param config:
        :return:
        """
        pass

    @abstractmethod
    def execute(self, context):
        """

        :param context:
        :return:
        """
        pass

class AxisSetMask:

    def __init__(self, config: dict[str, Any]):
        self.dimensions = config[wsk.DIMENSION.value]
        self.x = config[wsk.AXIS_RANDOMIZE_PREFIX_X.value]
        self.y = config[wsk.AXIS_RANDOMIZE_PREFIX_Y.value]
        self.z = config[wsk.AXIS_RANDOMIZE_PREFIX_Z.value]

    def dimensions(self):
        return self.dimensions

    def assign(self, vector_attribute: Any, value: Any):
        """

        :param vector_attribute:
        :param value:
        :return:
        """
        axes = [ax for ax in ['x', 'y', 'z'] if getattr(self, ax)]
        for axis, val in zip(axes, value):
            setattr(vector_attribute, axis, val)

    def increment(self, vector_attribute: Any, value: Any):
        """

        :param vector_attribute:
        :param value:
        :return:
        """
        UniqueLogger.quick_log("Value is: " + value.__str__())
        idx = 0
        if self.x:
            vector_attribute.x += value[idx]
            idx += 1
        if self.y:
            vector_attribute.y += value[idx]
            idx += 1
        if self.z:
            vector_attribute.z += value[idx]
        return


class NumericRandomOperation(PipelineOperation, metaclass=ABCMeta):
    """

    """

    def __init__(self):

        self.offset_mode    = None
        self.dimension      = None
        self.distribution   = None
        self.axis           = None
        self.targets        = None

    def compile(self, config: dict):
        """

        :param config:
        :return:
        """

        # Simply extract the value from the config
        self.dimension = int(config[wsk.DIMENSION.value])
        # The distribution will be compiled (either a node or a preset distribution)
        self.distribution = SamplerCompiler.compile(config[wsk.NODE_DISTRIBUTION.value], self.dimension)

        # Extract the axis and the targets. the axis object is a simple interface for
        # assigning on different dimensions
        self.axis = AxisSetMask(config[wsk.AXIS.value])
        self.targets = config[wsk.OBJECT.value][wsk.OBJECT_NAMES.value]

        # This is a boolean value
        self.offset_mode = config[wsk.OFFSET.value][wsk.OFFSET_MODE.value]

    @abstractmethod
    def get_context(self):
        """

        :return:
        """
        pass

    def get_global_context(self):
        return self.get_context()

    def get_frame_context(self):
        """

        :return:
        """
        if self.offset_mode:
            return self.get_context()
        else:
            return None

@OperationRegistry.register(PipeNames.SCALE.value)
class RandomizeScaleOperation(NumericRandomOperation):

    def execute(self, context):
        result = self.distribution.sample()
        for item in self.targets:
            obj = bpy.data.objects[item]
            if self.offset_mode:
                self.axis.increment(obj.scale, result)
            else:
                self.axis.assign(obj.scale, result)

    class ScaleContext(ContextManager):

        def __init__(self, items):
            self.items = items
            self.scales = []

        def __enter__(self):
            # Clear to avoid polluting and damaging the values
            self.scales.clear()
            for item in self.items:
                self.scales.append(tuple(bpy.data.objects[item].scale))

        def __exit__(self, exc_type, exc_val, exc_tb):
            for item, scale in zip(self.items, self.scales):
                bpy.data.objects[item].scale = scale

    def get_context(self):
        return RandomizeScaleOperation.ScaleContext(self.targets)


@OperationRegistry.register(PipeNames.POSITION.value)
class RandomizePositionOperation(NumericRandomOperation):

    def execute(self, context):
        result = self.distribution.sample()
        for item in self.targets:
            obj = bpy.data.objects[item]
            if self.offset_mode:
                self.axis.increment(obj.location, result)
            else:
                self.axis.assign(obj.location, result)

    class PositionContext(ContextManager):

        def __init__(self, items):
            self.items = items
            self.location = []

        def __enter__(self):
            # Clear to avoid polluting and damaging the values
            self.location.clear()
            for item in self.items:
                self.location.append(tuple(bpy.data.objects[item].location))

        def __exit__(self, exc_type, exc_val, exc_tb):
            for item, location in zip(self.items, self.location):
                bpy.data.objects[item].location = location

    def get_context(self):
        return RandomizePositionOperation.PositionContext(self.targets)


@OperationRegistry.register(PipeNames.MOVE.value)
class RandomizeMoveOperation(PipelineOperation):

    def __init__(self):

        self.distribution   = None
        self.targets        = None

    def get_frame_context(self):
        return RandomizePositionOperation.PositionContext(self.targets)

    def get_global_context(self):
        return RandomizePositionOperation.PositionContext(self.targets)

    def compile(self,  config: dict):
        pass

    def execute(self, context):
        pass


@OperationRegistry.register(PipeNames.ROTATION.value)
class RandomizeRotationOperation(PipelineOperation):

    def compile(self,  config: dict):
        pass

    def execute(self, context):
        pass


@OperationRegistry.register(PipeNames.VISIBILITY.value)
class RandomizeVisibilityOperation(PipelineOperation):

    def get_global_context(self):
        return RandomizeVisibilityOperation.VisibilityContext(self.targets)

    def get_frame_context(self):
        return RandomizeVisibilityOperation.VisibilityContext(self.targets)

    def compile(self, config: dict):
        self.targets = config[wsk.OBJECT.value][wsk.OBJECT_NAMES.value]
        # The distribution will be compiled ( a bernoulli )
        self.distribution = SamplerCompiler.compile(config[wsk.NODE_DISTRIBUTION.value], dim=1)

    def __init__(self):

        self.distribution   = None
        self.targets        = None

    def execute(self, context):
        # One dimensional result, a bernoulli

        result = self.distribution.sample()[0]
        for item in self.targets:
            obj = bpy.data.objects[item]
            if result > 0.5:
                self.hide(obj)

    @staticmethod
    def hide(obj) -> None:
        obj.hide_render = True
        obj.visible_camera = False
        obj.visible_diffuse = False
        obj.visible_glossy = False
        obj.visible_shadow = False
        obj.visible_transmission = False
        obj.visible_volume_scatter = False
        obj.hide_set(True)

    class VisibilityContext(ContextManager):

        def __init__(self, items):
            self.items = items
            # We actually need to change multiple attributes per object: not only are we
            # interested in the general render visibility, but also to the transparency to
            # rays and other computations that are required for labeling in general.
            self.visibilities: List[tuple] = []

        def __enter__(self):
            # Clear to avoid polluting and damaging the values
            self.visibilities.clear()
            for item in self.items:
                obj = bpy.data.objects[item]
                self.visibilities.append(self.extract(obj))

        def __exit__(self, exc_type, exc_val, exc_tb):
            for item, state in zip(self.items, self.visibilities):
                obj = bpy.data.objects[item]
                self.restore(obj, state)

        @staticmethod
        def restore(obj, state) -> None:
            obj.hide_render = state[0]
            obj.visible_camera = state[1]
            obj.visible_diffuse = state[2]
            obj.visible_glossy = state[3]
            obj.visible_shadow = state[4]
            obj.visible_transmission = state[5]
            obj.visible_volume_scatter = state[6]
            obj.hide_set( state[7] )

        @staticmethod
        def extract(obj) -> Tuple:
            return (
                obj.hide_render, obj.visible_camera, obj.visible_diffuse, obj.visible_glossy,
                obj.visible_shadow, obj.visible_transmission, obj.visible_volume_scatter, obj.hide_get()
            )