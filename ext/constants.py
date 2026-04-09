"""

"""
from enum import Enum


prefix_ext_conflict_rename = lambda name: "synth_blender_dataset_" + name
panel_conflict_rename = lambda name: "VIEW3D_PT_" + name

MAIN_PANEL_NAME = "Generator"
PANEL_CATEGORY  = "Synthetic"

REPO_URL = "https://github.com/lorenzozanizz/synth-blender-dataset"
DOCU_URL = "https://github.com/lorenzozanizz/synth-blender-dataset/docs"

VERSION        = "1.0.0"
TARGET_VERSION = "4.5.0"

NODE_CATEGORIES_NAME = "DISTRIBUTION_NODE_CATEGORIES"
DISTRO_EDITOR_NAME   = "DistributionNodeTree"


class PipeNames(Enum):
    """

    """

    # Special type of pipe which encloses a set of sub pipes.
    FOLDER      = "Folder"

    SCALE       = "Scale"
    ROTATION    = "Rotation"
    MOVE        = "Move"
    POSITION    = "Position"
    VISIBILITY  = "Visibility"

    # Material
    MATERIAL    = "Material"
    TEXTURE     = "Texture"
    INTENSITY   = "Intensity"
    METALLIC    = "Metallic"
    ROUGHNESS   = "Roughness"
    NODE_PROP   = "Node Property"

    # Lighting
    TEMPERATURE = "Temperature"
    POWER       = "Power"
    COLOR       = "Color"

    # Constraints
    OVERLAP     = "Overlap"
    OCCLUSION   = "Occlusion"
    DISTANCE    = "Distance"
    BOUND       = "Bound"
    GROUND      = "Ground"

    # Noise
    MOTION_BLUR = "Motion Blur"


class WidgetSerializationKeys(Enum):


    DIMENSION = "dimension"

    MATERIAL = "materials"
    MATERIAL_LIST               = "materials"

    # Incomplete, a bit messy for now!
    PROPERTY = ""

    VALUE   = "value"
    VALUE_MATERIAL              = "material"
    VALUE_LABEL                 = "label"

    POSITION = "positions"
    POSITION_LIST               = "positions"

    SIMPLE  = "distribution"
    SIMPLE_PRESET_NAME          = "preset"
    SIMPLE_OFFSET_MODE          = "do_offset"
    SIMPLE_DISCRETIZE           = "do_discretize"
    SIMPLE_CLAMP                = "do_clamp"
    SIMPLE_CLAMPING_EXTREMES    = "clamping_factors"
    SIMPLE_PARAMETERS           = "parameters"

    NODE    = "distribution"
    NODE_USE_TREE               = "use_tree"
    NODE_DISTRIBUTION           = "distribution"

    PATH    = "textures"
    PATH_USE_FOLDER             = "use_folder"
    PATH_FILES                  = "files"
    PATH_FOLDER                 = "folder"

    TEXTURE = "node"
    TEXTURE_MATERIAL            = "material"
    TEXTURE_LABEL               = "label"

    OBJECT  = "target"
    OBJECT_NAMES                = "names"

    AXIS    = "axis"
    AXIS_DIMS                   = "dims"
    AXIS_RANDOMIZE_PREFIX_X     = "target_x"
    AXIS_RANDOMIZE_PREFIX_Y     = "target_Y"
    AXIS_RANDOMIZE_PREFIX_Z     = "target_Z"