from bpy.types import PropertyGroup, NodeTree
from bpy.props import PointerProperty, StringProperty, BoolProperty, IntProperty, CollectionProperty

class PipelineOperation(PropertyGroup):
    """Single operation in the pipeline"""

    operation_type: StringProperty(name='Type', default='randomize_pose')   # type: ignore
    enabled: BoolProperty(name='Enabled', default=True)                     # type: ignore
    name: StringProperty(name='Name', default="Unnamed")                    # type: ignore
    config: StringProperty(name='Config', default='{}')                     # type: ignore
    order: IntProperty(default=0)                                           # type: ignore
    valid: BoolProperty(name='Valid', default=False)                        # type: ignore


class PipelineData(PropertyGroup):
    """Container for all operations"""
    operations: CollectionProperty(type=PipelineOperation)                  # type: ignore
    active_operation_index: IntProperty(default=0)                          # type: ignore

    def get_last_operation_order(self) -> int:
        max_order = 1
        for op in self.operations:
            if op.order > max_order:
                max_order = op.order
        return max_order

# Dummy PropertyGroup for the list
class DistributionItem(PropertyGroup):
    """Dummy item for UIList."""
    name: StringProperty()                                                  # type: ignore

    # Pointer to the real node bpy item
    node_tree: PointerProperty(                                             # type: ignore
        type=NodeTree,
        name="Node Tree",
        description="Reference to the actual DistributionNodeTree instance"
    )

data_properties = {
    "pipeline_data": PointerProperty(
        type=PipelineData
    ),
    "available_distributions": CollectionProperty(
        type=DistributionItem
    ),
    "selected_distribution_index": IntProperty(default=0)
}
