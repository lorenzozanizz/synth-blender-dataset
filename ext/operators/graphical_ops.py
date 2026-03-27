"""




"""

from .names import Labels

from bpy.types import Operator
from bpy.props import StringProperty, IntProperty

import bpy

class OpenDistributionOperator(Operator):

    bl_idname = Labels.OPEN_DISTRI_EDITOR.value
    bl_label = 'Edit Distribution'

    op_index: IntProperty()             # type: ignore

    def execute(self, context):
        scene = context.scene

        # Get selected distribution
        idx = scene.selected_distribution_index
        if idx >= len(scene.available_distributions):
            self.report({ 'ERROR' }, "No distribution selected")
            return { 'CANCELLED' }

        distribution_item = scene.available_distributions[idx]
        if not distribution_item.node_tree:
            self.report({ 'ERROR' }, "Distribution tree pointer is broken")
            return { 'CANCELLED' }

        distribution_tree = distribution_item.node_tree

        # Find existing Node Editor, if the editor is found then simply finish
        # (this just changes focus)
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                for space in area.spaces:
                    if space.type == 'NODE_EDITOR':
                        space.node_tree = distribution_tree
                        area.tag_redraw()
                        self.report({ 'INFO' }, f"Opened {distribution_tree.name}")
                        return { 'FINISHED' }

        # No Node Editor found - split view instead of new window
        # This is cleaner than opening a new window b
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                with context.temp_override(area=area):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)

                    # Find the new area and set it to Node Editor
                    for new_area in context.screen.areas:
                        if new_area != area and new_area.type == 'VIEW_3D':
                            new_area.type = 'NODE_EDITOR'
                            for space in new_area.spaces:
                                if space.type == 'NODE_EDITOR':
                                    space.node_tree = distribution_tree
                            return { 'FINISHED' }

        self.report({ 'INFO' }, "Open Node Editor manually and set tree type to Distribution")
        return { 'FINISHED' }



class PipeUpOperator(Operator):

    bl_idname = Labels.PIPE_UP_OPERATION_.value
    bl_label = "Select Node"

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        index = pipeline.active_operation_index

        # Can't move up if already at top
        if index <= 0:
            return { 'CANCELLED' }

        # Swap with previous item
        pipeline.operations.move(index, index - 1)
        # Keep selection on the moved item
        pipeline.active_operation_index = index - 1

        return { 'FINISHED' }


class PipeDownOperator(Operator):

    bl_idname = Labels.PIPE_DOWN_OPERATION_.value
    bl_label = "Select Node"

    def execute(self, context):
        pipeline = context.scene.pipeline_data
        index = pipeline.active_operation_index

        # Can't move down if already at bottom
        if index >= len(pipeline.operations) - 1:
            return {'CANCELLED'}

        # Swap with next item
        pipeline.operations.move(index, index + 1)
        pipeline.active_operation_index = index + 1

        return {'FINISHED'}


class ChangePipelineViewerTabOperator(Operator):

    bl_idname = Labels.CHANGE_VIEW_TAB_BUTTON_.value
    bl_label = 'Set Tab'
    tab: StringProperty()                               # type: ignore

    def execute(self, context):
        context.window_manager['pipeline_tab'] = self.tab
        return {'FINISHED'}


class AddFolderOperator(Operator):
    """

    """

    bl_idname = Labels.ADD_FOLDER_MENU.value
    bl_label = "Add folder"

    def execute(self, context):

        return { 'FINISHED' }
