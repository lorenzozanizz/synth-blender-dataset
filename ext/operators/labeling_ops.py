from .names import Labels

from bpy.types import Operator

class AddLabelClassOperator(Operator):
    bl_idname = Labels.ADD_LABEL_CLASS.value
    bl_label = "Add a new class of labels"


class RemoveLabelClassOperator(Operator):
    bl_idname = Labels.REMOVE_LABEL_CLASS.value
    bl_label = "Remove a label class"


class AddObjectLabelOperator(Operator):
    bl_idname = Labels.ADD_OBJECT_LABEL.value
    bl_label = "Add a new label to an object"


class RemoveObjectLabelOperator(Operator):
    bl_idname = Labels.REMOVE_OBJECT_LABEL.value
    bl_label = "Remove a label from an objecte"


class AddLabelRuleOperator(Operator):
    bl_idname = Labels.ADD_LABEL_RULE.value
    bl_label = "Add a new label rule"


class RemoveLabelRuleOperator(Operator):
    bl_idname = Labels.REMOVE_LABEL_RULE.value
    bl_label = "Remove a label rule"
