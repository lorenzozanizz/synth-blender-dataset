from dataclasses import dataclass
from .names import CoreLabels

from bpy.types import Operator

@dataclass
class ExecutionParameters:
    seed: int


class GenerateOperator(Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = CoreLabels.GENERATE.value
    bl_label = "Generate Dataset"

    @staticmethod
    def extract_relevant_data(context) -> ExecutionParameters:
        return ExecutionParameters(1)

    def execute(self, context):
        """Get all selected nodes"""

        # Deserialized all pipes only ones, preparing for thousands of generations poissbly.
        interpreted_pipes = {}
        return { 'FINISHED' }
