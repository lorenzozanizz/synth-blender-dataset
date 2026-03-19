from bpy.types import Operator
import bpy

class AddDistributionOperator(Operator):
    """Create new distribution tree."""
    bl_idname = "randomizer.add_distribution"
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
    bl_idname = "randomizer.remove_distribution"
    bl_label = "Remove Distribution"

    def execute(self, context):
        scene = context.scene
        idx = scene.selected_distribution_index
        distributions = scene.available_distributions
        if idx < len(distributions):
            tree = distributions.node_tree
            bpy.data.node_groups.remove(tree)
            distributions.remove(idx)
        return { 'FINISHED' }