from .generator import LabelData

import json

from abc import ABCMeta, abstractmethod
from typing import Dict


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
