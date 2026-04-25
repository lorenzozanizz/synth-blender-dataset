import random
import bpy

from ..pipeline.bpy_properties import PipelineData
from ..pipeline.context import NestedPipelineContext

from .executable_pipeline import ExecutablePipeline
from .orchestrator import LabelingOrchestrator
from .configurations import LabelExtractionConfig, GenerationConfig, WritingConfig
from .io import OutputWriter


class Executor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, context, data: PipelineData,
         gen_params: GenerationConfig,
         label_params: LabelExtractionConfig,
         write_params: WritingConfig,
         reporter = None
    ):
        self.data = data
        self.ctx = context
        self.parameters: GenerationConfig = gen_params
        self.reporter = reporter

        self.pipeline: ExecutablePipeline = ExecutablePipeline(self.ctx, data, reporter)
        self.writer = OutputWriter(write_params, gen_params)
        self.labeling_orchestrator: LabelingOrchestrator = LabelingOrchestrator(
            self.ctx,
            # Parameters which control the folder structure, labeling etc...
            label_params,
            reporter,
            # The orchestrator will assign the label serialization strategy to the writer
            writer=self.writer
        )

    def compile_contexts(self) -> NestedPipelineContext:
        """

        :return:
        """
        full_context = self.pipeline.build_context_manager()
        return full_context


    def execute(self):
        """Execute all compiled operations"""

        scene       = self.ctx.scene
        amount      = self.parameters.amount
        seed        = self.parameters.seed

        # Seed the random library with the user requested seed.
        random.seed(seed)

        start_idx   = self.writer.compute_starting_index()

        # We disable the updates in the viewport so that the program does not crash or lag!
        # In the future, this will be set in the settings!
        update_viewport = NoViewportUpdate(disable=False)
        default_camera = self.ctx.scene.camera

        # Generate the progress bar
        wm = self.ctx.window_manager
        wm.progress_begin(0, amount)

        try:
            with update_viewport:

                full_context = self.compile_contexts()
                with full_context:

                    for shot_idx in range(start_idx, start_idx + amount):
                        # Frame context enters/exits each iteration

                        self.writer.set_shot_index(shot_idx)
                        with full_context.frame_context():

                            # Execute pipeline
                            self.pipeline.execute()

                            # Run generation pipeline (handles extraction + formatting)
                            self.labeling_orchestrator.execute(
                                camera=default_camera,
                                depsgraph=self.ctx.evaluated_depsgraph_get()
                            )

                            write_path = self.writer.get_image_write_path()

                            # Renders
                            scene.render.filepath = write_path
                            bpy.ops.render.render(write_still=True)

                        # ^ Frame context exits here—restores frame-level state, required for
                        # pipes that require per-frame restoring (e.g. those that act as offset
                        wm.progress_update(shot_idx-start_idx)

                    # ^ Global contexts exit here—restores global state
        finally:
            wm.progress_end()

        return {'FINISHED'}



class NoViewportUpdate:

    def __init__(self, disable):
        self.disable = disable

    def __enter__(self):
        # Disable the visibility of everything in the viewport only (not the rendering)
        # this will be restored at the end
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
        return False
