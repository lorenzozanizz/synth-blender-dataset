from .data import PipelineData, PipelineOperation, data_properties, PipeNames, DistributionItem
from . import operations
from .operations import operation_properties, DistributionTreeList, sync_distribution_handler

import bpy

def register_handlers():
    """Register all scene handlers."""
    bpy.app.handlers.depsgraph_update_post.append(sync_distribution_handler)


def unregister_handlers():
    """Unregister all scene handlers."""
    if sync_distribution_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(sync_distribution_handler)


classes = (
    PipelineOperation, PipelineData, DistributionItem, DistributionTreeList
)

data_properties.update(operation_properties)
properties = data_properties