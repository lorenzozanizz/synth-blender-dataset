""" Random Dataset Generator for Blender

This addon generates synthetic datasets by applying randomized
transformations to objects in the scene and rendering multiple images.
The purpose is to synthetically generate computer visions dataset for various
tasks.

Features:
- Load configuration from JSON
- Generation oF JSON configuration directly from the extensions in Blender
- Randomize object position, rotation, and material textures, visibility
- Batch render images automatically
- Export datasets for computer vision pipelines (YOLO)

Version: 1.0.0
Blender: 4.x
License: MIT
"""

bl_info  = {
    "name": "Random Dataset Generator",
    "author": "Your Name",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "Sidebar > Randomizer",
    "description": "Load a JSON config randomize objects render N images",
    "category": "Render",
}

import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty, EnumProperty

# ------------------------= BLENDER PANEL GUI CONSTANTS =-----------------------

# Append the proprietary extension name to avoid naming conflicts with other
# extensions in the layout.
prefix_ext_conflict_rename = lambda name: "synth_blender_dataset_" + name
panel_conflict_rename = lambda name: "VIEW3D_PT_" + name

MAIN_PANEL_NAME = "Synthetic Dataset Generator"
PANEL_CATEGORY = "Synthetic"
CONFIG_URL = "https://github.com/lorenzozanizz/synth-blender-dataset"
WIKI_URL = "https://github.com/lorenzozanizz/synth-blender-dataset/wiki"

VERSION = "1.0.0"
DEVELOPED_FOR = "4.5.0"

# ------------------------= BLENDER PANEL GUI INTERFACE =-----------------------

class RandomizerPanel(bpy.types.Panel):
    """ The main panel for the randomizer class, containing the hooks for the
    configuration file, the saving file, the amount of samples, the seed for the
    random generators, the prefix to the save files, the label save format
    """

    bl_label = MAIN_PANEL_NAME
    bl_category = PANEL_CATEGORY
    bl_idname = panel_conflict_rename("random_dataset")
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):

        layout = self.layout
        scene = context.scene

        layout.prop(scene, "randomizer_config_path")
        layout.prop(scene, "randomizer_destination_path")

        layout.separator()  # Adds vertical space
        row = layout.row()
        row.label(text="Amount:")
        row.prop(scene, "randomizer_amount", text="")
        row = layout.row()
        row.label(text="Seed:")
        row.prop(scene, "randomizer_seed", text="")

        layout.separator()  # Adds vertical space
        layout.prop(scene, "randomizer_save_prefix")
        layout.prop(scene, "randomizer_label_format")
        layout.prop(scene, "randomizer_append_checkbox")

        layout.separator()  # Adds vertical space
        layout.operator("object.randomizer_generate", text="Generate", icon="TRIA_RIGHT")


class RegistrationPanel(bpy.types.Panel):
    """ The panel containing information regarding the registrations of new sampling
    operations (to be determined)
    """

    bl_label = "Operator Registration"
    bl_idname = panel_conflict_rename("random_operator_registration")
    bl_category = PANEL_CATEGORY
    bl_options = { 'DEFAULT_CLOSED' }
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, _context):
        # Currently Empty
        _a = NotImplemented


class InfoPanel(bpy.types.Panel):
    """ The panel containing information regarding the extension, its version,
    the version it was developed for, a link to the original repository and
    the documentation.
    """

    bl_label = "Info"
    bl_idname = panel_conflict_rename("random_info")
    bl_category = PANEL_CATEGORY
    bl_options = { 'DEFAULT_CLOSED' }
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, _context):
        layout = self.layout

        # Title
        col = layout.column(align=True)
        col.label(text=MAIN_PANEL_NAME, icon='INFO')
        col.separator()

        # Version Info
        col.label(text=f"Version: {VERSION}")
        col.label(text=f"Tested on Blender {DEVELOPED_FOR}")
        col.separator()

        # Links section
        col = layout.column(align=True)
        col.label(text="Links:")

        row = col.row()
        op = row.operator("wm.url_open", text="GitHub", icon='URL')
        op.url = "https://github.com/lorenzozanizz/synth-blender-dataset"
        op = row.operator("wm.url_open", text="Documentation", icon='FILE_FOLDER')
        op.url = "https://github.com/lorenzozanizz/synth-blender-dataset/wiki"

# ------------------------= SAMPLING DATA STRUCTURES =-----------------------


# ------------------------= SAMPLE GENERATION OPERATOR =-----------------------

class RandomizerGenerateOperator(bpy.types.Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = "object.randomizer_generate"
    bl_label = "Generate Dataset"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
      raise NotImplementedError

# ------------------------= BLENDER PANEL GUI CONSTANTS =-----------------------

registration_classes = (
    RandomizerPanel, RandomizerGenerateOperator, RegistrationPanel, InfoPanel
)

registration_properties = (
    "randomizer_config_path", "randomizer_destination_path", "randomizer_append_checkbox",
    "randomizer_save_prefix", "randomizer_seed", "randomizer_amount", "randomizer_label_format"
)

visual_gui_properties = {
    "randomizer_config_path": StringProperty(
        name="Config",
        subtype='FILE_PATH',
        description="Path to your JSON config"
    ),
    "randomizer_destination_path": StringProperty(
        name="Destination",
        subtype='FILE_PATH',
        description="Save folder destination"
    ),
    "randomizer_append_checkbox": BoolProperty(
        name="Start counter from last number",
        default=True,
        description="Start numbering at the last identified number in the destination folder",
    ),
    "randomizer_save_prefix": StringProperty(
        name="Save Prefix",
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
        name="Label Format",
        items=[("YOLO", "YOLO", "Export labels in YOLO format")]
    )
}


def register():
    """ Register the classes and properties for the GUI extension
    """

    # Define all the attributes for the GUI
    for prop_name, prop_value in visual_gui_properties.items():
        setattr(bpy.types.Scene, prop_name, prop_value)

    # Register all the required classes
    for cls in registration_classes:
        bpy.utils.register_class(cls)

def unregister():
    """ Unregister the classes and properties for the GUI extension
    """

    # Unregister all previously registered classes
    for cls in registration_classes:
        bpy.utils.unregister_class(cls)

    # Delete all registered properties in the environment
    for prop in registration_properties:
        delattr(bpy.types.Scene, prop)


if __name__ == "__main__":

    register()