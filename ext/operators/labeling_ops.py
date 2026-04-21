from .names import Labels

from random import random
from bpy.types import Operator
from bpy.props import IntProperty, EnumProperty

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

    def execute(self, context):
        data = context.scene.labeling_data
        classes = data.label_classes
        index = data.class_active_index

        # Check if there are operations
        if not classes:
            self.report({'WARNING'}, 'No class to remove')
            return {'CANCELLED'}

        # Remove the operation at the active index
        classes.remove(index)

        # Adjust active index if needed (if we removed the last item)
        if data.class_active_index >= len(classes):
            data.class_active_index = max(0, len(classes) - 1)

        return { 'FINISHED' }

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

    def execute(self, context):
        data = context.scene.labeling_data
        labels = data.direct_labels
        index = data.direct_active_index

        # Check if there are operations
        if not labels:
            self.report({'WARNING'}, 'No label to remove')
            return {'CANCELLED'}

        # Remove the operation at the active index
        labels.remove(index)

        # Adjust active index if needed (if we removed the last item)
        if data.direct_active_index >= len(labels):
            data.direct_active_index = max(0, len(labels) - 1)

        return {'FINISHED'}

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

    def execute(self, context):
        data = context.scene.labeling_data
        rules = data.label_rules
        index = data.rule_active_index

        # Check if there are operations
        if not rules:
            self.report({'WARNING'}, 'No rule to remove')
            return {'CANCELLED'}

        # Remove the operation at the active index
        rules.remove(index)

        # Adjust active index if needed (if we removed the last item)
        if data.rule_active_index >= len(rules):
            data.rule_active_index = max(0, len(rules) - 1)

        return {'FINISHED'}

class AddEntityOperator(Operator):
    bl_idname = Labels.ADD_ENTITY.value
    bl_label = "Add a new entity definition"

    def execute(self, context):
        entities = context.scene.labeling_data.entities
        new_val = entities.add()
        max_prev_id = max( entity.entity_id for entity in entities )
        max_prev_id = max_prev_id if max_prev_id else 0
        new_val.entity_id = max_prev_id + 1

        new_val.obj_or_entity_name = f"Unnamed Entity {new_val.entity_id}"
        return { 'FINISHED' }

class SelectEntityOperator(Operator):

    bl_idname = Labels.SELECT_ENTITY_LABEL.value
    bl_label = "Select the entity for the class"

    target_rule_obj_id: IntProperty()                       # type: ignore

    defined_entities: EnumProperty(                         # type: ignore
        name="Entities",
        description="Select an entity to add",
        items= lambda self, ctx: [                          # type: ignore
            (entity.entity_name, entity.entity_name, "")
            for entity in ctx.scene.labeling_data.entities
        ] or [("None", "No Entity defined", "")]
    )

    def draw(self, _context):
        layout = self.layout
        layout.prop(self, "defined_entities")
        # target_rule_obj_id is not drawn

    def execute(self, context):
        scene = context.scene

        entity = self.defined_entities
        if not entity or entity.lower == "none":
            return {'CANCELLED'}

        labels = scene.labeling_data.direct_labels
        target_lab = next( (lab for lab in labels if lab.assignment_id == self.target_rule_obj_id), None )
        if not target_lab:
            return { 'CANCELLED' }
        target_lab.is_entity = True
        names = target_lab.obj_names
        names.clear()

        entity_entry = names.add()
        entity_entry.obj_name = entity
        return {'FINISHED'}

    def invoke(self, context, _event):
        return context.window_manager.invoke_props_dialog(self)


class RemoveEntityOperator(Operator):
    bl_idname = Labels.REMOVE_ENTITY.value
    bl_label = "Remove an entity"

    def execute(self, context):
        data = context.scene.labeling_data
        entities = data.entities
        index = data.entities_active_index

        # Check if there are operations
        if not entities:
            self.report({'WARNING'}, 'No entity to remove')
            return {'CANCELLED'}

        # Remove the operation at the active index
        entities.remove(index)

        # Adjust active index if needed (if we removed the last item)
        if data.entities_active_index >= len(entities):
            data.entities_active_index = max(0, len(entities) - 1)

        return {'FINISHED'}

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

        target_lab.is_entity = False
        # Store names
        name_list = target_lab.obj_names
        name_list.clear()
        for obj in selected:
            nm = name_list.add()
            nm.obj_name = obj.name

        return { 'FINISHED' }


class TargetObjectsEntityOperator(Operator):
    bl_idname = Labels.CAPTURE_OBJECTS_ENTITY.value
    bl_label = "Capture selected objects for this label"

    target_entity_id: IntProperty(default=0)  # type: ignore


    def execute(self, context):
        labels = context.scene.labeling_data.entities
        target_ent = next( (lab for lab in labels if lab.entity_id == self.target_entity_id), None )

        if not target_ent:
            return { 'CANCELLED'}
        selected = context.selected_objects

        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        # Store names
        name_list = target_ent.obj_names
        name_list.clear()
        for obj in selected:
            nm = name_list.add()
            nm.obj_name = obj.name

        return { 'FINISHED' }