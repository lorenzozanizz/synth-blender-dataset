"""
A file containing all the labels assigned to all operations inside the extension.
Note that the labels are divided by class and file, as to find them easily.

The labels are used around the other folders to avoid spreading "magic strings" and
to prevent dead-link operators which Blender cannot render and have no effect.

When a class requires to draw the corresponding property operator, it can access the
label as Labels.NAME.value

Operation labels which are terminated with _ are internal operations which are more likely
related to auxiliary GUI (e.g. menu drawing, etc...) although the distinction is
admittedly somewhat fuzzy

"""

from enum import Enum

class Labels(Enum):
    """ This class contains label for all operators used for all actions inside the
    extensions. To access an operator's use Labels.NAME.value
    """

    # ------------- Names inside pipeline_ops.py ---------------
    # |
    # ( Captures a general node form the shader material node-editor )
    CAPTURE_GENERAL_NODE    = "randomizer.capture_general_node"
    # ( Captures a value node form the shader material node-editor )
    CAPTURE_VALUE_NODE      = "randomizer.capture_value"
    # ( Remove a material from the sampling pool of the Material pipe )
    REMOVE_MATERIAL_POOL    = "randomizer.remove_material_from_list"
    # ( Add a material to the sampling pool of the Material pipe )
    ADD_MATERIAL_POOL       = "randomizer.add_material_to_list"
    # ( Add a position to the pool of sampled positions for the Move pipe )
    REMOVE_POSITION_POOL    = "randomizer.remove_position"
    # ( Remove a position from the pool of sampled positions for the Move pipe )
    ADD_POSITION_POOL       = "randomizer.add_position"
    # ( Capture the current position of an object (does not handle multiple objects) )
    CAPTURE_OBJ_POSITION    = "randomizer.capture_obj_position"
    # ( Capture the currently selected Image Texture shader node-editor node )
    CAPTURE_TEXTURE_NODE    = "randomizer.capture_texture"
    # ( Capture the currently selected objects, either a single one or a group )
    CAPTURE_OBJECTS          = "randomizer.capture_objects"
    # ( Edit the currently selected operation )
    EDIT_PIPE               = "randomizer.edit_operation"
    # ( Remove the currently selected operation )
    REMOVE_PIPE             = "randomizer.remove_operation"
    # ( Add a new pipe (operation) to the pipeline )
    ADD_PIPE                = "randomizer.add_operation"
    # ( An auxiliary operation used to draw the add menus (which represent possible pipes)  )
    ADD_MENU_LIST_          = "randomizer.add_operation_menu"

    # ------------- Names inside io_ops.py ---------------
    # |
    # (  )
    SETUP_LOGGER_DIR        = "randomizer.setup_log"
    # (  )
    SAVE_PIPELINE_JSON      = "randomizer.save_pipeline"
    # (  )
    LOAD_PIPELINE_JSON      = "randomizer.load_pipeline"
    # (  )
    OPEN_LOG_DIRECTORY      = "randomizer.open_log_file"

    # ------------- Names inside graphical_ops.py ---------------
    # |
    # (  )
    ADD_FOLDER_MENU         = "randomizer.add_folder"
    # (  )
    CHANGE_VIEW_TAB_BUTTON_ = "randomizer.set_pipeline_tab"
    # (  )
    PIPE_DOWN_OPERATION_    = "randomizer.down_operation"
    # (  )
    PIPE_UP_OPERATION_      = "randomizer.up_operation"
    # (  )
    EDIT_PIPE_MENU_         = "randomizer.open_distribution_editor"
    # (  )
    OPEN_DISTRI_EDITOR      = "randomizer.open_distribution_editor"

    # ------------- Names inside distribution_ops.py ---------------
    # |
    # (  )
    REMOVE_IMAGE_PATH_POOL  = "randomizer.remove_image_path"
    # (  )
    ADD_IMAGE_PATH_POOL     = "randomizer.add_image_path"
    # (  )
    REMOVE_DISTRIBUTION     = "randomizer.remove_distribution"
    # (  )
    ADD_DISTRIBUTION        = "randomizer.add_distribution"

    # ------------- Default namespace names ---------------
    # |
    # (  )
    OPEN_URL                = "wm.url_open"
