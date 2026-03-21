"""
"""

from ..constants import PipeNames
from ..utils.logger import UniqueLogger
from ..distribution.computation import ONE_D_DISTRIBUTIONS, UPPER_D_DISTRIBUTIONS, Distribution
from ..distribution.nodes import get_tree_dimensionality
from abc import ABC
from typing import Tuple

from bpy.types import UIList, PropertyGroup
from bpy.props import StringProperty
import bpy


class OperationDrawerRegistry:

    _drawers = {}

    @classmethod
    def register(cls, op_type: str):
        def decorator(drawer_cls):
            cls._drawers[op_type] = drawer_cls
            return drawer_cls
        return decorator

    @classmethod
    def get(cls, op_type: str):
        return cls._drawers.get(op_type)

    @classmethod
    def get_all_types(cls) -> list:
        """Get all available operation types."""
        return list(cls._drawers.keys())

class PipeDrawer(ABC):
    """Base class for all pipeline operations."""

    operation_type: str  # "Scale", "Rotation", etc

    @staticmethod
    def draw_editor(layout, context):
        """Draw this operation's editor UI."""
        pass

class ImagePath(PropertyGroup):
    """Single image file path"""
    path: StringProperty(name="Path", subtype='FILE_PATH')      # type: ignore


class PathsUIList(UIList):
    """UIList for individual image paths"""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.scale_x = 0.3
        sub.label(text=f"{index + 1}")
        row.label(text=item.path, icon='IMAGE_DATA')

def get_selected_axis_dimension(scene):
    """

    :param scene:
    :return:
    """
    is_x = 1 if scene.randomize_x else 0
    is_y = 1 if scene.randomize_y else 0
    is_z = 1 if scene.randomize_z else 0
    return is_x + is_y + is_z



class DistributionTreeList(UIList):

    def draw_item(self, _context, layout, _data, item, icon, active_data, active_propname, index):
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



class AxisTarget:

    @staticmethod
    def draw(layout, context):
        layout = layout
        scene = context.scene

        # 3 checkboxes in a row
        row = layout.row(align=True)
        row.label(text="Axis:")

        sub = row.row(align=True)
        sub.scale_x = 0.7  # Shrink to 30% width
        sub.prop(scene, "randomize_x", text="X", toggle=True)
        sub.prop(scene, "randomize_y", text="Y", toggle=True)
        sub.prop(scene, "randomize_z", text="Z", toggle=True)
        row.separator()
        row.label(text = f"({get_selected_axis_dimension(scene)} Dims.)")


def get_distribution_by_dims(scene, _context) -> list[Tuple]:
    """Get distributions matching selected axes"""

    num_dims = get_selected_axis_dimension(scene)

    if num_dims == 1:
        return [(dist.name, dist.value.title(), "") for dist in ONE_D_DISTRIBUTIONS]
    elif num_dims >= 2:
        return [(dist.name, dist.value.title(), "") for dist in UPPER_D_DISTRIBUTIONS]
    else:
        return [('NONE', "None", "")]


def get_all_distribution_trees():
    """Get all saved DistributionNodeTree instances."""
    return [tree for tree in bpy.data.node_groups
            if tree.bl_idname == "DistributionNodeTree"]

def get_saved_distributions_names(_context):
    items = []
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "DistributionNodeTree":
            items.append((tree.name, tree.name, ""))
    return items if items else [("NONE", "None", "")]


class ObjectTargeter:

    @staticmethod
    def draw(layout, context):
        """

        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        box = layout.box().row()
        box.label(text="Target:")
        box.label(text=scene.targeted_objects_display, icon='OBJECT_DATA')
        box.operator("randomizer.capture_objects", text="Capture Selected", icon='GREASEPENCIL')


class MaterialTargeter:

    @staticmethod
    def draw(layout, context):
        """

        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        box = layout.box().row()
        box.label(text="Material:")
        box.label(text=scene.targeted_material_display, icon='OBJECT_DATA')
        box.operator("randomizer.capture_material", text="Capture Selected", icon='GREASEPENCIL')


