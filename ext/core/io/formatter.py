from abc import ABCMeta, abstractmethod
from collections.abc import Collection
from enum import Enum

from ...labeling.generator.data_structure import *
from ..configurations import WritingConfig, RenderConfig


class FolderStructure(Enum):
    """

    """
    YOLO = "yolo"
    YOLO_SPLIT = "yolo_split"       # images/train, labels/train, etc.
    COCO_FLAT = "coco_flat"         # single dir with annotations.json
    KITTI_3D = "kitti_3d"           # image_2/, label_2/, calib/


class SerializationStrategy(metaclass=ABCMeta):
    """ Abstract base for output formats """

    def __init__(self, write_config: WritingConfig):
        self.config = write_config

    @abstractmethod
    def format(self, label_data: LabelData, render_config: RenderConfig) -> Collection[tuple[str, str]]:
        """

        :param render_config:
        :param label_data:
        :return:
        """
        pass

    @abstractmethod
    def get_subdir(self, ext: str) -> str:
        """

        :param ext:
        :return:
        """
        pass

    @abstractmethod
    def mark_beginning(self) -> None:
        """

        :return:
        """
        pass

    @abstractmethod
    def mark_end(self) -> None:
        """

        :return:
        """
        pass

    @abstractmethod
    def declare_classes(self) -> None:
        """ For the COCO """
        pass
