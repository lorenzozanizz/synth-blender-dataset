from typing import Union, Any, Iterable, Dict
from  .bpy_properties import LabelClass, ObjectLabel, LabelRule

import bpy

from ..utils.logger import UniqueLogger


class LabelingEngine:
    """

    """

    def __init__(self, context):
        """

        :param scene:
        """
        self.ctx = context
        self.labels_mappings: Dict[str, LabelClass] = { }  # obj_name -> class_id


    def create_rule_mappings(self, target_blender_objects: Iterable[Any]) -> None:
        """

        :param target_blender_objects:
        :return:
        """

        # Populate the label mappings using the scene rules on the target objects.
        # First evaluate direct mappings, which have the highest priority
        label_data = self.ctx.scene.labeling_data
        labels = label_data.direct_labels
        classes = label_data.label_classes
        for label in labels:
            # Note: up to date there are no checks on actual uniqueness of the assignments.
            # the last assignment wins.
            if not self._sanitize_direct_mapping(label):
                UniqueLogger.quick_log("Skipping " + label.name)
                continue
            UniqueLogger.quick_log("sANITIZED " + label.name)

            names = label.obj_names
            label_cls = label.class_id
            target_class: Union[None, LabelClass] = next((cls for cls in classes if str(cls.class_id) == str(label_cls)), None)
            if target_class is None:
                # There is a dangling reference. ignore (and report, maybe?)
                UniqueLogger.quick_log("Dangling " + label.name)

                continue

            self.labels_mappings.update( { name.obj_name: target_class for name in names } )
        # then evaluate rules.

        do_use_rules = label_data.use_rules
        if not do_use_rules:
            return
        missing_names = set({obj.name for obj in target_blender_objects}).difference(self.labels_mappings.keys())
        mapping_rules = label_data.label_rules
        for mapping_rule in mapping_rules:
            if not self._sanitize_rule_mapping(mapping_rule):
                continue
            # Attempt to map the object using each mapping rule. Do this instead of evaluating every rule,
            # (assuming there are only a few objects to be mapped)
            if len(missing_names) == 0:
               return
            # We are missing some names, lets try to see if the current rule absolves one of the missing names

        return


    @staticmethod
    def _sanitize_direct_mapping(mapping: ObjectLabel) -> bool:
        names = mapping.obj_names
        if not names or names is None:
            return False
        if not mapping.class_id:
            return False
        return True

    @staticmethod
    def _sanitize_rule_mapping(mapping: LabelRule) -> bool:
        return True

    def get(self, obj: Union[str, Any]) -> Union[None, LabelClass]:
        """

        :param obj:
        :return:
        """
        if isinstance(obj, str):
            name = obj
        else: name = obj.name
        if name in self.labels_mappings:
            return self.labels_mappings[name]
        return None

    def get_mapping(self) -> Dict[str, LabelClass]:
        return self.labels_mappings

    def _get_matching_objects(self, rule, objects):
        if rule.rule_type == 'MATERIAL':
            return [o for o in objects
                    if any(s.material and s.material.name == rule.material_name
                           for s in o.material_slots)]

        elif rule.rule_type == 'NAME_CONTAINS':
            return [o for o in objects if rule.name_filter in o.name]

        elif rule.rule_type == 'COLLECTION':
            coll = bpy.data.collections.get(rule.collection_name)
            if not coll:
                return []
            return [o for o in coll.objects]

        return []

