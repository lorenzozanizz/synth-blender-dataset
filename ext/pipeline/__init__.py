from .data import PipelineData, PipelineOperation, data_properties, PipeNames, DistributionItem
from . import operations
from .operations import operation_properties, DistributionTreeList, sync_distribution_handler, distribution_settings

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


# Update the data properties of the pipeline with settings for the configuration of each pipe's distributions
# and properties regarding the pipeline operations
data_properties.update(operation_properties)
data_properties.update(distribution_settings)

# export this name for the parent module
properties = data_properties