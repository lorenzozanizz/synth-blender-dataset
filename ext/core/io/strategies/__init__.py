"""


"""
from enum import Enum

class SupportedFormats(Enum):
    """

    """

    ULTRALYTICS_YOLO = "Ultralytics YOLO"
    COCO = "COCO"
    COCO_SEGMENTATION = "COCO Segmentation"
    COCO_KEYPOINTS = "COCO Keypoints"
    PASCAL_VOC = "Pascal VOC"
    CVAT_XML_IMAGES = "CVAT XML Images"


from .coco_strategy import *
from .yolo_strategy import *
from .pascal_strategy import *
from .cvat_xml_strategy import *
