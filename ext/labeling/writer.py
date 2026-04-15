from abc import ABCMeta, abstractmethod
import json

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