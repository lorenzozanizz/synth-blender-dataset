from .panels import RandomizerPanel, SettingsPanel, InfoPanel
from .pipe_editor import (RegistrationPanel, AddCameraCategoryPipeMenu, AddLightingCategoryPipeMenu,
                         AddObjectCategoryPipeMenu, AddMaterialCategoryPipeMenu, AddConstraintCategoryPipeMenu,
                          PipelineOperationsList)
from .properties import ext_ui_properties

classes = (
    RandomizerPanel, SettingsPanel, InfoPanel, RegistrationPanel, AddCameraCategoryPipeMenu,
    AddLightingCategoryPipeMenu, AddObjectCategoryPipeMenu, PipelineOperationsList,
    AddMaterialCategoryPipeMenu, AddConstraintCategoryPipeMenu
)

properties = ext_ui_properties