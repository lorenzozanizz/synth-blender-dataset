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
    # ( Setup the logger directory and create the log file )
    SETUP_LOGGER_DIR        = "randomizer.setup_log"
    # ( Save a pipeline inside a JSON file as a human-readable dictionary )
    SAVE_PIPELINE_JSON      = "randomizer.save_pipeline"
    # ( Load a pipeline from a JSON file as inner pipe representation )
    LOAD_PIPELINE_JSON      = "randomizer.load_pipeline"
    # ( Open the log file directory using operative system utils. A bit messy on w11 noteblock )
    OPEN_LOG_DIRECTORY      = "randomizer.open_log_file"

    # ------------- Names inside graphical_ops.py ---------------
    # |
    # ( Add a special folder pipe which acts as a container of sub-pipes for neatness )
    ADD_FOLDER_MENU         = "randomizer.add_folder"
    # ( Set the current tab for the pipeline editor, e.g. list vs. edit pipe )
    CHANGE_VIEW_TAB_BUTTON_ = "randomizer.set_pipeline_tab"
    # ( Move a pipe down in the pipeline )
    PIPE_DOWN_OPERATION_    = "randomizer.down_operation"
    # ( Move the pipe up in the pipeline )
    PIPE_UP_OPERATION_      = "randomizer.up_operation"
    # ( Open the editor for the selected distribution in another workflow sidebar)
    OPEN_DISTRI_EDITOR      = "randomizer.open_distribution_editor"

    # ------------- Names inside distribution_ops.py ---------------
    # |
    # ( Remove a target image path from the randomization pool )
    REMOVE_IMAGE_PATH_POOL  = "randomizer.remove_image_path"
    # ( Add a target image path to the randomization pool )
    ADD_IMAGE_PATH_POOL     = "randomizer.add_image_path"
    # ( Remove a distribution from the distribution selector list )
    REMOVE_DISTRIBUTION     = "randomizer.remove_distribution"
    # ( Add a distribution to the distribution selector list )
    ADD_DISTRIBUTION        = "randomizer.add_distribution"

    # ------------- Default namespace names ---------------
    # |
    # ( Default operator to open a URL.  )
    OPEN_URL                = "wm.url_open"
