from .labeling import LabelingFormats

from ..pipeline.operation_registry import OperationRegistry
from ..ui.pipe_schema import PipeSchemaRegistry

import json
import random
import os
from dataclasses import dataclass

from bpy.types import Operator
import bpy

@dataclass
class ExecutionParameters:
    seed: int
    amount: int
    prefix: str
    format: str

    from_last: bool


class PipelineExecutor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, scene):
        self.scene = scene
        self.compiled_ops = []

    def compile_pipeline(self, scene) -> list:
        """Deserialize all operations once"""
        pipeline = scene.pipeline_data
        compiled = []

        for operation in pipeline.operations:
            if not operation.enabled:
                continue

            op_type = operation.operation_type

            # Get schema to validate config
            schema = PipeSchemaRegistry.get(op_type)
            if not schema:
                continue

            # Deserialize config
            try:
                config = json.loads(operation.config)
            except json.JSONDecodeError as e:
                print(f"Failed to parse config for {op_type}: {e}")
                continue

            # Get executor class
            try:
                executor_cls = OperationRegistry.get(op_type)
            except ValueError:
                print(f"No executor for {op_type}")
                continue

            compiled.append({
                'name': operation.name,
                'type': op_type,
                'config': config,
                'executor': executor_cls
            })

        self.compiled_ops = compiled
        return compiled

    def execute(self, scene, objects):
        """Execute all compiled operations"""
        for op_data in self.compiled_ops:
            executor = op_data['executor']
            config = op_data['config']

            try:
                executor.execute(scene, objects, config)
            except Exception as e:
                print(f"Error executing {op_data['name']}: {e}")
                # Continue on error or fail? Your choice
                raise