class PathListSelector:

    @staticmethod
    def draw(layout, context):
        scene = context.scene
        # Toggle button
        layout.prop(scene, "use_folder_mode", text="Use Folder Mode")

        if scene.use_folder_mode:
            box = layout.box()
            box.label(text="Folder Selection")
            box.prop(scene, "image_folder", text="")

        else:
            box = layout.box()
            box.label(text="Individual Files")

            row = box.row()
            row.template_list(
                PathsUIList.__name__,
                "image_paths_list",
                scene, "image_paths",
                scene, "selected_image_path_index"
            )

            # +/- buttons
            col = row.column()
            col.operator("randomizer.add_image_path", icon='ADD', text='')
            col.operator("randomizer.remove_image_path", icon='REMOVE', text='')

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
        """

        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        layout.prop(scene, "use_distribution_tree")

        if scene.use_distribution_tree:
            box = layout.box()
            box.label(text="Saved Distributions")
            row = box.row()
            row.template_list(
                DistributionTreeList.__name__,
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
            SimplifiedDistributionSelector.draw(layout, context)

class SimplifiedDistributionSelector:

    # This prefix is applied to all property names, used for clarity
    _name_prefix = "dist_"

    @staticmethod
    def draw(layout, context):
        """

        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        box = layout.box()
        box.label(text="Preset Distributions")
        box.prop(scene, "simple_distribution_enum")

        value = scene.simple_distribution_enum.upper()
        num_dims = get_selected_axis_dimension(scene)
        if value != "NONE":
            interested_properties = DISTRIBUTION_PROPERTIES_MAP[value]

            # Vector properties need to change with dimension.
            for property_name in interested_properties:
                extended_name = SimplifiedDistributionSelector._name_prefix + property_name
                if "vec" in property_name:
                    row = box.row(align=True)
                    row.label(text=vector_names[extended_name])
                    row.prop(scene, extended_name, index=0, text="X")
                    row.prop(scene, extended_name, index=1, text="Y")

                    if num_dims == 3:
                        row.prop(scene, extended_name, index=2, text="Z")
                else:
                    box.prop(context.scene, extended_name)


        # SimplifiedDistributionSelector.dispatch_draw(str_value, box, context)

        row = box.row(align=True)
        row.prop(context.scene, "do_offset")
        row.prop(context.scene, "do_discretize")

        row = box.row(align=True)
        row.prop(context.scene, "do_clamp")
        row.prop(context.scene, "clamping_factors")


class SimplePropertyDrawer(PipeDrawer):

    @staticmethod
    def draw_editor(layout, context):
        """

        :return:
        """
        ObjectTargeter.draw(layout, context)
        layout.separator()
        AxisTarget.draw(layout, context)
        layout.separator()
        NodeDistributionSelector.draw(layout, context)

# The following operations

@OperationDrawerRegistry.register(PipeNames.SCALE.value)
class RandomizeScaleOperation(SimplePropertyDrawer):
    pass

@OperationDrawerRegistry.register(PipeNames.ROTATION.value)
class RandomizeRotationOperation(SimplePropertyDrawer):
    pass

@OperationDrawerRegistry.register(PipeNames.POSITION.value)
class RandomizeRotationOperation(SimplePropertyDrawer):
    pass

@OperationDrawerRegistry.register(PipeNames.TEXTURE.value)
class RandomizeTextureOperation(PipeDrawer):

    @staticmethod
    def draw_editor(layout, context):
        """

        :return:
        """
        MaterialTargeter.draw(layout, context)
        layout.separator()
        PathListSelector.draw(layout, context)


DISTRIBUTION_PROPERTIES_MAP = {
    Distribution.UNIFORM.name: ['min', 'max'],
    Distribution.MULTIVARIATE_UNIFORM.name: ['min_vec', 'max_vec'],
    Distribution.BETA.name: ['alpha', 'beta', 'min', 'max'],
    Distribution.GEOMETRIC.name: ['p'],
    Distribution.BINOMIAL.name: ['n', 'p'],
    Distribution.GAUSSIAN.name: ['mean', 'std'],
    Distribution.MULTIVARIATE_GAUSSIAN.name: ['mean_vec', 'cov_matrix'],
    Distribution.MULTIVARIATE_ISOTROPIC_GAUSSIAN.name: ['mean_vec', 'variance'],
}

vector_names = {
    "dist_mean_vec": "Mean Vector",
    "dist_min_vec": "Minimum Vector",
    "dist_max_vec": "Maximum Vector"
}
