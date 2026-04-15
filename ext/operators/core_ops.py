from .names import Labels
from ..core.generation import ExecutionParameters, Executor
from ..core.preview import PreviewGenerator

import traceback
from typing import Union
from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = Labels.GENERATE.value
    bl_label = "Generate Dataset"

    def validate_data_extract(self, context) -> Union[None, ExecutionParameters]:
        """

        :param context:
        :return:
        """
        scene = context.scene
        amount = scene.randomizer_amount
        if amount <= 0:
            self.report({'ERROR'}, 'Cannot generate: invalid amount of images')
            return None
        save_prefix = scene.randomizer_save_prefix
        if not save_prefix:
            self.report({'ERROR'}, 'Cannot generate: invalid save prefix')
            return None
        dest_path = scene.randomizer_destination_path
        if not dest_path:
            self.report({'ERROR'}, 'Cannot generate: invalid destination path')
            return None

        return ExecutionParameters(
            scene.randomizer_seed,
            amount,
            scene.randomizer_append_checkbox,
            dest_path,
            save_prefix,
            scene.randomizer_label_format,
            scene.randomizer_do_labelize
        )

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # Extract the data from the scene, e.g. the properties of the "Generate" panel which
        # include the number of images, the seed and saving options
        params_or_error = self.validate_data_extract(context)
        if params_or_error is None:
            return { 'CANCELLED'}

        pipeline = context.scene.pipeline_data
        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        executor = Executor(context, pipeline, params_or_error, reporter=self)

        try:
            # Entrust the deserialization and execution of the pipeline to the executor object. Any exception
            # during the execution will be caught and the user notified.
            # ( Note: invalid pipes are ignored, IO is handled by the executor )
            # Internally, the executor will compile the pipeline and distributions, will construct the
            # context managers and execute the pipeline for every different synthesis
            executor.execute()

        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {traceback.format_exc()}")
            return { 'CANCELLED' }

        return { 'FINISHED' }



class PreviewOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = Labels.PREVIEW_SAMPLE.value
    bl_label = "Generate Dataset"

    def validate_data_extract(self, context) -> Union[None, ExecutionParameters]:
        """

        :param context:
        :return:
        """
        scene = context.scene
        # No checks are required
        return ExecutionParameters(
            scene.randomizer_seed,      scene.randomizer_amount,
            scene.randomizer_save_prefix,   scene.randomizer_label_format,
            scene.randomizer_append_checkbox,   scene.randomizer_destination_path,
            scene.randomizer_do_labelize
        )

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # Extract the data from the scene, e.g. the properties of the "Generate" panel which
        # include the number of images, the seed and saving options
        params_or_error = self.validate_data_extract(context)
        if params_or_error is None:
            return { 'CANCELLED' }

        pipeline = context.scene.pipeline_data
        preview = PreviewGenerator(context, pipeline, params_or_error, reporter=self)

        # extract the default class
        default_class = context.scene.labeling_data.default_class
        if not default_class or default_class.lower() == "None":
            default_class = ""
        try:
            # ( Note: invalid pipes are ignored, IO is handled by the executor )
            # Internally, the executor will compile the pipeline and distributions, will construct the
            # context managers and execute the pipeline for every different synthesis
            preview.execute()
            preview.display_and_render_preview(ignore_default_class=default_class)

        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {traceback.format_exc()}")
            return { 'CANCELLED' }

        return { 'FINISHED' }