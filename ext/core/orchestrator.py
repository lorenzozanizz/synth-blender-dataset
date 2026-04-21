from .configurations import LabelExtractionConfig
from .io import OutputWriter, SerializationStrategy, YoloFormatter

from ..labeling.generator import LabelData
from ..labeling.class_engine import ClassificationEngine
from ..labeling.generator import Extractor, BoundingBoxExtractor, PolygonExtractor
from ..labeling.ray_casting import get_visible_objects_from_camera

from typing import Union, Dict, Tuple, Collection, Any


class LabelingOrchestrator:

    def __init__(self, context, config: LabelExtractionConfig, reporter, writer: Union[None, OutputWriter]):
        self.config = config
        self.ctx = context

        # To report issues and errors in the generation
        self.reporter = reporter

        self.classifier = ClassificationEngine(self.ctx )
        self.visible_objects = None

        # Explicitly instantiate the label formatter and extractor based on the configuration
        self.extractor: Extractor = self._create_extractor()

        self.writer: OutputWriter = writer
        if self.writer:
            self.formatter: SerializationStrategy = self._create_formatter()
            self.writer.set_strategy(self.formatter)

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
            self.visible_objects.keys()
        )

        self.label_data = self.extractor.extract(
            visible_objects=self.visible_objects,
            classifier=self.classifier,
            entity_data=entity_scene_data,
            camera=camera,
            estimate_visibility=self.config.estimate_visibility
        )

        if self.config.write_labels and self.writer is not None:
            files = self.formatter.format(self.label_data)
            self.writer.write_label(files)

        return

    def begin_generation(self) -> None:
        """

        :return:
        """
        pass

    def end_generation(self) -> None:
        """

        :return:
        """

    def _create_formatter(self) -> Union[None, SerializationStrategy]:
        if self.writer is None:
            return None
        return YoloFormatter(write_config=self.writer.get_config())

    def _create_extractor(self):
        return PolygonExtractor(self.ctx)

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