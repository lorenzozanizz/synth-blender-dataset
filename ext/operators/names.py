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
    # ( Captures a general node form the shader material node editor )
    CAPTURE_GENERAL_NODE    = "randomizer.capture_general_node"
    # ( Captures a value node form the shader material node editor )
    CAPTURE_VALUE_NODE      = "randomizer.capture_value"
    # ( Remove a material from the sampling pool of the Material pipe )
    REMOVE_MATERIAL_POOL    = "randomizer.remove_material_from_list"
    # ( Add a material to the sampling pool of the Material pipe )
    ADD_MATERIAL_POOL       = "randomizer.add_material_to_list"
    # (  )
    REMOVE_POSITION_POOL    = "randomizer.remove_position"
    # (  )
    ADD_POSITION_POOL       = "randomizer.add_position"
    # (  )
    CAPTURE_OBJ_POSITION    = "randomizer.capture_obj_position"
    # (  )
    CAPTURE_TEXTURE_NODE    = "randomizer.capture_texture"
    # (  )
    CAPTURE_OBJECT          = "randomizer.capture_objects"
    # (  )
    EDIT_PIPE               = "randomizer.edit_operation"
    # (  )
    REMOVE_PIPE             = "randomizer.remove_operation"
    # (  )
    ADD_PIPE                = "randomizer.add_operation"
    # (  )
    ADD_MENU_LIST_          = "randomizer.add_operation_menu"

    # ------------- Names inside pipeline_ops.py ---------------


    # ------------- Names inside graphical_ops.py ---------------


    # ------------- Names inside io_ops.py ---------------


    # ------------- Names inside distribution_ops.py ---------------

