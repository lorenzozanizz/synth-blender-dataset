from ..constants import *
from ..operators.names import Labels
from bpy.types import UIList, PropertyGroup, Panel

class LabelClassesUIList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        sub = row.column(align=True)
        sub.scale_x = 0.3
        sub.prop(item, 'color', text='')
        row.separator()
        row.prop(item, 'name', text='', emboss=False)
        row.separator()
        row.prop(item, 'class_id', emboss=False, text="")



class ObjectLabelsUIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        scene = context.scene

        # The class has to be an enum depending on the classes currentlyr egistered.
        # Now show a small band with the class color for visual aid.
        # Find the corresponding class, put its color for clarity.
        row = layout.row(align=True)
        cls = next((cls for cls in scene.labeling_data.label_classes
                    if str(cls.class_id).lower() == item.class_id.lower()), None)
        if cls:
            sub = row.column(align=True)
            sub.scale_x = 0.3
            sub.prop(cls, 'color', text='')
            row.separator()

        text_label = str([n_prop.obj_name for n_prop in item.obj_names]) \
             if len(item.obj_names) != 0 else "None"

        row.label(text=text_label, icon='OBJECT_DATA')
        row.operator(Labels.CAPTURE_OBJECTS_LABEL.value, icon="EYEDROPPER", text="").target_rule_obj_id = (
            item.assignment_id)

        row.separator()
        row.prop(item, 'class_id', emboss=False, text="")
        if cls:
            sub = row.column(align=True)
            sub.scale_x = 0.4
            sub.label(text=f"({cls.class_id})")


class LabelRulesUIList(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.rule_type)
        row.label(text=f"{item.class_name}")


class LabelingPanel(Panel):

    bl_label = "Labeling"
    bl_idname = panel_conflict_rename("labeling")
    bl_category = PANEL_CATEGORY
    bl_space_type = 'VIEW_3D'
    bl_options = { 'DEFAULT_CLOSED' }
    bl_region_type = 'UI'

    def draw(self, context):

        layout = self.layout
        scene = context.scene

        labeling_data = scene.labeling_data

        box = layout.box()
        box.label(text="Classes", icon='GROUP')
        row = box.row()
        row.template_list(
            LabelClassesUIList.__name__,
            'labeling_classes_list',
            labeling_data, 'label_classes',
            labeling_data, 'class_active_index'
        )
        col = row.column()
        col.operator(Labels.ADD_LABEL_CLASS.value, icon='ADD', text='')
        col.operator(Labels.REMOVE_LABEL_CLASS.value, icon='REMOVE', text='')

        row = layout.row(align=True)
        row.label(text="Default Class")
        row.prop(labeling_data, 'default_class', text="")

        # Draw the color associated with the default class.
        cls = next((cls for cls in scene.labeling_data.label_classes
                    if str(cls.class_id).lower() == labeling_data.default_class.lower()), None)
        if cls:
            sub = row.column(align=True)
            sub.scale_x = 0.4
            sub.prop(cls, 'color', text='')
            row.separator()


        box = layout.box()
        box.label(text="Object Labels", icon='OBJECT_DATA')
        row = box.row()
        row.template_list(
            ObjectLabelsUIList.__name__,
            'object_labels_list',
            labeling_data, 'direct_labels',
            labeling_data, 'direct_active_index'
        )
        col = row.column()
        col.operator(Labels.ADD_OBJECT_LABEL.value, icon='ADD', text='')
        col.operator(Labels.REMOVE_OBJECT_LABEL.value, icon='REMOVE', text='')

        layout.prop(labeling_data, 'use_rules', text="Use Assignment Rules")
        if labeling_data.use_rules:
            box = layout.box()
            box.label(text="Labeling Rules", icon='SOLO_ON')
            row = box.row()
            row.template_list(
                LabelRulesUIList.__name__,
                'label_rules_list',
                labeling_data, 'label_rules',
                labeling_data, 'rule_active_index'
            )
            col = row.column()
            col.operator(Labels.ADD_LABEL_RULE.value, icon='ADD', text='')
            col.operator(Labels.REMOVE_LABEL_RULE.value, icon='REMOVE', text='')

        # Show rule editor if selected

        if labeling_data.label_rules:
            rule = labeling_data.label_rules[labeling_data.rule_active_index]
            box = layout.box()
            box.prop(rule, 'rule_type', text='Type')

            if rule.rule_type == 'MATERIAL':
                box.prop(rule, 'material_name', text='Material')
            elif rule.rule_type == 'NAME_CONTAINS':
                box.prop(rule, 'name_filter', text='Contains')
            elif rule.rule_type == 'COLLECTION':
                box.prop(rule, 'collection_name', text='Collection')

            box.prop(rule, 'class_id', text='Assign to Class')
