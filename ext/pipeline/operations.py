"""



"""

from .operation_registry import OperationRegistry
from .context import *

from ..constants import PipeNames, WidgetSerializationKeys
from ..utils.logger import UniqueLogger

from abc import ABCMeta, abstractmethod


class PipelineOperation(DoubleFramedPipe, metaclass=ABCMeta):
    """Base class for all pipeline operations."""

    operation_type: str  # "randomize_position", "randomize_rotation", etc.

    @abstractmethod
    def compile(self, config: dict):
        pass

    @abstractmethod
    def execute(self, context):
        """Execute this operation on the scene."""
        pass


class NumericRandomOperation:

    def __init__(self, operation: PipelineOperation):
        pass

@OperationRegistry.register(PipeNames.SCALE.value)
class RandomizeScaleOperation(PipelineOperation):

    def get_global_context(self):
        pass

    def get_frame_context(self):
        pass

    def compile(self, config: dict):
        pass

    def execute(self, context):
        # Your logic
        pass

    class ScaleContext(ContextManager):

        def __enter__(self):
            pass
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass


@OperationRegistry.register(PipeNames.POSITION.value)
class RandomizePositionOperation(PipelineOperation):

    def compile(self, config: dict):
        pass

    def execute(self, context):
        # Your logic
        pass


@OperationRegistry.register(PipeNames.MOVE.value)
class RandomizeMoveOperation(PipelineOperation):

    def compile(self,  config: dict):
        pass

    def execute(self, context):
        # Your logic
        pass


@OperationRegistry.register(PipeNames.ROTATION.value)
class RandomizeRotationOperation(PipelineOperation):

    def compile(self,  config: dict):
        pass

    def execute(self, context):
        # Your logic
        pass


@OperationRegistry.register(PipeNames.VISIBILITY.value)
class RandomizeVisibilityOperation(PipelineOperation):

    def compile(self,  config: dict):
        pass

    def execute(self, context):
        # Your logic
        pass
