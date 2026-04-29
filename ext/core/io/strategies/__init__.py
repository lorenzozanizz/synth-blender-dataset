"""


"""
from enum import Enum

class SupportedFormats(Enum):
    """

    """

    YOLO = "YOLO"
    COCO = "COCO"
    COCO_SEGMENTATION = "COCO Segmentation"
    COCO_LANDMARKS = "COCO Landmarks"
    PASCAL_VOC = "Pascal VOC"


from .coco_strategy import *
from .yolo_strategy import *
from .pascal_strategy import *
