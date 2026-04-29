"""

"""

from typing import Any, Collection

from .. import file_type, StorageSpec, extension
from ....labeling.conversions import convert_camera_centered_to_yolo
from ....labeling.generator.data_structure import *
from ...configurations import RenderConfig, WritingConfig
from ..io_strategy import IOStrategy, FormatSpecification
from ..registry import LabelingFormatRegistry
from . import SupportedFormats


@LabelingFormatRegistry.register_strategy(SupportedFormats.YOLO.value)
class YoloFormatter(IOStrategy):
    """

    """

    def __init__(self, write_config: WritingConfig, config: dict):
        super().__init__(write_config, config)
        self.bbox_precision = config.get('bbox_precision') or 3
        self.split = config.get('split') or ''

    def serialize_image_labels(self, transformed: list[dict]) -> Collection[tuple[file_type, extension, str]]:
        lines = []
        for label in transformed:
            cls_id = label['id']
            yolo_coos = label['bbox']

            lines.append(f"{cls_id} "
                         f"{yolo_coos[0]:.{self.bbox_precision}f} "
                         f"{yolo_coos[1]:.{self.bbox_precision}f} "
                         f"{yolo_coos[2]:.{self.bbox_precision}f} "
                         f"{yolo_coos[3]:.{self.bbox_precision}f}\n")

        return ('label', '.txt', "".join(lines)),

    def get_storage_spec(self) -> StorageSpec:
        pass

    def get_subdir_for(self, shot_id: int, f_type: file_type | Literal["image"]) -> str:
        """

        :param shot_id:
        :param f_type:
        :return:
        """
        if f_type == "image":
            return (self.split + "/" if self.split else "") + "images/"
        else: return (self.split + "/" if self.split else "") + "labels/"

    def get_filename_for(self, shot_id: int, f_type: file_type | Literal["image"]) -> str:
        return f"{self.write_cfg.prefix}_{shot_id}"

    def transform_annotation(self, label: Label, shot_idx: int, shot_config: RenderConfig) -> dict[str, Any]:
        if not label.annotation_type == "bbox":
            raise RuntimeError("Wrong annotation type in YOLO formatter!")
        bbox = label.bbox
        return {
            'bbox': convert_camera_centered_to_yolo(bbox),
            'id': label.cls.class_id
        }

    def get_specification(self) -> FormatSpecification:

        return FormatSpecification(
            # Data structure
            single_file_per_image = True,
            global_metadata_required = False,
            # Annotation grouping
            aggregation_strategy = "per_image",
            # Hooks
            requires_class_declaration = False,
            supports_image_metadata = False,
            # Core geometry types
            requires_bbox = True
        )

    def aggregate_batch(self, annotations, batch_metadata):
        # Not used for per-image format
        raise NotImplementedError("Should not be used!")

    def finalize(self, aggregated):
        # Not used for per-image format
        raise NotImplementedError("Should not be used!")

