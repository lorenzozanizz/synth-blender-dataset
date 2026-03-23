"""



"""

from .registry import OperationRegistry
from ..constants import PipeNames

from abc import ABC, abstractmethod



class PipelineOperation(ABC):
    """Base class for all pipeline operations."""

    operation_type: str  # "randomize_position", "randomize_rotation", etc.

    @abstractmethod
    def from_config(self) -> dict:
        pass

    @abstractmethod
    def execute(self, scene, objects):
        """Execute this operation on objects."""
        pass


@OperationRegistry.register(PipeNames.SCALE.value)
class RandomizeScaleOperation(PipelineOperation):

    def from_config(self) -> dict:
        pass

    def execute(self, scene, objects):
        # Your logic
        pass

