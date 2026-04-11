from .names import Labels
from ..core.generation import ExecutionParameters, Executor

from typing import Union
from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = Labels.GENERATE.value
    bl_label = "Generate Dataset"

    @staticmethod
    def validate_data_extract(context) -> Union[None, ExecutionParameters]:
        """

        :param context:
        :return:
        """
        scene = context.scene

        return ExecutionParameters(
            scene.randomizer_seed,
            scene.randomizer_amount,
            scene.randomizer_save_prefix,
            scene.randomizer_label_format,
            scene.randomizer_append_checkbox,
            scene.randomizer_destination_path
        )

    def execute(self, context):
        """

        :param context:
        :return:
        """
        # Extract the data from the scene, e.g. the properties of the "Generate" panel which
        # include the number of images, the seed and saving options
        params = self.validate_data_extract(context)

        pipeline = context.scene.pipeline_data
        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        executor = Executor(context, pipeline, params, reporter=self)

        try:
            # Entrust the deserialization and execution of the pipeline to the executor object. Any exception
            # during the execution will be caught and the user notified.
            # ( Note: invalid pipes are ignored, IO is handled by the executor )
            # Internally, the executor will compile the pipeline and distributions, will construct the
            # context managers and execute the pipeline for every different synthesis
            executor.execute()

        except Exception as e:
            self.report({'ERROR'}, f"Generation failed: {str(e)}")
            return { 'CANCELLED' }

        return { 'FINISHED' }