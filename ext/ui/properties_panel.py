from ..constants import panel_conflict_rename

from bpy.types import Panel

class PropertiesPanel(Panel):

    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_idname = panel_conflict_rename("properties_randomizer")
    bl_label = 'My Add-on Settings'

    def draw(self, context):
        pass