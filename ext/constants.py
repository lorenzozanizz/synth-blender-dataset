""" Module containing several constants definitions that are used throughout the code,
including pipe names and serialization constants.

The module contains the extension version, the urls of the repositories used in the
extension info panel, the names of the extension panels and the blender target version,
the names of the pipes used to register them to the various registries in the code for UI
and functionality, and names used in the serialization and deserialization of pipes.
"""

from enum import Enum

def panel_conflict_rename(name: str) -> str:
    """ Get the prefix to name the registered panels of the blender extension """
    return "VIEW3D_PT_" + name

# Names of the main panel and the category name
MAIN_PANEL_NAME = "Generator"
PANEL_CATEGORY  = "Gensynth"

REPO_URL = "https://github.com/lorenzozanizz/gensynth"
DOCU_URL = "https://github.com/lorenzozanizz/gensynth/docs"

VERSION        = "1.0.0"
TARGET_VERSION = "4.5.0"

# Names of the internal distribution tree for arbitrary distributions
NODE_CATEGORIES_NAME = "DISTRIBUTION_NODE_CATEGORIES"
DISTRO_EDITOR_NAME   = "DistributionNodeTree"


class PipeNames(Enum):
    """ A class containing the key used to register all the pipes to all the registries
    in the code including UI, validation and operation.

    To access a key one writes PipeNames.NAME.value
    """

    # Special type of pipe which encloses a set of sub pipes.
    FOLDER      = "Folder"

    SCALE       = "Scale"
    ROTATION    = "Rotation"
    MOVE        = "Move"
    POSITION    = "Position"
    VISIBILITY  = "Visibility"
    LINE        = "Line"
    SELECT      = "Select"
    SPHERICAL   = "Sphere"          # (x)

    # Material
    MATERIAL    = "Material"
    TEXTURE     = "Texture"
    INTENSITY   = "Intensity"
    METALLIC    = "Metallic"        # (x)
    ROUGHNESS   = "Roughness"       # (x)
    NODE_PROP   = "Node Property"   # (x)
    BASE_COLOR  = "Base Color"      # (x)

    # Lighting
    TEMPERATURE = "Temperature"     # (x)
    POWER       = "Power"           # (x)
    COLOR       = "Color"           # (x)

    # Camera
    BEZIER_LOCK = "Bezier Lock"
    SPHERE_LOCK = "Sphere Lock"
    FOCAL_LEN   = "Focal Length"
    JITTER      = "Camera Jitter"   # (x)
    POV         = "Change POVs"     # (x)

    # Constraints
    OVERLAP     = "Overlap"         # (x)
    OCCLUSION   = "Occlusion"       # (x)
    DISTANCE    = "Distance"        # (x)
    BOUND       = "Bound"           # (x)
    GROUND      = "Ground"          # (x)

    # Noise
    MOTION_BLUR = "Motion Blur"     # (x)


class WidgetSerializationKeys(Enum):
    """ Keys that are used to serialize and deserialize the pipes in various
    stages of the code. This is done to use blender's property system to
    save the settings of a pipeline inside a .blend file.

    Using the enum keys instead of the strings helps prevent dangling references.
    """

    # Meta-name used for conditional widgets.
    ENABLED = "enabled"

    TYPED_OBJ = "typed_obj"
    TYPED_OBJ_NAME = "name"

    BEZIER = "bezier"
    BEZIER_NAME = "name"

    DIMENSION = "dimension"

    SELECT = "select"
    SELECT_K = "k"

    MATERIAL = "materials"
    MATERIAL_LIST               = "materials"

    # Incomplete, a bit messy for now!
    PROPERTY = ""

    SHADER_NODE    = "shader_node"
    SHADER_MATERIAL             = "shader_mat"
    SHADER_LABEL                = "label"

    VALUE   = "value"
    VALUE_MATERIAL              = "material"
    VALUE_LABEL                 = "label"

    POSITION                    = "positions"   # Parent name
    POSITION_LIST               = "positions"

    SIMPLE                      = "distribution" # ^ Parent name
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
    AXIS_RANDOMIZE_PREFIX_X     = "randomize_x"
    AXIS_RANDOMIZE_PREFIX_Y     = "randomize_y"
    AXIS_RANDOMIZE_PREFIX_Z     = "randomize_z"

    OFFSET  = "offset"
    OFFSET_MODE                 = "mode"