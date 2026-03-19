from bpy.types import PropertyGroup
from bpy.props import PointerProperty, StringProperty, BoolProperty, IntProperty, CollectionProperty

class PipelineOperation(PropertyGroup):
    """Single operation in the pipeline"""
    operation_type: StringProperty(name='Type', default='randomize_pose')   # type: ignore
    enabled: BoolProperty(name='Enabled', default=True)                     # type: ignore
    seed: IntProperty(name='Seed', default=0)                               # type: ignore
    intensity: StringProperty(name='Intensity', default='0.5')              # type: ignore


class PipelineData(PropertyGroup):
    """Container for all operations"""
    operations: CollectionProperty(type=PipelineOperation)                  # type: ignore
    active_operation_index: IntProperty(default=0)                          # type: ignore

data_properties = {
    "pipeline_data": PointerProperty(
        type=PipelineData
    )
}