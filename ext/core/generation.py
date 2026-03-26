from .names import CoreLabels

from bpy.types import Operator

class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = CoreLabels.GENERATE_OPERATOR.value
    bl_label = "Generate Dataset"

    def execute(self, context):
        """Get all selected nodes"""
        return { 'FINISHED' }

