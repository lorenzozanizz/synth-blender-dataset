from .compiled_pipeline import ExecutablePipeline
from .generation import NoViewportUpdate
from ..labeling.rule_engine import LabelingEngine

from ..utils.logger import UniqueLogger
from ..labeling.generator import BoundingBoxExtractor
from ..labeling.conversions import convert_camera_centered_to_absolute_pixels_y_inverted
from ..pipeline.bpy_properties import PipelineData
from ..pipeline.context import NestedPipelineContext

from ..utils.timer import TimingContext
from ..utils.images import (draw_bounding_box, draw_bitmap_text, font_size_fit_box_perc,
                            estimate_text_pixel_height)

from typing import Dict, Any
import tempfile
import os

import bpy

class PreviewGenerator:
    """

    """
    _preview_name = "randomizer_preview.png"

    def __init__(self, context, data: PipelineData, parameters, reporter=None):
        """

        :param context:
        :param data:
        :param parameters:
        :param reporter:
        """

        self.data = data
        self.ctx = context
        self.parameters = parameters
        self.reporter = reporter

        self.pipeline = ExecutablePipeline(self.ctx, data, reporter)
        self.path = os.path.join(tempfile.gettempdir(), PreviewGenerator._preview_name)

        # The list of visible objects will be populated when the pipeline is executed once to
        # sample a random shot
        self.used_camera = None

        # Timing statistics
        self.timings: Dict[str, float] = { 'compile': self.pipeline.get_compilation_time() }
        self.estimated_visibility: Dict[Any, float] = dict()

        self.bbox_extractor = BoundingBoxExtractor(context=self.ctx)
        self.engine: LabelingEngine = LabelingEngine(self.ctx)


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

                    # Extract entity data:
                    entity_data = self.engine.extract_entity_data()
                    # Compute the bounding boxes from the scene using the given camera and ray tracing
                    self.bbox_extractor.extract(self.used_camera, ray_casting_ratio=0.1,
                                                entity_data=entity_data, estimate_visibility=True)
                    self.timings['labeling'] = self.bbox_extractor.get_labeling_time()

                    self.estimated_visibility = self.bbox_extractor.get_estimated_visibility()

                # We render in a temp path
                scene.render.filepath = self.path
                with TimingContext(self.timings, 'render'):
                    bpy.ops.render.render(write_still=True)

        # ^ Global contexts exit here—restores global state

        return

    def _open_render_f12_menu(self) -> None:
        """

        """

        # Opens the F12 render window and opens the newly temp rendered file. this file is later
        # opened and modified to draw over boxes, texts, etc...
        bpy.ops.render.opengl('INVOKE_DEFAULT')
        if img := bpy.data.images.get(self.path):
            bpy.data.images.remove(img)
        elif img := bpy.data.images.get(self._preview_name):
            bpy.data.images.remove(img)
        bpy.ops.image.open(filepath=self.path)

    def display_and_render_preview(self,
                                   show_obj_name: bool = True,
                                   show_class_name_or_id: str = "id",
                                   show_obj_boundaries: bool = True,
                                   show_entity: bool = True,
                                   ignore_default_class: str = "",
                                   show_visibility: bool = True,
                                   show_rendering_time: bool = True
                                   ) -> None:
        """
        :param show_entity:
        :param ignore_default_class:
        :param show_visibility:
        :param show_rendering_time:
        :param show_obj_boundaries:
        :param show_obj_name:
        :param show_class_name_or_id:
        :return:
        """

        # Open the render f12 menu, then we will reopen the image and render some statistics
        # using the pixel raster.
        self._open_render_f12_menu()

        scene = self.ctx.scene
        img = bpy.data.images[PreviewGenerator._preview_name]

        # self.visible is a { object, bounding_box } dictionary, but the extraction may have failed
        if not self.bbox_extractor.get_bbox_objects():
            return

        self.engine.create_rule_mappings(self.bbox_extractor.get_visible_objects())

        width = int(scene.render.resolution_x * scene.render.resolution_percentage / 100)
        height = int(scene.render.resolution_y * scene.render.resolution_percentage / 100)

        for obj, xyxy in self.bbox_extractor.get_bbox_objects().items():

            match_class = self.engine.map_obj(obj)
            # Only classified objects have a bounding box and label info
            if not match_class:
                continue
            elif ignore_default_class and match_class.name == ignore_default_class:
                continue
            # Draw the information related to the object, conditional on the render flags and
            # the preview settings.
            self._render_object_info(img, obj.name, obj, xyxy, width, height, cls=match_class,
                 show_class_name_or_id=show_class_name_or_id, show_bounding_boxes=show_obj_boundaries,
                 show_visibility=show_visibility, show_obj_name=show_obj_name)

        if show_entity:

            UniqueLogger.quick_log("ENTITIES" + self.bbox_extractor.get_bbox_entities().__str__())
            for entity, xyxy in self.bbox_extractor.get_bbox_entities().items():

                match_class = self.engine.map_entity(entity)
                # Only classified objects have a bounding box and label info
                if not match_class:
                    continue
                elif ignore_default_class and match_class.name == ignore_default_class:
                    continue
                self._render_object_info(img, entity, entity, xyxy, width, height, cls=match_class,
                                         show_class_name_or_id=show_class_name_or_id,
                                         show_bounding_boxes=show_obj_boundaries,
                                         show_visibility=show_visibility, show_obj_name=show_obj_name)

        if show_rendering_time:
            self._render_bottom_left_time_stats(img, width)

    def _render_object_info(self, img, obj_name, obj_key, xyxy: tuple[float, float, float, float],
                            width: int, height: int, cls,
                            # Flags which are used to conditionally draw various elements in the object info
                            show_bounding_boxes: bool = True, show_obj_name: bool = True,
                            show_class_name_or_id: str = "id", show_visibility: bool = True,
                            show_unoccluded_bbox: bool = True) -> None:
        """

        :param img:
        :param obj_name:
        :param obj_key:
        :param xyxy:
        :param width:
        :param height:
        :param cls:
        :return:
        """
        # new_xyxy is the bounding box in pixel integer space
        # We have to invert the ys, because blender image pixel API has the y values of the bottom row
        # as 0, which is the opposite way
        new_xyxy = convert_camera_centered_to_absolute_pixels_y_inverted(xyxy, width, height)
        p0 = (new_xyxy[0], new_xyxy[1])
        p1 = (new_xyxy[2], new_xyxy[3])

        color_prop = tuple(cls.color)
        color = (color_prop[0], color_prop[1], color_prop[2], color_prop[3])

        box_width = abs(new_xyxy[0] - new_xyxy[2])
        # Draw the bounding box first, so that the text is visible in all cases, hopefully.
        if show_bounding_boxes:
            draw_bounding_box(img, color, p0, p1, y_grows_up_to_down=False, line_width=4)
        if show_unoccluded_bbox:
            pass
        if show_obj_name or (show_class_name_or_id != "none"):

            text = f"" if show_class_name_or_id == "none" else \
                f" {cls.name}" if show_class_name_or_id == "name" else f"{cls.class_id}"
            if show_obj_name:
                text = f"{obj_name}" + (" - " if text else "") + text
            # Generate in a single pass the text to be written, then write it.

            font_size = font_size_fit_box_perc(text, box_width, 0.9)
            y_min = min(p0[1], p1[1])
            draw_bitmap_text(
                img, text, (p0[0] + 20, 10 + y_min + estimate_text_pixel_height("", font_size)),
                color=color, size=font_size)

        if show_visibility:
            estimated_visibility = self.estimated_visibility[obj_key]
            # estimated_occlusion = float(estimate_occlusion_3d(obj, self.used_camera, self.ctx, scene.render, xyxy))
            text = f"{int(estimated_visibility * 100)}%"

            font_size = font_size_fit_box_perc(text, box_width, 0.3)
            y_max = max(p0[1], p1[1])
            draw_bitmap_text(img, text, (p0[0] + 20, y_max - 10),
                             color=color, size=font_size)


    def _render_bottom_left_time_stats(self, img, width: int) -> None:
        """

        :return:
        """

        text = (f"Compiled in {self.timings['compile']:.2f}s, rendered in {self.timings['render']:.2f}s, "
                f"labeled in {self.timings['labeling']:.2f}s")

        font_size = font_size_fit_box_perc(text, width, 0.4)
        draw_bitmap_text(img, text,
         (10, 10 + estimate_text_pixel_height("", font_size)),
            color=None, size=font_size
        )


    def _render_bottom_right_statistics(self) -> None:
        """

        :return:
        """
        num_objects = len(self.visible_objects)
