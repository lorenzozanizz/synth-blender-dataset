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