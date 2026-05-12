from .names import Labels

from bpy.types import Operator
from bpy.props import StringProperty
import bpy

class AddDistributionOperator(Operator):
    """Create new distribution tree."""

    bl_idname = Labels.ADD_DISTRIBUTION.value
    bl_label = "Add Distribution"

    def execute(self, _context):
        # Create new DistributionNodeTree
        bpy.data.node_groups.new(
            name="Distribution",
            type="DistributionNodeTree"
        )
        return {'FINISHED'}


class RemoveDistributionOperator(Operator):
    """Remove selected distribution tree."""

    bl_idname = Labels.REMOVE_DISTRIBUTION.value
    bl_label = "Remove Distribution"

    def execute(self, context):
        scene = context.scene
        idx = scene.selected_distribution_index
        distributions = scene.available_distributions

        if idx < len(distributions):
            tree = distributions[idx].node_tree
            bpy.data.node_groups.remove(tree)
            distributions.remove(idx)

        # Clamp index if needed
        if scene.selected_distribution_index >= len(distributions):
            scene.selected_distribution_index = max(0, len(distributions) - 1)
        return { 'FINISHED' }


class AddImagePathOperator(Operator):
    """Add image file to list"""

    bl_idname = Labels.ADD_IMAGE_PATH_POOL.value
    bl_label = "Add Image"

    filepath: StringProperty(subtype='FILE_PATH')           # type: ignore

    def execute(self, context):
        item = context.scene.image_paths.add()
        item.path = self.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class RemoveImagePathOperator(Operator):
    """Remove image path from list"""

    bl_idname = Labels.REMOVE_IMAGE_PATH_POOL.value
    bl_label = "Remove Image"

    def execute(self, context):
        scene = context.scene
        idx = scene.selected_image_path_index

        if idx < len(scene.image_paths):
            scene.image_paths.remove(idx)

        return {'FINISHED'}


# Operator to add palette colors
class ColorPaletteAddOperator(Operator):
    """Add a new color to the palette"""
    bl_idname = Labels.ADD_PALETTE_ITEM.value
    bl_label = "Add Color"

    def execute(self, context):
        scene = context.scene
        item = scene.color_dist_palette_items.add()
        item.color = (1.0, 1.0, 1.0, 1.0)
        item.weight = 1.0
        scene.color_dist_palette_index = len(scene.color_dist_palette_items) - 1
        return {'FINISHED'}


# Operator to remove palette colors
class ColorPaletteRemoveOperator(Operator):
    """Remove the active color from the palette"""
    bl_idname = Labels.REMOVE_PALETTE_ITEM.value
    bl_label = "Remove Color"

    def execute(self, context):
        scene = context.scene
        if scene.color_dist_palette_items:
            scene.color_dist_palette_items.remove(scene.color_dist_palette_index)
            if scene.color_dist_palette_index > 0:
                scene.color_dist_palette_index -= 1
        return {'FINISHED'}


# Operator to add gradient colors
class ColorGradientAddOperator(Operator):
    """Add a new color to the gradient"""
    bl_idname = Labels.ADD_GRADIENT_ITEM.value
    bl_label = "Add Color"

    def execute(self, context):
        scene = context.scene
        item = scene.color_dist_gradient_items.add()
        item.color = (1.0, 1.0, 1.0, 1.0)
        item.weight = 0.5  # Position in gradient (0-1)
        scene.color_dist_gradient_index = len(scene.color_dist_gradient_items) - 1
        return {'FINISHED'}


# Operator to remove gradient colors
class ColorGradientRemoveOperator(Operator):
    """Remove the active color from the gradient"""
    bl_idname = Labels.REMOVE_GRADIENT_ITEM.value
    bl_label = "Remove Color"

    def execute(self, context):
        scene = context.scene
        if scene.color_dist_gradient_items:
            scene.color_dist_gradient_items.remove(scene.color_dist_gradient_index)
            if scene.color_dist_gradient_index > 0:
                scene.color_dist_gradient_index -= 1
        return {'FINISHED'}


