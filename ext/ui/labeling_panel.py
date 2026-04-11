from ..constants import *

from bpy.types import UIList, PropertyGroup, Panel


class RANDOMIZER_UL_classes(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.prop(item, 'color', text='')
        row.prop(item, 'name', text='', emboss=False)

class RANDOMIZER_UL_object_labels(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.obj_name)
        row.label(text=f"Class {item.class_id}")

class RANDOMIZER_UL_label_rules(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text=item.rule_type)
        row.label(text=f"→ Class {item.class_id}")


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
            RANDOMIZER_UL_classes.__name__,
            'classes',
            labeling_data, 'label_classes',
            labeling_data, 'class_active_index'
        )
        col = row.column()
        col.operator('randomizer.add_label_class', icon='ADD', text='')
        col.operator('randomizer.remove_label_class', icon='REMOVE', text='')

        box = layout.box()
        box.label(text="Object Labels", icon='OBJECT_DATA')
        row = box.row()
        row.template_list(
            RANDOMIZER_UL_object_labels.__name__,
            'object_labels',
            labeling_data, 'direct_labels',
            labeling_data, 'direct_active_index'
        )
        col = row.column()
        col.operator('randomizer.add_object_label', icon='ADD', text='')
        col.operator('randomizer.remove_object_label', icon='REMOVE', text='')

        box = layout.box()
        box.label(text="Labeling Rules", icon='RULE')
        row = box.row()
        row.template_list(
            RANDOMIZER_UL_label_rules.__name__,
            'label_rules',
            labeling_data, 'label_rules',
            labeling_data, 'rule_active_index'
        )
        col = row.column()
        col.operator('randomizer.add_label_rule', icon='ADD', text='')
        col.operator('randomizer.remove_label_rule', icon='REMOVE', text='')

        # Show rule editor if selected
        if context.scene.label_rules:
            rule = context.scene.label_rules[context.scene.label_rule_index]
            box = layout.box()
            box.prop(rule, 'rule_type', text='Type')

            if rule.rule_type == 'MATERIAL':
                box.prop(rule, 'material_name', text='Material')
            elif rule.rule_type == 'NAME_CONTAINS':
                box.prop(rule, 'name_filter', text='Contains')
            elif rule.rule_type == 'COLLECTION':
                box.prop(rule, 'collection_name', text='Collection')

            box.prop(rule, 'class_id', text='Assign to Class')