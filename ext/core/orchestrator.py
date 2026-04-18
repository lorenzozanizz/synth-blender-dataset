from .configurations import LabelExtractionConfig
from .io import LabelWriter

from ..labeling.serialization import LabelData, Formatter, YoloFormatter
from ..labeling.class_engine import ClassificationEngine
from ..labeling.generator import Extractor, BoundingBoxExtractor, PolygonExtractor
from ..labeling.raytracing import get_visible_objects_from_camera

from typing import Union, Dict, Tuple, Collection, Any


class LabelingOrchestrator:

    def __init__(self, context, config: LabelExtractionConfig, reporter, writer: LabelWriter):
        self.config = config
        self.ctx = context

        # To report issues and errors in the generation
        self.reporter = reporter

        self.classifier = ClassificationEngine(self.ctx )
        self.visible_objects = None

        # Explicitly instantiate the label formatter and extractor based on the configuration
        self.extractor: Extractor = self._create_extractor()
        self.formatter: Formatter = self._create_formatter()

        self.writer = writer

        self.label_data = None

    def execute(self, camera, depsgraph) -> None:
        """

        :param camera:
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
            self.ctx.scene, depsgraph, camera,
            resolution_x=res_x, resolution_y=res_y, compute_mapping=True)

        # Compute the bbox/polygon/etc from the scene using the given camera and ray tracing
        self.classifier.classify_visible_objects(
            self.visible_objects.values()
        )

        label_data = self.extractor.extract(
            visible_objects=self.visible_objects,
            classifier=self.classifier,
            entity_data=entity_scene_data,
            camera=camera,
            estimate_visibility=self.config.estimate_visibility
        )

        if self.config.write_labels:
            files = self.formatter.format(label_data)
            self.writer.write_label(files)

        return

    def _create_formatter(self) -> Formatter:
        return YoloFormatter()

    def _create_extractor(self):
        return BoundingBoxExtractor(self.ctx)

    def get_last_label_data(self) -> Union[None, LabelData]:
        return self.label_data

    def get_raw_visible_data(self) -> dict[Any, Collection]:
        """

        :return:
        """
        return self.visible_objects

    def get_visible_amount(self) -> Tuple[int, int, int]:
        """

        :return:
        """
        match_amt = tuple((0, 0, 0))

        # Just ensure they really are the sum, TBR
        assert match_amt[0] == match_amt[1] + match_amt[2]
        return match_amt


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