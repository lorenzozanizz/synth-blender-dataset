from .labeling import LabelingFormats
from ..pipeline.bpy_properties import PipelineData, PipelineOperation
from ..pipeline.operation_registry import OperationRegistry
from ..pipeline.context import NestedPipelineContext
from ..ui.pipe_schema import PipeSchemaRegistry

import json
import random
import re
import os
from dataclasses import dataclass
from pathlib import Path
from os import listdir
from os.path import isdir, isfile, join

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

class ExecutablePipeline:

    def __init__(self, pipeline_data: PipelineData, reporter = None ):
        """

        :param pipeline_data:
        :param reporter:
        """
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
            pipe.execute()

class Executor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, context, data: PipelineData, parameters, reporter = None):
        self.data = data
        self.ctx = context
        self.parameters = parameters
        self.reporter = reporter

        self.pipeline = ExecutablePipeline(data, reporter)

    def compile_contexts(self) -> NestedPipelineContext:
        """

        :return:
        """
        full_context = self.pipeline.build_context_manager()
        return full_context


    def execute(self):
        """Execute all compiled operations"""

        scene = self.ctx.scene

        path_root   = Path(self.parameters.save_path)
        amount      = self.parameters.amount
        seed        = self.parameters.seed
        labeling_f  = LabelingFormats.from_string(self.parameters.format)

        # Seed the random library with the user requested seed.
        random.seed(seed)

        index       = 0
        prefix      = self.parameters.prefix
        if self.parameters.from_last and isdir(path_root):
            # We have to inspect the data folder, if there are already fils with the same root and
            # some indexes are already present, start counting from the last
            index = self._analyze_folder_last_index(path_root, prefix)

        # We disable the updates in the viewport so that the program does not crash or lag!
        with NoViewportUpdate():

            full_context = self.compile_contexts()
            with full_context:

                for shot_idx in range(index, index + amount):
                    # Frame context enters/exits each iteration

                    with full_context.frame_context():

                        # Execute pipeline
                        self.pipeline.execute()

                        # Renders
                        write_path = join(path_root, f"{prefix}_{shot_idx}.png")
                        scene.render.filepath = write_path
                        bpy.ops.render.render(write_still=True)

                        # ^ Frame context exits here—restores frame-level state, required for
                        # pipes that require per-frame restoring (e.g. those that act as offset

                # ^ Global contexts exit here—restores global state

        return {'FINISHED'}


    @staticmethod
    def _analyze_folder_last_index(path_root: Path, prefix) -> int:

        files = [f for f in listdir(path_root) if isfile(join(path_root, f))]

        # Find all files matching "prefix_index" pattern
        pattern = re.compile(rf"{re.escape(prefix)}_(\d+)")
        indices = []

        for file in files:
            match = pattern.match(file)
            if match:
                indices.append(int(match.group(1)))

        # Get the last index, or 0 if no matches
        last_index = max(indices) if indices else 0
        next_index = last_index + 1
        return next_index


class NoViewportUpdate:

    def __enter__(self):
        # Disable updates
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Force single update
        bpy.context.view_layer.update()

        # Re-enable viewport
        for area in bpy.context.screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        region.tag_redraw = True
        return False
