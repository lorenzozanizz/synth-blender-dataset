"""



"""

from .operation_registry import OperationRegistry
from ..constants import PipeNames

from abc import ABC, abstractmethod


class PipelineOperation(ABC):
    """Base class for all pipeline operations."""

    operation_type: str  # "randomize_position", "randomize_rotation", etc.

    @abstractmethod
    def compile(self, config: dict):
        pass

    @abstractmethod
    def execute(self, context):
        """Execute this operation on the scene."""
        pass


@OperationRegistry.register(PipeNames.SCALE.value)
class RandomizeScaleOperation(PipelineOperation):

    def compile(self, config: dict):
        pass

    def execute(self, context):
        # Your logic
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
