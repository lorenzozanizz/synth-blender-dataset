from typing import Union, Any, Iterable, Dict, List
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
        self.entity_mappings: Dict[str, LabelClass] = { }

    def extract_entity_data(self) -> Dict[str, List[str]]:
        """

        :return:
        """
        entity_data = self.ctx.scene.labeling_data.entities

        ret_data = dict()
        for ent_declaration in entity_data:
            name = ent_declaration.entity_name
            components = [ comp.obj_name for comp in ent_declaration.obj_names ]
            ret_data[name] = components
        return ret_data

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
                continue

            names = label.obj_names
            label_cls = label.class_id
            target_class: Union[None, LabelClass] = next((cls for cls in classes if str(cls.class_id) == str(label_cls)), None)
            if target_class is None:
                # There is a dangling reference. ignore (and report, maybe?)
                continue
            if label.is_entity:
                self.entity_mappings.update( { name.obj_name: target_class for name in names } )
            else:
                self.labels_mappings.update( { name.obj_name: target_class for name in names } )

        # then evaluate rules.
        do_use_rules = label_data.use_rules
        if not do_use_rules:
            return

        name_map = {obj.name: obj for obj in target_blender_objects}
        missing_names = set(name_map.keys()).difference(self.labels_mappings.keys())
        mapping_rules = label_data.label_rules

        for mapping_rule in mapping_rules:
            relevant_data = self._sanitize_rule_mapping(mapping_rule)
            if not relevant_data:
                continue
            # Attempt to map the object using each mapping rule. Do this instead of evaluating every rule,
            # (assuming there are only a few objects to be mapped)
            if len(missing_names) == 0:
               return
            # We are missing some names, lets try to see if the current rule absolves one of the missing names
            rule_type = mapping_rule.rule_type
            mapping_class = next((cls for cls in label_data.label_classes
                        if str(cls.class_id).lower() == mapping_rule.class_id.lower()), None)
            resolved = []

            if rule_type.lower() == "material":

                material = relevant_data
                for missing_name in missing_names:
                    obj = name_map.get(missing_name)
                    if obj and obj.data and hasattr(obj.data, 'materials'):
                        if material.name in obj.data.materials:
                            resolved.append(missing_name)

            elif rule_type.lower() == "name_contains":
                partial_match = mapping_rule.name_filter
                resolved = [name for name in missing_names
                            if partial_match.lower() in name.lower()]

            elif rule_type.lower() == "collection":
                collection = relevant_data

                collection_obj_names = set(obj.name for obj in collection.objects)
                resolved = missing_names & collection_obj_names

            for name in resolved:
                self.labels_mappings[name] = mapping_class
                missing_names.discard(name)

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
    def _sanitize_rule_mapping(mapping: LabelRule) -> Union[None, Any]:

        relevant_data = True
        # Initially check that a mapping class is correclty provided.
        if not mapping.class_id:
            return None
        # For a "material" rule, we check if the material exists
        if mapping.rule_type.upper() == "MATERIAL":
            mat = mapping.material_name
            if not mat.strip():
                return None
            relevant_data = bpy.data.materials.get(mat)
            if relevant_data is None:
                return None

        # For a "Name contains" rule, we check if the partial match is not empty
        elif mapping.rule_type.upper() == "NAME_CONTAINS":
            name = mapping.name_filter
            if not name.strip():
                return None

        # For a "collection" rule, we check if the collection exists.
        elif mapping.rule_type.upper() == "COLLECTION":
            collection = mapping.collection_name
            if not collection.strip():
                return None
            relevant_data = bpy.data.collections.get(collection)
            if relevant_data is None:
                return None
        else: return None
        return relevant_data

    def map_obj(self, obj: Union[str, Any]) -> Union[None, LabelClass]:
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

    def map_entity(self, entity_name: str) -> Union[None, LabelClass]:
        return self.entity_mappings.get(entity_name)

    def get_mapping(self) -> Dict[str, LabelClass]:
        return self.labels_mappings


