from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = "object.randomizer_generate"
    bl_label = "Generate Dataset"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        """Get all selected nodes"""

        selected = []
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                space = area.spaces.active
                if space.node_tree:
                    for node in space.node_tree.nodes:
                        if node.select:
                            selected.append(node)

        scene = context.scene

        return selected
