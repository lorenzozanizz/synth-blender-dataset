from .executable_pipeline import ExecutablePipeline

from ..labeling import LabelingFormats
from ..pipeline.bpy_properties import PipelineData
from ..pipeline.context import NestedPipelineContext


import random
import re
from dataclasses import dataclass
from pathlib import Path
from os import listdir
from os.path import isdir, isfile, join

import bpy

@dataclass
class GenerationConfig:
    """

    """

    seed: int
    amount: int

    from_last: bool
    save_path: str
    prefix: str

    format: str
    do_labeling: bool

class Executor:
    """Compiled, reusable pipeline executor"""

    def __init__(self, context, data: PipelineData, parameters, reporter = None):
        self.data = data
        self.ctx = context
        self.parameters: GenerationConfig = parameters
        self.reporter = reporter

        self.pipeline = ExecutablePipeline(self.ctx, data, reporter)
        self.io_manager = None

        self.classifier = None

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
        do_labeling = self.parameters.do_labeling
        labeling_f  = self.parameters.format
        # Seed the random library with the user requested seed.
        random.seed(seed)

        start_idx       = 0
        prefix      = self.parameters.prefix
        if self.parameters.from_last and isdir(path_root):
            # We have to inspect the data folder, if there are already fils with the same root and
            # some indexes are already present, start counting from the last
            start_idx = self._analyze_folder_last_index(path_root, prefix)

        # We disable the updates in the viewport so that the program does not crash or lag!
        # In the future, this will be set in the settings!
        update_viewport = NoViewportUpdate(disable=False)

        # Generate the progress bar
        wm = self.ctx.window_manager
        wm.progress_begin(0, amount)

        try:
            with update_viewport:

                full_context = self.compile_contexts()
                with full_context:

                    for shot_idx in range(start_idx, start_idx + amount):
                        # Frame context enters/exits each iteration

                        with full_context.frame_context():

                            # Execute pipeline
                            self.pipeline.execute()

                            # Extract classifications
                            classifications = self.classifier.classify_visible_objects(
                                self.pipeline.get_visible_objects()
                            )

                            # Run generation pipeline (handles extraction + formatting)
                            self.label_data = self.generation_pipeline.execute(
                                visible_objects=self.pipeline.get_visible_objects(),
                                classifications=classifications,
                                camera=camera,
                                depsgraph=self.ctx.evaluated_depsgraph_get(),
                                render_settings=self.ctx.scene.render
                            )

                            write_path = self.io_manager.get_path_for(shot_idx)

                            # Renders
                            write_path = join(path_root, f"{prefix}_{shot_idx}.png")
                            scene.render.filepath = write_path
                            bpy.ops.render.render(write_still=True)

                        # ^ Frame context exits here—restores frame-level state, required for
                        # pipes that require per-frame restoring (e.g. those that act as offset
                        wm.progress_update(shot_idx-start_idx)

                    # ^ Global contexts exit here—restores global state
        finally:
            wm.progress_end()

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

        # Get the last index, or -1 (which becomes 0 when i add +1) if no matches
        last_index = max(indices) if indices else -1
        next_index = last_index + 1
        return next_index


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
