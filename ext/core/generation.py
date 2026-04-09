from .labeling import LabelingFormats

from ..pipeline.operation_registry import OperationRegistry
from ..ui.pipe_schema import PipeSchemaRegistry

import json
import random
import os
from dataclasses import dataclass

import bpy

@dataclass
class ExecutionParameters:
    """

    """
    seed: int
    amount: int
    prefix: str
    format: str

    from_last: bool

    save_path: str

class PipelineExecutor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, context, parameters, reporter = None):
        self.ctx = context
        self.parameters = parameters
        self.compiled_ops = []
        self.reporter = reporter

    def compile_pipeline(self) -> list:
        """Deserialize all operations once"""
        scene = self.ctx.scene
        pipeline = scene.pipeline_data
        compiled = []

        for operation in pipeline.operations:
            if not operation.enabled:
                continue
            # Momentarily, invalid operations are skipped. It may be that in the future this
            # is not the case...
            elif not operation.valid:
                continue
            op_type = operation.operation_type
            # Deserialize config
            try:
                config = json.loads(operation.config)
            except json.JSONDecodeError as e:
                if self.reporter:
                    self.reporter.report({'ERROR'}, f"Invaid configuration for pipe {operation.name}")
                continue

            # Get executor class
            try:
                executor = OperationRegistry.get(op_type)
                executor.compile(config)
            except ValueError:
                if self.reporter:
                    self.reporter.report({'ERROR'}, f"No executor found for operation {operation.name}")
                continue

            compiled.append(executor)

        self.compiled_ops = compiled
        return compiled

    def execute(self):
        """Execute all compiled operations"""

        scene = self.ctx.scene
        for op_data in self.compiled_ops:
            executor = op_data['executor']

            try:
                executor.execute(scene)
            except Exception as e:
                print(f"Error executing {op_data['name']}: {e}")
                raise
