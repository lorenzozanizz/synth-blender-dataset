from enum import Enum
from typing import Union

class LabelingFormats(Enum):

    YOLO = "Yolo"

    @staticmethod
    def from_string(s: str) -> Union[None, 'LabelingFormats']:
        if s == "YOLO":
            return LabelingFormats.YOLO
        return None