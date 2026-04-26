
from collections.abc import Collection

from ...labeling.conversions import convert_camera_centered_to_yolo
from ...labeling.generator.data_structure import *
from ..configurations import WritingConfig, RenderConfig
from .formatter import SerializationStrategy


class YoloFormatter(SerializationStrategy):
    """

    """

    def declare_classes(self) -> None:
        """ For the YOLO strategy this step is unnecessary, the class ids are specified
        per label when each file is getting generated and there is no unique "class description" """
        return

    def mark_beginning(self) -> None:
        """ Yolo formatter has no need for a beginning of generation hooko"""
        return

    def mark_end(self) -> None:
        """ Yolo formatter has no need for an end of generation hooko"""
        return

    def __init__(self, write_config: WritingConfig):
        super().__init__(write_config)

    def format(self, label_data: LabelData, render_config: RenderConfig) -> Collection[tuple[str, str]]:
        """

        :param label_data:
        :param render_config:
        :return:
        """
        # The label data is initially in the centered camera format. We need to transform it into
        # the correct yolo format.
        lines = []
        for label in label_data:
            cls_id = label.cls.class_id
            bbox = label.geometry

            yolo_coos = convert_camera_centered_to_yolo(bbox)
            lines.append(f"{cls_id} {yolo_coos[0]:.2f} {yolo_coos[1]:.2f} {yolo_coos[2]:.2f} {yolo_coos[3]:.2f}\n")
        return ('.txt', "".join(lines)),

    def get_subdir(self, ext: str) -> str:
        """

        :param ext:
        :return:
        """
        if 'txt' in ext:
            return 'labels'
        elif 'image' in ext:
            return 'images'
        return ""

class YoloSplitFormatter(SerializationStrategy):

    def declare_classes(self) -> None:
        pass

    def format(self, label_data: LabelData, render_config: RenderConfig) -> Collection[tuple[str, str]]:
        pass

    def get_subdir(self, ext: str) -> str:
        pass

    def mark_beginning(self) -> None:
        pass

    def mark_end(self) -> None:
        pass
