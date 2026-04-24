import json

from ..pipeline.bpy_properties import PipelineData, PipelineOperation
from ..pipeline.operation_registry import OperationRegistry
from ..pipeline.context import NestedPipelineContext

from ..utils.timer import TimingContext


class ExecutablePipeline:
    """ Represents a compiled and executable pipeline built from a sequence of
    pipeline operations.

    This class is responsible for validating, compiling, and executing
    operations defined in the Blender property PipelineData object. It also tracks compilation
    timing and provides access to the resulting executable operations and
    their combined context through the NestedPipelineContext.
    """

    def __init__(self, ctx, pipeline_data: PipelineData, reporter = None ):
        """ Initializes a new ExecutablePipeline from the blender property
        PipelineData object.

        :param pipeline_data: the blender property PipelineData object
        :param reporter: an object which can report information to the blender GUI.
        """
        self.ctx = ctx
        self.reporter = reporter
        self.data = pipeline_data
        self.pipes_executable: list[PipelineOperation] = []

        self.compilation_time = dict()
        with TimingContext(self.compilation_time, 'compilation'):
            self.compile_pipeline()

    def compile_pipeline(self) -> list[PipelineOperation]:
        """
        Compile the pipeline operations into executable instances.

        Iterates over all operations defined in the pipeline data, skipping
        those that are disabled or invalid. Each operation's configuration
        is deserialized from JSON, and the corresponding executor is retrieved
        from the OperationRegistry and compiled.

        Errors during configuration parsing or executor lookup are optionally
        reported via the reporter.

        :return: A list of compiled PipelineOperation executors
        """
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
                executor.compile(self.ctx, config)
            except ValueError:
                if self.reporter:
                    self.reporter.report({'ERROR'}, f"No executor found for operation {operation.name}")
                continue

            compiled.append(executor)

        self.pipes_executable = compiled
        return compiled

    def get_executors(self) -> list[PipelineOperation]:
        """ Return all pipeline operations """
        return self.pipes_executable

    def build_context_manager(self) -> NestedPipelineContext:
        """ Get the context manager for the entire pipeline, which is a composite context
        encompassing all frame and full contexts of all operations in the pipeline. Note
        that certain operations may not provide a frame context, which might not be needed if
        for example the positions is overridden at every frame.

        :return: A NestedPipelineContext object with both a full and frame context
        """
        return NestedPipelineContext(self.get_executors())

    def execute(self) -> None:
        """ Execute all compiled pipeline operations in sequence.

        Each operation in self.pipes_executable is invoked with the shared
        pipeline context. Operations are executed in the order they were compiled.
        The operations which could not be validated are NOT executed.
        """
        for pipe in self.pipes_executable:
            pipe.execute(self.ctx)

    def get_compilation_time(self) -> float:
        """ Get the time it took to compile all the pipes in the pipeline """
        return self.compilation_time['compilation']