from bpy.types import Operator
from bpy.props import IntProperty, StringProperty
import bpy

class PipeAddOperator(Operator):

    bl_idname = "randomizer.add_operation"
    bl_label = "Add a new pipe to the pipeline"

    op_name: StringProperty(default="Nothing")  # type: ignore

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        new_op = pipeline.operations.add()
        new_op.operation_type = self.op_name
        new_op.seed = 0
        new_op.intensity = '0.5'
        new_op.enabled = True
        return { 'FINISHED' }


class PipeRemoveOperator(Operator):

    bl_idname = "randomizer.remove_operation"
    bl_label = "Select Node"

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        index = pipeline.active_operation_index

        # Check if there are operations
        if not pipeline.operations:
            self.report({'WARNING'}, 'No operations to remove')
            return {'CANCELLED'}

        # Remove the operation at the active index
        pipeline.operations.remove(index)

        # Adjust active index if needed (if we removed the last item)
        if pipeline.active_operation_index >= len(pipeline.operations):
            pipeline.active_operation_index = max(0, len(pipeline.operations) - 1)

        return { 'FINISHED' }


class MenuOperator(Operator):
    bl_idname = 'randomizer.add_operation_menu'
    bl_label = 'Add Operation'

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.popup_menu(self.draw_menu)
        return {'FINISHED'}

    def draw_menu(self, menu, context):
        layout = menu.layout

        # Lighting category
        layout.menu('AddLightingCategoryPipeMenu', icon="LIGHT")
        layout.menu('AddCameraCategoryPipeMenu', icon="VIEW_CAMERA")
        layout.menu('AddObjectCategoryPipeMenu', icon="CUBE")
        layout.menu('AddMaterialCategoryPipeMenu', icon="MATERIAL")
        layout.menu('AddConstraintCategoryPipeMenu', icon="RESTRICT_INSTANCED_OFF")


class EditPipeOperator(Operator):
    bl_idname = "randomizer.edit_operation"
    bl_label = "Select Node"

    op_index: IntProperty(default=0)        # type: ignore

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        # Select the operation in the UIList
        pipeline.active_operation_index = self.op_index

        # Switch to edit tab
        context.window_manager['pipeline_tab'] = 'config'

        return { 'FINISHED' }


class CaptureObjectsOperator(Operator):
    """Capture currently selected objects"""

    bl_idname = "randomizer.capture_objects"
    bl_label = "Capture Objects"

    def execute(self, context):
        selected = context.selected_objects

        if not selected:
            self.report({ 'WARNING' }, "No objects selected")
            return { 'CANCELLED' }

        # Store names
        names = ", ".join([obj.name for obj in selected])
        context.scene.targeted_objects_display = names

        self.report({ 'INFO' }, f"Captured {len(selected)} objects")
        return { 'FINISHED' }


class CaptureMaterialOperator(Operator):
    """Capture currently selected objects"""

    bl_idname = "randomizer.capture_texture"
    bl_label = "Capture Texture"

    def execute(self, context):
        selected, mat_name = self.get_selected_node_and_material(context)

        if not selected:
            return { 'CANCELLED' }

        # Store name
        lab = selected.label
        context.scene.targeted_material_display = f"{mat_name} > {lab}"

        self.report({ 'INFO' }, f"Captured: {mat_name} > {lab}")
        return { 'FINISHED' }

    def get_selected_node_and_material(self, context) -> tuple:
        """Get the currently selected node in the active editor"""

        # Get active editor area
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                # Get the node tree
                space = area.spaces.active
                node_tree = space.node_tree
                if node_tree:
                    mat_name = "Unknown Material"
                    if hasattr(space, "id") and space.id:
                        mat_name = space.id.name

                    # Find selected nodes
                    for node in node_tree.nodes:
                        if not node.select:
                            continue
                        if not node.bl_idname == 'ShaderNodeTexImage':
                            return None, None
                        # At this point the node is selected and an image texture node.
                        if not node.label or node.bl_label.strip() == "":
                            self.report({'WARNING'}, f"Node must have a label to ensure safety!")
                            return None, None
                        else:
                            return node, mat_name
        return None, None

class CaptureObjectPositionOperator(Operator):

    bl_idname = "randomizer.capture_obj_position"
    bl_label = "Capture Object Position"

    def execute(self, context):
        obj = bpy.context.active_object
        if not obj:
            self.report({ 'WARNING' }, "No objects selected")
            return {'CANCELLED'}
        positions = context.scene.position_collection
        new_op = positions.add()
        new_op.pos = obj.location

        self.report({'INFO'}, f"Captured position from currently selected object.")
        return {'FINISHED'}


class PositionAddOperator(Operator):

    bl_idname = "randomizer.add_position"
    bl_label = "Add a new target position"

    op_name: StringProperty(default="Nothing")  # type: ignore

    def execute(self, context):
        positions = context.scene.position_collection
        positions.add()
        return { 'FINISHED' }


class PositionRemoveOperator(Operator):

    bl_idname = "randomizer.remove_position"
    bl_label = "Delete the selected target position"

    def execute(self, context):
        scene = context.scene
        positions = context.scene.position_collection
        index = positions.selected_position_index

        if not positions:
            self.report({'WARNING'}, 'No Position to remove')
            return {'CANCELLED'}

        positions.remove(index)

        if scene.selected_position_index >= len(positions):
            scene.selected_position_index = max(0, len(positions) - 1)

        return { 'FINISHED' }



class AddMaterialToListOperator(Operator):
    """Add selected material to list"""
    bl_idname = "randomizer.add_material_to_list"
    bl_label = "Add Material"

    # Dropdown property with all materials
    material: bpy.props.EnumProperty(                           # type: ignore
        name="Material",
        description="Select material to add",
        items= lambda self, context: [                           # type: ignore
            (mat.name, mat.name, "")
            for mat in bpy.data.materials
        ] or [("NONE", "No materials", "")]
    )

    def execute(self, context):
        scene = context.scene

        mat = bpy.data.materials.get(self.material)

        if not mat:
            self.report({'WARNING'}, "Material not found")
            return { 'CANCELLED' }

        for item in scene.material_list:
            if item.material == mat:
                self.report({'INFO'}, f"{mat.name} already in list")
                return { 'CANCELLED' }

        new_item = scene.material_list.add()
        new_item.material = mat

        self.report({'INFO'}, f"Added {mat.name}")
        return {'FINISHED'}

    def invoke(self, context, _event):
        return context.window_manager.invoke_props_dialog(self)


class RemoveMaterialFromListOperator(Operator):
    """Remove material from list"""
    bl_idname = "randomizer.remove_material_from_list"
    bl_label = "Remove"

    def execute(self, context):
        scene = context.scene
        idx = scene.material_list_index

        if idx < len(scene.material_list):
            scene.material_list.remove(idx)

        return {'FINISHED'}
