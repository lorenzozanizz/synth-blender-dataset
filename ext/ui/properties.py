import os

from bpy.props import (
    StringProperty, IntProperty, BoolProperty, EnumProperty
)

ext_ui_properties = {
    "pipeline_has_unsaved_changes": BoolProperty(default=False),
    "randomizer_pipeline_save_path": StringProperty(
        name="Output path",
        subtype='FILE_PATH',
        description="Path to save JSON config"
    ),
    "randomizer_config_use_file": BoolProperty(name="Use file path", default=True),
    "randomizer_config_path": StringProperty(
        name="Input path",
        subtype='FILE_PATH',
        description="Path to your JSON config"
    ),
    "randomizer_destination_path": StringProperty(
        name="Destination",
        subtype='FILE_PATH',
        description="Save folder destination"
    ),
    "randomizer_append_checkbox": BoolProperty(
        name="Initialize counter to last number",
        default=True,
        description="Start numbering at the last identified number in the destination folder",
    ),
    "randomizer_save_prefix": StringProperty(
        name="Prefix",
        description="File naming prefix for saved images"
    ),
    "randomizer_amount": IntProperty(
        name="Amount",
        description="Number of images to generate",
        min=0,
        default=100
    ),
    "randomizer_seed": IntProperty(
        name="Seed",
        description="Random seed for reproducibility",
        min=0,
        default=0
    ),
    "randomizer_label_format": EnumProperty(
        name="Format",
        items=[("YOLO", "YOLO", "Export labels in YOLO format")]
    ),
    "randomizer_logging_path": StringProperty(
        name="Log Path",
        subtype='FILE_PATH',
        description="Path where addon logs will be saved",
        default=os.path.expanduser("~/logs/")
    ),
    "randomizer_enable_logging": BoolProperty(
        name="Enable Logging",
        default=False,
        description="Enable Logging"
    )
}
