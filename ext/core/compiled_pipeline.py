from ..pipeline.bpy_properties import PipelineData, PipelineOperation
from ..pipeline.operation_registry import OperationRegistry
from ..pipeline.context import NestedPipelineContext

import json


class ExecutablePipeline:

    def __init__(self, ctx, pipeline_data: PipelineData, reporter = None ):
        """

        :param pipeline_data:
        :param reporter:
        """
        self.ctx = ctx
        self.reporter = reporter
        self.data = pipeline_data
        self.pipes_executable: list[PipelineOperation] = []
        self.compile_pipeline()

    def compile_pipeline(self):
        """Deserialize all operations once"""
        compiled = []

        for operation in self.data.operations:

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

        self.pipes_executable = compiled
        return compiled

    def get_executors(self) -> list[PipelineOperation]:
        """Return all pipeline operations"""
        return self.pipes_executable

    def build_context_manager(self) -> NestedPipelineContext:
        return NestedPipelineContext(self.get_executors())

    def execute(self):

        for pipe in self.pipes_executable:
            pipe.execute(self.ctx)