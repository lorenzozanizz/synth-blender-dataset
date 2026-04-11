from enum import Enum
from typing import Union

from bpy.types import PropertyGroup
from bpy.props import EnumProperty, StringProperty, IntProperty, FloatVectorProperty, CollectionProperty, PointerProperty

class LabelingFormats(Enum):

    YOLO = "Yolo"

    @staticmethod
    def from_string(s: str) -> Union[None, 'LabelingFormats']:
        if s == "YOLO":
            return LabelingFormats.YOLO
        return None


class LabelClass(PropertyGroup):
    """ """
    name: StringProperty(default="Class")  # type: ignore
    class_id: IntProperty(default=0)  # type: ignore
    color: FloatVectorProperty(subtype='COLOR')  # type: ignore

class ObjectLabel(PropertyGroup):
    """ """

    obj_name: StringProperty()  # type: ignore
    class_id: IntProperty()  # type: ignore


class LabelRule(PropertyGroup):

    rule_type: EnumProperty(  # type: ignore
        items=[
            ('MATERIAL', 'Material', ''),
            ('NAME_CONTAINS', 'Name Contains', ''),
            ('COLLECTION', 'Collection', ''),
        ]
    )

    # Rule parameters
    material_name: StringProperty()  # type: ignore
    name_filter: StringProperty()  # type: ignore
    collection_name: StringProperty()  # type: ignore

    class_id: IntProperty()  # type: ignore

class LabelingData(PropertyGroup):

    label_classes: CollectionProperty(type=LabelClass) # type: ignore
    class_active_index: IntProperty(default=0)          # type: ignore

    direct_labels: CollectionProperty(type=ObjectLabel) # type: ignore
    direct_active_index: IntProperty(default=0)         # type: ignore

    label_rules: CollectionProperty(type=LabelRule)     # type: ignore
    rule_active_index: IntProperty(default=0)           # type: ignore


label_properties = {
    "labeling_data": PointerProperty(
        type=LabelingData
    )
}
