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


GitHub: https://github.com/lorenzozanizz/synth-blender-dataset
Documentation: https://github.com/lorenzozanizz/synth-blender-dataset/wiki


Version: 1.0.0
Blender: 4.x
License: MIT
"""

bl_info  = {
    "name": "Random Dataset Generator",
    "author": "lorenzozanizz",
    "version": (1, 0, 0),
    "blender": (4, 5, 0),
    "location": "Sidebar > Randomizer",
    "description": "Load a JSON config randomize objects render N images",
    "category": "Render",
}

import logging

# Immediately define the logger at the module level, this module is
# to be shared by all operations.
logger = None
current_log_file: str = ""

import subprocess
import platform
import os

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

# Bpy imports
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
    bl_order = 0

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
    bl_order = 1
    def draw(self, _context):
        # Currently Empty
        layout = self.layout


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
    bl_order = 3
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


class OpenLogsOperator(bpy.types.Operator):
    """Open the log file in default editor"""
    bl_idname = "randomizer.open_log_file"
    bl_label = "Open Log File"

    def execute(self, context):
        global current_log_file

        if not os.path.exists(current_log_file):
            self.report({'ERROR'}, "Log file does not exist.")
            return { 'CANCELLED' }

        # Open file with default app
        try:
            if platform.system() == "Windows":
                os.startfile(current_log_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", current_log_file])
            else:  # Linux
                subprocess.Popen(["xdg-open", current_log_file])

        except Exception as e:
            self.report({ 'ERROR' }, f"Could not open log file: {e}")

        return { 'FINISHED' }


class SettingsPanel(bpy.types.Panel):
    """ The main panel for the randomizer class, containing the hooks for the
    configuration file, the saving file, the amount of samples, the seed for the
    random generators, the prefix to the save files, the label save format
    """

    bl_label = "Settings"
    bl_category = PANEL_CATEGORY
    bl_idname = panel_conflict_rename("random_settings")
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = { 'DEFAULT_CLOSED' }
    bl_order = 2

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        # Title
        row = layout.row(align=True)
        row.label(text="Logging", icon='GREASEPENCIL')

        row.prop(scene, "randomizer_enable_logging")

        box = layout.box()
        box.enabled = scene.randomizer_enable_logging
        box.prop(scene, "randomizer_logging_path")
        row = box.row(align=True)
        row.operator("randomizer.open_log_file", text="Open logs", icon="KEY_MENU")

        row.operator("randomizer.setup_log", text="Save path", icon="FILE_TICK")
        layout.separator()

def setup_logger_from_scene(context):
    """ Setup logger using scene property """
    global logger
    global current_log_file

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(context.scene.randomizer_logging_path, f"logs_{timestamp}.txt")
    current_log_file = log_path

    # Remove existing handlers
    if logger:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger = logging.getLogger("default_logger")
    logger.setLevel(logging.DEBUG)

    try:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        logger.info(f"Completed logger setup: {log_path}")
        return True

    except Exception as e:
        context.report({'ERROR'}, f"Could not setup logger: {e}")
        return False


class ApplyLogPathOperator(bpy.types.Operator):
    bl_idname = "randomizer.setup_log"
    bl_label = "Apply Log Path"

    def execute(self, context):
        if setup_logger_from_scene(context):
            self.report({'INFO'}, "Logger updated!")
            return { 'FINISHED' }
        else:
            self.report({'ERROR'}, "Failed to update logger")
            return { 'CANCELLED' }



# ------------------------= SAMPLING DATA STRUCTURES =-----------------------

RECOGNIZED_DISTRIBUTIONS = ("normal", "poisson", "uniform", "gamma", "custom")

class DistributionType(Enum):
    NORMAL = 0
    POISSON = 1
    UNIFORM = 2
    CUSTOM = 4


# ------------------------= SAMPLE GENERATION OPERATOR =-----------------------

class RandomizerGenerateOperator(bpy.types.Operator):
    """Main operator that reads the config and runs the render loop"""

    bl_idname = "object.randomizer_generate"
    bl_label = "Generate Dataset"
    bl_options = { 'REGISTER', 'UNDO' }

    def execute(self, context):
        """Get all selected nodes"""

        selected = []
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                space = area.spaces.active
                if space.node_tree:
                    for node in space.node_tree.nodes:
                        if node.select:
                            selected.append(node)

        scene = context.scene
        config_path = scene.randomizer_config_path

        return selected

# ------------------------= BLENDER PANEL GUI CONSTANTS =-----------------------

registration_classes = (
    RandomizerPanel, RegistrationPanel, SettingsPanel, InfoPanel,
    OpenLogsOperator, ApplyLogPathOperator, RandomizerGenerateOperator
)

registration_properties = (
    "randomizer_config_path", "randomizer_destination_path", "randomizer_append_checkbox",
    "randomizer_save_prefix", "randomizer_seed", "randomizer_amount", "randomizer_label_format",
    "randomizer_enable_logging", "randomizer_logging_path",
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
        name="Initialize counter to last number",
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