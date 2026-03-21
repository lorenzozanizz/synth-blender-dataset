from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .operations import PipelineOperation

class OperationRegistry:
    """Registry of all available operations."""

    _operations = {}

    @classmethod
    def register(cls, op_type: str):
        def decorator(drawer_cls):
            cls._operations[op_type] = drawer_cls
            return drawer_cls
        return decorator

    @classmethod
    def get(cls, operation_type: str) -> 'PipelineOperation':
        """Get an operation instance by type."""
        if operation_type not in cls._operations:
            raise ValueError(f"Unknown operation type: {operation_type}")
        return cls._operations[operation_type]()

    @classmethod
    def get_all_types(cls) -> list:
        """Get all available operation types."""
        return list(cls._operations.keys())
