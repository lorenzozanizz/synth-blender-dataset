from .panels import RandomizerPanel, SettingsPanel, InfoPanel
from .pipeline_viewer_list import (RegistrationPanel, AddCameraCategoryPipeMenu, AddLightingCategoryPipeMenu,
                                   AddObjectCategoryPipeMenu, AddMaterialCategoryPipeMenu, AddConstraintCategoryPipeMenu,
                                   PipelineOperationsList,)
from .properties import ext_ui_properties, distribution_settings, operation_properties
from .pipe_editor import DistributionTreeList, sync_distribution_handler, PathsUIList, ImagePath, PositionsUIList, ObjectPosition

import bpy

def register_handlers():
    """Register all scene handlers."""
    bpy.app.handlers.depsgraph_update_post.append(sync_distribution_handler)


def unregister_handlers():
    """Unregister all scene handlers."""
    if sync_distribution_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(sync_distribution_handler)


classes = (
    RandomizerPanel, SettingsPanel, InfoPanel, RegistrationPanel, AddCameraCategoryPipeMenu,
    AddLightingCategoryPipeMenu, AddObjectCategoryPipeMenu, PipelineOperationsList,
    AddMaterialCategoryPipeMenu, AddConstraintCategoryPipeMenu, DistributionTreeList, PathsUIList,
    ImagePath, PositionsUIList, ObjectPosition
)

# Update the main UI properties of the pipeline with settings for the configuration of each pipe's distributions
# and properties regarding the pipeline operations
ext_ui_properties.update(operation_properties)
ext_ui_properties.update(distribution_settings)

properties = ext_ui_properties