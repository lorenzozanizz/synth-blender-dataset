"""
COCO format strategy for bounding box object detection.
Generates COCO-formatted JSON with image metadata and annotations.
"""

import json
from typing import Any, Collection, Literal
from datetime import datetime
from os.path import join

from .. import file_type, StorageSpec, extension
from ....labeling.conversions import convert_camera_centered_to_coco
from ....labeling.generator.data_structure import *
from ...configurations import RenderConfig, WritingConfig, BatchMetadata
from ..io_strategy import IOStrategy, FormatSpecification
from ..registry import LabelingFormatRegistry
from . import SupportedFormats


@LabelingFormatRegistry.register_strategy(SupportedFormats.COCO.value)
class COCOFormatter(IOStrategy):
    """
    COCO format implementation for bounding box detection.
    Generates a single JSON file per batch with all images and annotations.
    """

    def ensure_directories(self) -> None:
        image_dir = join(self.write_cfg.save_path, (self.split + "/" if self.split else "") + "images/")
        self._make_dirs([image_dir])

    def __init__(self, write_config: WritingConfig, config: dict):
        super().__init__(write_config, config)
        self.bbox_precision = config.get('bbox_precision') or 2
        self.split = config.get('split') or ''

        # COCO structure - accumulated during batch processing
        self.coco_data = {
            "info": {
                "description": "Synthetically generated dataset using the Blendersynth extension",
                "version": "1.0",
                "year": datetime.now().year,
            },
            "images": [],
            "annotations": [],
            "categories": []
        }
        self.annotation_id_counter = 1
        self.marked_img_ids = set()

    def get_specification(self) -> FormatSpecification:
        return FormatSpecification(
            # Data structure
            single_file_per_image=False,  # COCO uses one global file
            global_metadata_required=True,
            # Annotation grouping
            aggregation_strategy="global",  # All images aggregated into one file
            # Hooks
            requires_class_declaration=True,
            supports_image_metadata=True,
            # Core geometry types
            requires_bbox=True
        )

    def get_storage_spec(self) -> StorageSpec:
        return StorageSpec(
            single_file_per_image=False
        )

    def get_subdir_for(self, shot_id: int, f_type: file_type | Literal["image"]) -> str:
        """
        COCO structure: images/ folder for images, root for annotations.json
        """
        if f_type == "image":
            return (self.split + "/" if self.split else "") + "images/"
        else:
            # Labels go in root or dedicated folder
            return (self.split + "/" if self.split else "") + ""

    def get_filename_for(self, shot_id: int, f_type: file_type | Literal["image"]) -> str:
        """
        Images get individual filenames; annotations are in a single file.
        """
        if f_type == "image":
            return f"{self.write_cfg.prefix}_{shot_id}"
        else:
            # Single annotation file for all images
            return "instances"

    def transform_annotation(
        self,
        label: Label,
        shot_idx: int,
        shot_config: RenderConfig
    ) -> dict[str, Any]:
        """
        Transform a single annotation to COCO format.
        Does NOT create the annotation entry yet - that happens in aggregate_batch.
        """
        if not label.annotation_type == "bbox":
            raise RuntimeError("COCO bbox formatter only supports bbox annotations!")

        bbox = label.bbox
        coco_bbox = convert_camera_centered_to_coco(bbox, shot_config.width, shot_config.height)

        if shot_idx not in self.marked_img_ids:
            self.coco_data["images"].append({
                "id": shot_idx,
                "file_name": f"{self.get_filename_for(shot_idx, 'image')}.{self.write_cfg.image_extension.lower()}",
                "height": shot_config.height,  # Should be provided by RenderConfig
                "width": shot_config.width,  # Should be provided by RenderConfig
            })
            self.marked_img_ids.add(shot_idx)

        return {
            'bbox': coco_bbox,  # [x, y, width, height]
            'class_id': label.cls.class_id,
            'class_name': label.cls.name,
            'image_id': shot_idx,
            'width': shot_config.width,
            'height': shot_config.height
        }

    def aggregate_batch(
        self,
        annotations: list[dict[str, Any]],
        batch_metadata: BatchMetadata
    ) -> dict[str, list[dict]]:
        """
        Aggregate all annotations for a batch.
        Groups by image_id and builds COCO structure.
        """
        # Build categories from batch metadata
        categories = []
        for class_obj in batch_metadata.classes:
            categories.append({
                "id": class_obj.class_id,
                "name": class_obj.name,
                "supercategory": "object"
            })

        # Group annotations by image
        annotations_by_image = {}
        for ann in annotations:
            img_id = ann['image_id']
            if img_id not in annotations_by_image:
                annotations_by_image[img_id] = []
            annotations_by_image[img_id].append(ann)

        # Build COCO annotations with proper structure
        coco_annotations = []
        for img_id, img_annotations in annotations_by_image.items():
            for ann in img_annotations:
                coco_ann = {
                    "id": self.annotation_id_counter,
                    "image_id": img_id,
                    "category_id": ann['class_id'],
                    "bbox": ann['bbox'],
                    "area": ann['bbox'][2] * ann['bbox'][3],  # width * height
                    "iscrowd": 0,
                }
                coco_annotations.append(coco_ann)
                self.annotation_id_counter += 1

        return {
            "categories": categories,
            "annotations": coco_annotations,
            "num_images": batch_metadata.num_images
        }

    def serialize_image_labels(
            self,
            transformed: list[dict]
    ) -> Collection[tuple[file_type, extension, str]]:
        """
        Not used for COCO (global format).
        Per-image serialization doesn't apply here.
        """
        raise NotImplementedError(
            "COCO uses global aggregation via finalize(), not per-image serialization"
        )

    def finalize(self, aggregated: dict[str, Any]) -> Collection[tuple[file_type, extension, str]]:
        """
        Final pass: build complete COCO JSON structure.
        Receives aggregated data from aggregate_batch + image info.
        """
        # Add categories
        self.coco_data["categories"] = aggregated['categories']
        self.coco_data["annotations"] = aggregated['annotations']

        # Serialize to JSON
        coco_json = json.dumps(self.coco_data, indent=2)

        return (("instances", ".json", coco_json),)

@LabelingFormatRegistry.register_strategy(SupportedFormats.COCO_SEGMENTATION.value)
class COCOSegmentation(IOStrategy):
    pass

@LabelingFormatRegistry.register_strategy(SupportedFormats.COCO_KEYPOINTS.value)
class COCOLandmarks(IOStrategy):
    pass