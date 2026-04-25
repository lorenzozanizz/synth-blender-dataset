from dataclasses import dataclass
from typing import Optional, Literal, Union, Dict

from ..bpy_properties import LabelClass


@dataclass
class Label:
    """ Single entity annotation """

    obj_or_entity_name: str
    cls: Optional[LabelClass]

    # The annotation data — could be any shape
    geometry: Union[
        tuple,  # bbox: (x, y, w, h)
        list[tuple],  # polygon: [(x1,y1), (x2,y2), ...]
        dict  # flexible structure
    ]

    annotation_type: Literal["bbox", "polygon"]  # "bbox", "polygon", "depth"

    # Whether a label belongs to a single object or to a composite multi-mesh entity
    is_entity: bool
    visibility: float = 0.0


class LabelData:
    """Container for all annotations in a frame"""

    def __init__(self):
        self.data: Dict[str, Label] = dict()

    def __iter__(self):
        """ """
        return iter(self.data.values())

    def items(self):
        return self.data.items()

    def __getitem__(self, item: str):
        """ """
        return self.data.get(item)

    def add(self, new_lab: Label):
        """ """
        self.data[new_lab.obj_or_entity_name] = new_lab
