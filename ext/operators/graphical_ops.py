"""




"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty

from ..constants import DISTRO_EDITOR_NAME

class OpenDistributionOperator(Operator):
    bl_idname = 'randomizer.open_distribution_editor'
    bl_label = 'Edit Distribution'

    op_index: IntProperty()

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        operation = pipeline.operations[self.op_index]

        # Find or create a Node Editor area
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                # Found one, use it
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.tree_type = DISTRO_EDITOR_NAME
                        # space.node_tree = operation.distribution_tree
                        area.tag_redraw()
                return {'FINISHED'}

        # No Node Editor found, create one (optional)
        bpy.ops.wm.window_new()
        self.report({'INFO'}, 'Open Node Editor and set tree type to Distribution')
        return {'FINISHED'}


class PipeUpOperator(Operator):

    bl_idname = "randomizer.up_operation"
    bl_label = "Select Node"

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        index = pipeline.active_operation_index

        # Can't move up if already at top
        if index <= 0:
            return {'CANCELLED'}

        # Swap with previous item
        pipeline.operations.move(index, index - 1)

        # Keep selection on the moved item
        pipeline.active_operation_index = index - 1

        return {'FINISHED'}


class PipeDownOperator(Operator):
    bl_idname = "randomizer.down_operation"
    bl_label = "Select Node"

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        index = pipeline.active_operation_index

        # Can't move down if already at bottom
        if index >= len(pipeline.operations) - 1:
            return {'CANCELLED'}

        # Swap with next item
        pipeline.operations.move(index, index + 1)

        # Keep selection on the moved item
        pipeline.active_operation_index = index + 1

        return {'FINISHED'}


class ChangePipelineViewerTabOperator(Operator):
    bl_idname = 'randomizer.set_pipeline_tab'
    bl_label = 'Set Tab'
    tab: StringProperty()

    def execute(self, context):
        context.window_manager['pipeline_tab'] = self.tab
        return {'FINISHED'}