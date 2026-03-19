"""



"""
from .data import PipeNames
from .registry import OperationRegistry
from ..utils.logger import UniqueLogger

from abc import ABC, abstractmethod

from bpy.props import BoolProperty, IntProperty, StringProperty
from bpy.types import UIList
import bpy


class PipelineOperation(ABC):
    """Base class for all pipeline operations."""

    operation_type: str  # "randomize_position", "randomize_rotation", etc.

    @abstractmethod
    def draw_editor(self, layout, context):
        """Draw this operation's editor UI."""
        pass

    @abstractmethod
    def get_default_config(self) -> dict:
        """Return default config for this operation."""
        pass

    def get_config(self) -> dict:
        pass

    @abstractmethod
    def execute(self, scene, objects):
        """Execute this operation on objects."""
        pass


def get_tree_dimensionality(tree):
    return 1


class DistributionTreeList(UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        """Draw each distribution tree."""

        distribution_item = item

        row = layout.row(align=True)
        # Middle: Tree name with icon

        row.label(text=distribution_item.name, icon='NODETREE')

        # Right: Dimensionality
        if distribution_item.node_tree:
            dims = get_tree_dimensionality(distribution_item.node_tree)
            row.label(text=f"{dims}D", icon='EMPTY_ARROWS')
        else:
            # Tree pointer is broken
            row.label(text="Broken Tree Link", icon='ERROR')


def get_all_distribution_trees():
    """Get all saved DistributionNodeTree instances."""
    return [tree for tree in bpy.data.node_groups
            if tree.bl_idname == "DistributionNodeTree"]

def get_saved_distributions_names(context):
    items = []
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "DistributionNodeTree":
            items.append((tree.name, tree.name, ""))
    return items if items else [("NONE", "None", "")]

class ObjectTargeter:

    @staticmethod
    def draw(layout, context):
        pass

class AxisTarget:

    @staticmethod
    def draw(layout, context):
        layout = layout
        scene = context.scene

        # 3 checkboxes in a row
        row = layout.row(align=True)
        row.label(text="Target")

        sub = row.row(align=True)
        sub.scale_x = 0.7  # Shrink to 30% width
        sub.prop(scene, "randomize_x", text="X", toggle=True)
        sub.prop(scene, "randomize_y", text="Y", toggle=True)
        sub.prop(scene, "randomize_z", text="Z", toggle=True)
        row.separator()
        row.label(text = f"{get_selected_axis_dimension(scene)} Dims.")


class SimplifiedDistributionSelector:

    @staticmethod
    def draw(layout, context):
        pass


def sync_distribution_handler(scene):
    """Synchronizes scene.available_distributions with actual bpy.data.node_groups."""

    # Get all actual DistributionNodeTree instances
    actual_trees = [
        tree for tree in bpy.data.node_groups
        if tree.bl_idname == "DistributionNodeTree"
    ]
    UniqueLogger.quick_log(str(actual_trees))

    # Get names of existing items
    existing_names = {item.name for item in scene.available_distributions}
    actual_names = {tree.name for tree in actual_trees}

    # Remove items that no longer exist
    items_to_remove = []
    for idx, item in enumerate(scene.available_distributions):
        if item.name not in actual_names:
            items_to_remove.append(idx)

    for idx in reversed(items_to_remove):
        scene.available_distributions.remove(idx)

    # Add new items and update pointers
    for tree in actual_trees:
        if tree.name not in existing_names:
            item = scene.available_distributions.add()
            item.name = tree.name
            item.node_tree = tree
        else:
            for item in scene.available_distributions:
                if item.name == tree.name:
                    # Reconcile possible missing links
                    item.node_tree = tree
                    break
    if scene.selected_distribution_index >= len(scene.available_distributions):
        scene.selected_distribution_index = max(0, len(scene.available_distributions) - 1)


class NodeDistributionSelector:

    @staticmethod
    def draw(layout, context):
        scene = context.scene

        layout.prop(scene, "use_distribution_tree")

        # List
        if scene.use_distribution_tree:

            box = layout.box()
            box.label(text="Saved Distributions")

            row = box.row()

            row.template_list(
                "DistributionTreeList",
                "distribution_trees",
                scene, "available_distributions",  # Will populate this
                scene, "selected_distribution_index"
            )

            # Add/Remove buttons
            col = row.column()
            col.operator("randomizer.add_distribution", icon='ADD', text='')
            col.operator("randomizer.remove_distribution", icon='REMOVE', text='')

            if len(scene.available_distributions) == 0:
                return
            # Error message space
            if scene.distribution_dimension_error:
                box.label(text="Dimension mismatch", icon='ERROR')
                box.label(text=scene.distribution_dimension_error)
            else:
                box.label(text="Valid distribution", icon='CHECKMARK')
        else:
            layout.label(text="Hello", icon='ERROR')

def get_selected_axis_dimension(scene):
    is_x = 1 if scene.randomize_x else 0
    is_y = 1 if scene.randomize_y else 0
    is_z = 1 if scene.randomize_z else 0
    return is_x + is_y + is_z

@OperationRegistry.register
class RandomizeScaleOperation(PipelineOperation):

    operation_type = PipeNames.SCALE.value

    def get_default_config(self):
        return {"seed": 0, "intensity": 0.1}

    def draw_editor(self, layout, context):
        AxisTarget.draw(layout, context)
        NodeDistributionSelector.draw(layout, context)

    def execute(self, scene, objects):
        # Your logic
        pass


operation_properties = {
    "use_distribution_tree": BoolProperty(
        name="Use advanced Distribution Editor nodes",
        default=False
    ),
    "selected_distribution_index": IntProperty(default=0),
    "distribution_dimension_error": StringProperty(default=""),
     "randomize_x": BoolProperty(default=True),
     "randomize_y": BoolProperty(default=True),
    "randomize_z": BoolProperty(default=True)
}
