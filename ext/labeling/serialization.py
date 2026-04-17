from abc import ABCMeta, abstractmethod
from typing import Literal, Union, Dict
import json
from enum import Enum
import os
from dataclasses import dataclass

from ext.labeling import LabelingFormats

class LabelingConfig:
    pass


class FolderStructure(Enum):
    """

    """

    YOLO_SPLIT = "yolo_split"       # images/train, labels/train, etc.
    COCO_FLAT = "coco_flat"         # single dir with annotations.json
    KITTI_3D = "kitti_3d"           # image_2/, label_2/, calib/


@dataclass
class LabelData:


    pass


class Formatter(metaclass=ABCMeta):
    """ Abstract base for output formats """

    @abstractmethod
    def format(self, label_data: LabelData) -> Dict[str, str]:
        """
        Args:
            label_data: Extracted annotations
        Returns:
            {filename: file_content} dict
        """
        pass

class YoloFormatter(Formatter):
    def format(self, label_data: LabelData) -> Dict[str, str]:
        result = {}
        for image_name, annotations in label_data.items():
            lines = [f"{ann.class_id} {ann.bbox[0]} ..." for ann in annotations]
            result[f"{image_name}.txt"] = "\n".join(lines)
        return result

class CocoFormatter(Formatter):
    def format(self, label_data: LabelData) -> Dict[str, str]:
        coco_data = {"images": [...], "annotations": [...]}
        return {"annotations.json": json.dumps(coco_data)}

class LabelWriter:

    def __init__(self, config: LabelingConfig):
        self.config = config

    def write(self, formatter: Formatter, label_data: LabelData) -> None:
        files = formatter.format(label_data)

        for filename, content in files.items():
            # Determine output path based on folder structure
            path = self._resolve_path(filename)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)

    def _resolve_path(self, filename: str) -> str:
        """Map filename to actual path based on folder structure"""
        if self.config.folder_structure == FolderStructure.YOLO_SPLIT:
            if filename.endswith('.txt'):
                subdir = f"labels/{self.config.split}"
            else:
                subdir = f"images/{self.config.split}"
        elif self.config.folder_structure == FolderStructure.COCO_FLAT:
            subdir = ""
        elif self.config.folder_structure == FolderStructure.KITTI_3D:
            if "calib" in filename:
                subdir = "calib"
            elif "label" in filename:
                subdir = "label_2"
            else:
                subdir = "image_2"

        return os.path.join(self.config.output_dir, subdir, filename)

