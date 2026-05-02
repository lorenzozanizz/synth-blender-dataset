from .names import Labels
from ..core.configurations import PreviewRenderConfig, GenerationConfig, WritingConfig, LabelExtractionConfig
from ..core.generation import Executor
from ..core.preview import PreviewGenerator

import traceback
from typing import Union, Optional
from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = Labels.GENERATE.value
    bl_label = "Generate Dataset"

    def validate_extract_gen_config(self, context) -> Optional[GenerationConfig]:
        """

        :param context:
        :return:
        """
        scene = context.scene
        amount = scene.randomizer_amount
        if amount <= 0:
            self.report({'ERROR'}, 'Cannot generate: invalid amount of images')
            return None
        return GenerationConfig(scene.randomizer_seed, amount)

    def validate_extract_label_config(self, context) -> Optional[LabelExtractionConfig]:
        """

        :param context:
        :return:
        """
        scene = context.scene
        return LabelExtractionConfig(
            scene.randomizer_label_format,
            dict(),
            scene.randomizer_do_labelize
        )

    def validate_io_write_config(self, context) -> Optional[WritingConfig]:
        """

        :param context:
        :return:
        """

        scene = context.scene
        save_prefix = scene.randomizer_save_prefix
        if not save_prefix:
            self.report({'ERROR'}, 'Cannot generate: invalid save prefix')
            return None
        dest_path = scene.randomizer_destination_path
        if not dest_path:
            self.report({'ERROR'}, 'Cannot generate: invalid destination path')
            return None
        from_last = scene.randomizer_append_checkbox
        out_format = scene.render.image_settings.file_format
        return WritingConfig(from_last, dest_path, save_prefix, image_extension=out_format)

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # Extract the data from the scene, e.g. the properties of the "Generate" panel which
        # include the number of images, the seed and saving options
        gen_config = self.validate_extract_gen_config(context)
        label_config = self.validate_extract_label_config(context)
        io_write_config = self.validate_io_write_config(context)

        if gen_config is None or label_config is None or io_write_config is None:
            return { 'CANCELLED' }

        pipeline = context.scene.pipeline_data
        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        executor = Executor(
            context, pipeline,
            gen_params=gen_config,
            label_params=label_config,
            write_params=io_write_config,
            reporter=self
        )

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

    def validate_data_extract(self, context) -> Optional[PreviewRenderConfig]:
        """

        :param context:
        :return:
        """
        # No checks are required
        return PreviewRenderConfig()

    def validate_extract_label_config(self, context) -> Optional[LabelExtractionConfig]:
        """

        :param context:
        :return:
        """

        # Extraction the labeling config.


        scene = context.scene
        return LabelExtractionConfig(
            scene.randomizer_label_format,
            dict(),
            scene.randomizer_do_labelize
        )

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # Extract the data from the scene, e.g. the properties of the "Generate" panel which
        # include the number of images, the seed and saving options
        preview_config = self.validate_data_extract(context)
        label_config = self.validate_extract_label_config(context)

        if preview_config is None or label_config is None:
            return { 'CANCELLED' }

        pipeline = context.scene.pipeline_data
        preview = PreviewGenerator(context, pipeline,
            preview_config, label_config, reporter=self)

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