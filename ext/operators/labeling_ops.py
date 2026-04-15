from .names import Labels

from random import random
from bpy.types import Operator
from bpy.props import IntProperty

class AddLabelClassOperator(Operator):
    bl_idname = Labels.ADD_LABEL_CLASS.value
    bl_label = "Add a new class of labels"

    def execute(self, context):
        classes = context.scene.labeling_data.label_classes
        cls = classes.add()
        r, g, b = [random()for i in range(3)]
        cls.color = (r, g, b, 1)
        max_prev_id = max( cl.class_id for cl in classes )
        max_prev_id = max_prev_id if max_prev_id else 0
        cls.class_id = max_prev_id + 1
        cls.name = f"Unnamed {cls.class_id}"
        return { 'FINISHED' }

class RemoveLabelClassOperator(Operator):
    bl_idname = Labels.REMOVE_LABEL_CLASS.value
    bl_label = "Remove a label class"


class AddObjectLabelOperator(Operator):
    bl_idname = Labels.ADD_OBJECT_LABEL.value
    bl_label = "Add a new label to an object"

    def execute(self, context):
        labels = context.scene.labeling_data.direct_labels
        new_lab = labels.add()
        # We assign a new unique id to this assignment. Note that the ids need not
        # be contiguous (some assignments may later be deleted). The only requirement
        # is uniqueness.
        max_prev_id = max( assignment.assignment_id for assignment in labels )
        max_prev_id = max_prev_id if max_prev_id else 1
        new_lab.assignment_id = max_prev_id + 1
        return { 'FINISHED' }

class RemoveObjectLabelOperator(Operator):
    bl_idname = Labels.REMOVE_OBJECT_LABEL.value
    bl_label = "Remove a label from an objecte"


class AddLabelRuleOperator(Operator):
    bl_idname = Labels.ADD_LABEL_RULE.value
    bl_label = "Add a new label rule"

    def execute(self, context):
        rules = context.scene.labeling_data.label_rules
        new_val = rules.add()
        return { 'FINISHED' }

class RemoveLabelRuleOperator(Operator):
    bl_idname = Labels.REMOVE_LABEL_RULE.value
    bl_label = "Remove a label rule"


class AddEntityOperator(Operator):
    bl_idname = Labels.ADD_ENTITY.value
    bl_label = "Add a new entity definition"

    def execute(self, context):
        rules = context.scene.labeling_data.entities
        new_val = rules.add()
        return { 'FINISHED' }


class RemoveEntityOperator(Operator):
    bl_idname = Labels.REMOVE_ENTITY.value
    bl_label = "Remove an entity"


class TargetObjectsLabelOperator(Operator):
    bl_idname = Labels.CAPTURE_OBJECTS_LABEL.value
    bl_label = "Capture selected objects for this label"

    target_rule_obj_id: IntProperty(default=0)  # type: ignore

    def execute(self, context):
        labels = context.scene.labeling_data.direct_labels
        target_lab = next( lab for lab in labels if lab.assignment_id == self.target_rule_obj_id )

        selected = context.selected_objects

        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        # Store names
        name_list = target_lab.obj_names
        name_list.clear()
        for obj in selected:
            nm = name_list.add()
            nm.obj_name = obj.name

        return { 'FINISHED' }