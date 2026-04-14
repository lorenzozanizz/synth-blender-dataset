from .compiled_pipeline import ExecutablePipeline
from .generation import NoViewportUpdate
from ..labeling.rule_engine import LabelingEngine
from ..utils.logger import UniqueLogger
from ..labeling.raytracing import get_visible_objects_from_camera, estimate_occlusion_3d
from ..labeling.conversions import one_minus_one_centered_into_absolute_pixels_0y_top
from ..pipeline.bpy_properties import PipelineData
from ..pipeline.context import NestedPipelineContext

from ..utils.images import draw_bounding_box, draw_bitmap_text, estimate_text_pixel_width, estimate_text_pixel_height

import random
from typing import Dict
import tempfile
import os
import bpy
import time


class PreviewGenerator:
    """

    """
    _preview_name = "randomizer_preview.png"

    def __init__(self, context, data: PipelineData, parameters, reporter=None):
        self.data = data
        self.ctx = context
        self.parameters = parameters
        self.reporter = reporter

        self.pipeline = ExecutablePipeline(self.ctx, data, reporter)
        self.path = os.path.join(tempfile.gettempdir(), PreviewGenerator._preview_name)

        # The list of visible objects will be populated when the pipeline is executed once to
        # sample a random shot
        self.visible = None
        self.used_camera = None

        # Timing statistics
        self.render_time = None
        self.labeling_time = None
        self.compilation_time = self.pipeline.get_compilation_time()

    def compile_contexts(self) -> NestedPipelineContext:
        """
        :return:
        """
        full_context = self.pipeline.build_context_manager()
        return full_context

    def execute(self):
        """

        """

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

                default_camera = self.ctx.scene.camera
                if not default_camera:
                    self.reporter.report({'WARNING'}, "No default camera was set, no labels preview could be generated")
                else:
                    self.used_camera = default_camera
                    res_ratio = 0.1
                    res_x = int(self.ctx.scene.render.resolution_x * res_ratio)
                    res_y = int(self.ctx.scene.render.resolution_y * res_ratio)

                    self.labeling_time = time.time()

                    self.visible: Dict = get_visible_objects_from_camera(
                        self.ctx.scene, self.ctx.evaluated_depsgraph_get(), default_camera,
                        resolution_x=res_x, resolution_y=res_y, compute_bounding_boxes=True)
                    self.labeling_time = time.time() - self.labeling_time


                # We render in a temp path
                self.render_time = time.time()
                scene.render.filepath = self.path
                bpy.ops.render.render(write_still=True)
                self.render_time = time.time() - self.render_time

        # ^ Global contexts exit here—restores global state

        return { 'FINISHED' }

    def display_and_render_preview(self,
        show_obj_name: bool = True,
        show_class_name_or_id: str = "id",
        show_bounding_boxes: bool = True,
        show_convex_hull: bool = True,
        draw_default_class: bool = False,
        show_occlusion: bool = True,
        show_rendering_time: bool = True
    ) -> None:
        """
        :param show_convex_hull:
        :param show_occlusion:
        :param show_rendering_time:
        :param show_bounding_boxes:
        :param show_obj_name:
        :param show_class_name_or_id:
        :return:
        """

        scene = self.ctx.scene
        # Opens the F12 render window and opens the newly temp rendered file. this file is later
        # opened and modified to draw over boxes, texts, etc...
        bpy.ops.render.opengl('INVOKE_DEFAULT')
        bpy.ops.image.open(filepath=self.path)

        img = bpy.data.images[PreviewGenerator._preview_name]

        # self.visible is a { object, bounding_box } dictionary, but the extraction may have failed
        if not self.visible:
            return
        visible_objects = self.visible

        UniqueLogger.quick_log({obj.name : xyxy for obj, xyxy in visible_objects.items()}.__str__())
        engine = LabelingEngine(self.ctx)
        engine.create_rule_mappings(visible_objects.keys())
        UniqueLogger.quick_log("mappings" + engine.get_mapping().__str__())

        width = int(scene.render.resolution_x * scene.render.resolution_percentage / 100)
        height = int(scene.render.resolution_y * scene.render.resolution_percentage / 100)

        base_size = 4  # arbitrary reference size

        for obj, xyxy in visible_objects.items():

            UniqueLogger.quick_log("Evaluating" + obj.name)

            cls = engine.get(obj)
            # Only classified objects have a bounding box and label info
            if not cls:
                UniqueLogger.quick_log("NOT CLASSED" + obj.name)

                continue

            new_xyxy = one_minus_one_centered_into_absolute_pixels_0y_top(xyxy, width, height)

            UniqueLogger.quick_log(f"Pixel bbox before: ({xyxy}) -> {obj.name}")
            UniqueLogger.quick_log(f"Pixel bbox: ({new_xyxy}) -> {obj.name}")

            # We have to invert the ys, because blender image pixel API has the y values of the bottom row
            # as 0, which is the opposite way
            p0 = (new_xyxy[0], height-new_xyxy[1])
            p1 = (new_xyxy[2], height-new_xyxy[3])
            color_prop = tuple(cls.color)
            color = (color_prop[0], color_prop[1], color_prop[2], color_prop[3])

            box_width = abs(new_xyxy[0] - new_xyxy[2])
            # Draw the bounding box first, so that the text is visible in all cases, hopefully.
            if show_bounding_boxes:
                draw_bounding_box(img, color, p0, p1, y_grows_up_to_down=False, line_width=4)
            if show_obj_name or (show_class_name_or_id != "none"):

                text = f"" if show_class_name_or_id == "none" else \
                    f" {cls.name}" if show_class_name_or_id == "name" else f"{cls.class_id}"
                if show_obj_name:
                    text = f"{obj.name}" + (" - " if text else "") + text
                # Generate in a single pass the text to be written, then write it.
                base_width = estimate_text_pixel_width(text, base_size)

                scale = box_width / base_width
                font_size = max(2, int(base_size * scale))
                y_min = min(p0[1], p1[1])
                draw_bitmap_text(
                    img, text, (p0[0]+ 20, 10 + y_min + estimate_text_pixel_height("", font_size)),
                    color=color, size=font_size)

            if show_occlusion:

                estimated_occlusion = float(estimate_occlusion_3d(obj, self.used_camera, self.ctx, scene.render, xyxy))
                text = f"{int(estimated_occlusion * 100)}%"
                base_width = estimate_text_pixel_width(text, base_size)

                scale = box_width / base_width
                font_size = max(2, int(base_size * scale * 0.3))
                y_max = max(p0[1], p1[1])
                draw_bitmap_text(
                    img, text, (p0[0] + 20, y_max - 10),
                    color=color, size=font_size)

        if show_rendering_time:

            text = (f"Compiled in {self.compilation_time:.2f}s, "
                    f"rendered in {self.render_time:.2f}s, "
                    f"labeled in {self.labeling_time:.2f}s")

            base_width = estimate_text_pixel_width(text, base_size)

            scale = width / base_width
            font_size = max(2, int(base_size * scale* 0.4))
            draw_bitmap_text(img, text, ( 10, 10 + estimate_text_pixel_height("", font_size) ), color=None, size=font_size)