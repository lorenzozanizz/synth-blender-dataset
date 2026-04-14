
from ..utils.timer import TimingContext
from .raytracing import get_visible_objects_from_camera

from abc import ABCMeta, abstractmethod

from typing import Iterable, Any, Dict, Callable
import json


class LabelManager:

    def __init__(self, folder, fmt: str):
        self.format = fmt
        self.folder = folder

    def create_label_directory(self) -> None:
        pass

class LabelGenerator:
    """Main orchestrator for label generation"""

    def __init__(self, format_type: str = "yolo"):
        self.format_type = format_type
        self.formatter = LabelGenerator._get_formatter(format_type)

    def generate_labels(self, visible_objects, class_engine, bbox_extractor,
                        camera, context, render, output_dir):
        """

        :param visible_objects:
        :param class_engine:
        :param bbox_extractor:
        :param camera:
        :param context:
        :param render:
        :param output_dir:
        :return:
        """
        annotations = []

        for obj in visible_objects:
            # Get class
            class_id, class_name = class_engine.resolve(obj)
            # bbox_data = bbox_extractor.extract(obj, camera, context, render)

            # Build annotation entry
            annotation = {
                "object": obj.name,
                "class_id": class_id,
                "class_name": class_name,
                # "bbox": bbox_data["bbox"],
                # "visibility": bbox_data["visibility"]
            }
            annotations.append(annotation)

        # Format and save
        self.formatter.save(annotations, output_dir)
        return annotations

    @staticmethod
    def _get_formatter(type):
        if type == "YOLO":
            return YoloFormatter()
        return None


class BoundingBoxExtractor:
    """Encapsulates bbox extraction logic"""

    def __init__(self, context):
        self.ctx = context

        self.timings: Dict[str, float] = dict()

        self.visible_objects = dict()


    def extract(self, camera, ray_casting_ratio: float = 0.5):
        """

        :return:
        """
        res_x = int(self.ctx.scene.render.resolution_x * ray_casting_ratio)
        res_y = int(self.ctx.scene.render.resolution_y * ray_casting_ratio)

        with TimingContext(self.timings, 'labeling'):
            self.visible_objects = get_visible_objects_from_camera(
                self.ctx.scene, self.ctx.evaluated_depsgraph_get(), camera,
                resolution_x=res_x, resolution_y=res_y, compute_bounding_boxes=True)

    def get_labeling_time(self) -> float:
        """ Get the time it took to compute the boxes and the visible objects """
        return self.timings['labeling']

    def get_visible_objects(self) -> Iterable[Any]:
        """ Get the visible objects """
        return self.visible_objects.keys()

    def get_bounding_boxes(self, conv_func: Callable = None) -> Iterable[Any]:
        """ Get the camera centered bounding boxes """
        if not conv_func:
            return self.visible_objects.values()
        else:
            return (conv_func(bbox) for bbox in self.visible_objects.values())

    def get_bbox_mappings(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        return self.visible_objects


class Formatter(metaclass=ABCMeta):
    """

    """

    @abstractmethod
    def save(self, annotations, output_dir):
        """

        :param annotations:
        :param output_dir:
        :return:
        """
        pass


class YoloFormatter(Formatter):
    """YOLO-specific output format"""

    def save(self, annotations, output_dir):
        for annotation in annotations:
            label_file = f"{output_dir}/{annotation['object']}.txt"
            line = f"{annotation['class_id']} " \
                   f"{annotation['bbox'][0]} {annotation['bbox'][1]} " \
                   f"{annotation['bbox'][2]} {annotation['bbox'][3]}\n"
            with open(label_file, 'a') as f:
                f.write(line)


class CocoFormatter(Formatter):
    """COCO JSON format"""

    def save(self, annotations, output_dir):
        coco_data = {
            "images": [...],
            "annotations": [...],
            "categories": [...]
        }
        json.dump(coco_data, open(f"{output_dir}/annotations.json", 'w'))


class PascalVocFormatter(Formatter):
    """Pascal VOC XML format"""

    def save(self, annotations, output_dir):
        # Generate XML per image
        pass