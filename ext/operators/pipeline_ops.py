from bpy.types import Operator
from bpy.props import IntProperty, StringProperty

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