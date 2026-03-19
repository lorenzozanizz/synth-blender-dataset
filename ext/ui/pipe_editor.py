from ..constants import PANEL_CATEGORY, panel_conflict_rename
from ..pipeline.registry import OperationRegistry
from ..pipeline.data import PipeNames
from ..utils.logger import UniqueLogger

from bpy.types import Panel, UIList, Menu
from bpy.props import StringProperty, EnumProperty


pipe_to_ico_mapping = {
    PipeNames.SCALE: "CON_SIZELIKE",
    PipeNames.ROTATION: "CON_ROTLIKE",
    PipeNames.POSITION: "EMPTY_ARROWS",
    PipeNames.VISIBILITY: "MOD_OPACITY",
    PipeNames.MOVE: "EMPTY_AXIS",
    PipeNames.MATERIAL: "MATERIAL",
    PipeNames.TEXTURE: "NODE_TEXTURE"
}

class RegistrationPanel(Panel):
    """ The panel containing information regarding the registrations of new sampling
    operations (to be determined)
    """

    bl_label = "Pipeline Editor"
    bl_idname = panel_conflict_rename("random_operator_registration")
    bl_options = { 'DEFAULT_CLOSED' }
    bl_space_type = 'VIEW_3D'
    bl_category = PANEL_CATEGORY
    bl_region_type = 'UI'
    bl_order = 1


    def draw(self, context):
        # Currently Empty
        layout = self.layout
        layout.operator("object.randomizer_node_selector", text="Pick node", icon="LINE_DATA")
        scene = context.scene


        box = layout.box()
        box.label(text="Load pipeline", icon="WORDWRAP_OFF")
        box.prop(scene, "randomizer_config_path")
        box.operator("randomizer.load_pipeline", text="Load", icon="FILE")

        # === TAB BAR ===
        row = layout.row()
        active = context.window_manager.get('pipeline_tab', 'ops')

        for tab_id, tab_label in [('ops', 'View Pipeline'), ('config', 'Edit Current')]:
            row.operator('randomizer.set_pipeline_tab',
                         text=tab_label,
                         depress=(tab_id == active),
                         emboss=True).tab = tab_id

        layout.separator()
        scene = context.scene
        pipeline = scene.pipeline_data


        # === COLLECTION PROPERTIES - Use .add() ===
        # Add a new operation to the list

        # Which view are we in?
        if active == 'ops':
            self.draw_list_view(context, pipeline)
        elif active == 'config':
            self.draw_edit_view(context, pipeline)


    def draw_list_view(self, context, pipeline):
        """Show list of operations with +/- buttons"""
        scene = context.scene
        layout = self.layout

        # Load/Save buttons
        layout.label(text=f"Pipeline length: {len(pipeline.operations)} operation"
                          f"{'' if len(pipeline.operations) == 1 else 's'}")

        layout.separator()

        table = layout.column(align=True)
        # Create column header row.
        head = table.box()
        head.scale_y = 0.6  # shrink in height
        cols = head.column_flow(columns=5)  # ensure same number of columns
        sub = cols.row(align=True)
        sub.scale_x = 0.3
        sub.label(text="#")
        cols.label(text="Operation")
        cols.label(text="Target")
        cols.label(text="Enabled")
        table.enabled = False

        row = layout.row()
        row.template_list(
            'PipelineOperationsList',  # UIList class name
            'pipeline_operations',  # Unique ID
            pipeline,  # Data object
            'operations',  # Collection property name
            pipeline,  # Active data object
            'active_operation_index'  # Active index property name
        )

        col = row.column(align=True)
        col.operator('randomizer.add_operation_menu', icon='ADD', text='')
        col.operator('randomizer.remove_operation', icon='REMOVE', text='')
        col.separator()

        col.operator('randomizer.up_operation', icon='BACK', text='')
        col.operator('randomizer.down_operation', icon='FORWARD', text='')

        layout.separator()

        # === SAVE SECTION ===

        box = layout.box()
        col = box.column(align=True)
        col.label(text='Save Pipeline', icon='FILE_TICK')
        col.separator()
        col.prop(scene, "randomizer_pipeline_save_path")
        col.separator()
        row = col.row(align=True)
        row.operator('randomizer.save_pipeline', text='Save', icon="FILE_TICK")


    def draw_edit_view(self, context, pipeline):
        """Show detailed editor for selected operation"""
        layout = self.layout
        scene = context.scene

        if not pipeline.operations:
            layout.label(text='There are no operations.')
            return

        op_index = pipeline.active_operation_index
        operation = pipeline.operations[op_index]

        # Header
        layout.label(text=f"Editing: {operation.operation_type}", icon='PREFERENCES')
        layout.separator()

        reg_op = OperationRegistry.get_operation(operation.operation_type)

        # Draw its editor - just one line!
        reg_op.draw_editor(layout, context)


        layout.separator()
        layout.operator("randomizer.open_distribution_editor", text="Open tree")

        layout.operator('randomizer.set_pipeline_tab',
                         text="Ok", emboss=True).tab = 'ops'

        # Back button
        # layout.operator('wm.back_from_edit', text='Back to List', icon='BACK')

    def draw_filter(self, _context, layout):
        """Draw the filter options and search bar"""
        row = layout.row()

        # Search text input (automatic)
        row.prop(self, "filter_name", text="")

        # Filter by operation type (optional)
        row = layout.row(align=True)
        row.prop(self, "filter_operation_type", expand=True)

    def filter_items(self, _context, data, name):
        """Filter and sort items based on search"""
        items = getattr(data, name)

        # Create filter list (1 = show, 0 = hide)
        flt_flags = [self.bitflag_filter_item] * len(items)
        flt_neworder = list(range(len(items)))

        # Filter by search name
        if self.filter_name:
            for idx, item in enumerate(items):
                if self.filter_name.lower() not in item.operation_type.lower():
                    flt_flags[idx] = 0

        return flt_flags, flt_neworder

    # Add filter properties
    filter_name: StringProperty(default="", options={'TEXTSEARCH'}) # type: ignore
    filter_operation_type: EnumProperty( # type: ignore
        items=[
            ('ALL', 'All', 'Show all'),
            ('RANDOMIZE', 'Randomize', 'Show randomize ops'),
        ],
        default='ALL'
    )


