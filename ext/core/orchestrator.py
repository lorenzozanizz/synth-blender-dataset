from .configurations import LabelExtractionConfig, RenderConfig, GenerationConfig, BatchMetadata
from .io import OutputWriter

from ..labeling.generator import LabelData
from ..labeling.class_engine import ClassificationEngine
from ..labeling.generator import Extractor, BoundingBoxExtractor
from ..labeling.ray_casting import get_visible_objects_from_camera

from typing import Dict, Collection, Any, Optional


class LabelingOrchestrator:

    def __init__(self, context, config: LabelExtractionConfig, reporter, writer: Optional[OutputWriter]):
        self.config = config
        self.ctx = context

        # To report issues and errors in the generation
        self.reporter = reporter

        self.classifier = ClassificationEngine(self.ctx)
        self.visible_objects = None

        # Explicitly instantiate the label formatter and extractor based on the configuration
        self.extractor: Extractor = self._create_extractor()

        self.writer: OutputWriter = writer

        self.label_data = None

    def process_shot(self, render_cfg: RenderConfig, depsgraph) -> None:
        """

        :param render_cfg: The configuration of the rendered shot, including camera, width, height,
            etc...
        :param depsgraph:
        :return:
        """
        # Extract the visible objects from the scene, this corresponds to a dictionary mapping
        # blender 'Object' to a point cloud representing raytracing hits. Depending on the
        # labeling type, this becomes a polygon or a box or depth data (TBI)

        # Step 1] Extract the entity data from the scene, which is to be used by the extractor to
        # compose together multi-object entities.
        entity_scene_data = self.classifier.extract_entity_data()

        # Step 2] Extract the visible entities which are going to be bound and classified by the
        # extractor and classifier

        res_x = int(self.ctx.scene.render.resolution_x * self.config.ray_casting_ratio)
        res_y = int(self.ctx.scene.render.resolution_y * self.config.ray_casting_ratio)
        self.visible_objects = get_visible_objects_from_camera(
            self.ctx.scene, depsgraph, render_cfg.camera,
            resolution_x=res_x, resolution_y=res_y, compute_mapping=True)

        # Compute the bbox/polygon/etc from the scene using the given camera and ray tracing
        self.classifier.classify_visible_objects(
            self.visible_objects.keys()
        )

        self.label_data: LabelData = self.extractor.extract(
            visible_objects=self.visible_objects,
            classifier=self.classifier,
            entity_data=entity_scene_data,
            camera=render_cfg.camera,
            estimate_visibility=self.config.estimate_visibility
        )

        if self.config.write_labels and self.writer is not None:
            # files = self.formatter.format(self.label_data, render_config)
            self.writer.write_shot(self.label_data, render_cfg)

        return

    def begin_generation(self, gen_cfg: GenerationConfig) -> None:
        """

        :return:
        """
        # Propagate the beginning of generation hook to the writer.
        # the batch config is used to aggregate the data at the end of generation
        batch_metadata = BatchMetadata(
            gen_cfg.amount,
            self.classifier.get_classes()
        )
        self.writer.begin_batch(batch_metadata)

    def end_generation(self) -> None:
        """

        :return:
        """
        # Propagate the end of generation to the writer.
        self.writer.end_batch()

    def _create_extractor(self):
        return BoundingBoxExtractor(self.ctx)

    def get_last_label_data(self) -> Optional[LabelData]:
        return self.label_data

    def get_raw_visible_data(self) -> dict[Any, Collection]:
        """

        :return:
        """
        return self.visible_objects

    # ----- A set of timing routines to provide an interface to display them in the preview -----

    def get_timings(self) -> Dict[str, float]:
        """ """
        pass

    def get_raytracing_timing(self) -> float:
        """ """
        pass

    def get_classification_timing(self) -> float:
        """ """
        pass

    def get_io_timing(self) -> float:
        """ """
        pass