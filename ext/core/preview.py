from ..labeling import LabelingFormats
from .compiled_pipeline import ExecutablePipeline
from .generation import NoViewportUpdate
from ..pipeline.bpy_properties import PipelineData, PipelineOperation
from ..pipeline.operation_registry import OperationRegistry
from ..pipeline.context import NestedPipelineContext
from ..labeling.raytracing import get_visible_objects_from_camera
from ..utils.logger import UniqueLogger
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

class PreviewGenerator:


    def __init__(self, context, data: PipelineData, parameters, reporter=None):
        self.data = data
        self.ctx = context
        self.parameters = parameters
        self.reporter = reporter

        self.pipeline = ExecutablePipeline(self.ctx, data, reporter)

    def compile_contexts(self) -> NestedPipelineContext:
        """

        :return:
        """
        full_context = self.pipeline.build_context_manager()
        return full_context

    def execute(self):
        """Execute all compiled operations"""

        scene = self.ctx.scene
        seed = self.parameters.seed

        # Seed the random library with the user requested seed.
        random.seed(seed)

        # We disable the updates in the viewport so that the program does not crash or lag!
        # In the future, this will be set in the settings!
        update_viewport = NoViewportUpdate(disable=False)

        with update_viewport:

            full_context = self.compile_contexts()
            with full_context:

                    # Execute pipeline
                self.pipeline.execute()

                # We render in a temp path
                scene.render.filepath = "write_path"
                bpy.ops.render.render(write_still=True)

        # ^ Global contexts exit here—restores global state

        return {'FINISHED'}

    def display_and_render_preview(self) -> None:

        bpy.ops.render.opengl('INVOKE_DEFAULT')
        bpy.ops.image.open(filepath="Path")

        img = bpy.data.images['Path']