class PipelineOperationsList(UIList):

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        # item = the current PipelineOperation

        operation = item

        # Left side: icon + operation name
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.scale_x = 0.3  # Make it tiny
        sub.label(text=f"{index + 1}")

        row.label(text=operation.operation_type, icon='LIGHT')

        # Middle: show some property
        row.label(text=f"Seed: {operation.seed}")

        row.prop(operation, 'enabled', text='')
        # Right side: edit button
        row.operator('randomizer.edit_operation', text='', icon='GREASEPENCIL').op_index = index


# Submenu for lighting operations
class AddLightingCategoryPipeMenu(Menu):
    bl_label = 'Lighting'
    bl_idname = 'AddLightingCategoryPipeMenu'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        layout.label(text='Lighting')


# Submenu for constraint operations
class AddConstraintCategoryPipeMenu(Menu):
    bl_label = 'Constraints'
    bl_idname = 'AddConstraintCategoryPipeMenu'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        layout.label(text='Constraints')


# Submenu for object operations
class AddObjectCategoryPipeMenu(Menu):
    bl_label = 'Object'
    bl_idname = 'AddObjectCategoryPipeMenu'

    def draw(self, context):
        layout = self.layout
        for name in (
            PipeNames.ROTATION, PipeNames.MOVE, PipeNames.POSITION, PipeNames.SCALE, PipeNames.VISIBILITY
        ):
            layout.operator("randomizer.add_operation", text=name.value,
                            icon=pipe_to_ico_mapping[name]).op_name = name.value

# Submenu for camera operations
class AddCameraCategoryPipeMenu(Menu):
    bl_label = 'Camera'
    bl_idname = 'AddCameraCategoryPipeMenu'

    def draw(self, context):
        layout = self.layout
        layout.label(text='Camera')


# Submenu for material operations
class AddMaterialCategoryPipeMenu(Menu):
    bl_label = 'Material'
    bl_idname = 'AddMaterialCategoryPipeMenu'

    def draw(self, context):
        layout = self.layout
        for name in (
            PipeNames.MATERIAL, PipeNames.TEXTURE, PipeNames.POSITION, PipeNames.SCALE, PipeNames.VISIBILITY
        ):
            layout.operator("randomizer.add_operation", text=name.value,
                            icon=pipe_to_ico_mapping[name]).op_name = name.value
