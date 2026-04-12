
class LabelingEngine:
    """

    """

    def __init__(self, scene):

        self.scene = scene
        self.labels = {}  # obj_name -> class_id

    def apply_labels(self, objects):
        """Apply manual labels + rule-based labels"""

        # First: apply manual labels
        for label_item in self.scene.object_labels:
            self.labels[label_item.obj_name] = label_item.class_id

        # Second: apply rules
        for rule in self.scene.label_rules:
            matching_objects = self._get_matching_objects(rule, objects)
            for obj in matching_objects:
                if obj.name not in self.labels:  # Don't override manual
                    self.labels[obj.name] = rule.class_id

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

    def get_label(self, obj_name: str) -> int:
        return self.labels.get(obj_name, 0)  # Default to 0 if unlabeled