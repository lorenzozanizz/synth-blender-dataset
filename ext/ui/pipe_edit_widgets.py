from ..operators.names import Labels
from ..distribution.computation import ONE_D_DISTRIBUTIONS, UPPER_D_DISTRIBUTIONS, Distribution
from ..distribution.nodes import get_tree_dimensionality
from ..utils.logger import UniqueLogger

from abc import ABC, abstractmethod
from typing import Tuple

import bpy
from bpy.props import StringProperty, FloatVectorProperty, PointerProperty, BoolProperty
from bpy.types import UIList, PropertyGroup, Material


class ImagePath(PropertyGroup):
    """Single image file path"""
    path: StringProperty(name="Path", subtype='FILE_PATH')  # type: ignore


class PathsUIList(UIList):
    """UIList for individual image paths"""

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.scale_x = 0.3
        sub.label(text=f"{index + 1}")
        row.label(text=item.path, icon='IMAGE_DATA')


class ObjectPosition(PropertyGroup):
    """Single image file path"""
    pos: FloatVectorProperty(name="Position", size=3, default=(0, 0, 0))  # type: ignore


class PositionsUIList(UIList):
    """UIList for individual image paths"""

    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        row = layout.row(align=True)
        sub = row.row(align=True)
        sub.scale_x = 0.3
        sub.label(text=f"{index + 1}")
        row.prop(item, "pos", text="Position", emboss=False)


class MaterialListItem(PropertyGroup):
    """Single material in list"""
    material: PointerProperty(  # type: ignore
        type=Material,
        name="Material"
    )


class MaterialUIList(UIList):
    """UIList for materials"""

    @staticmethod
    def draw_item(self, _context, layout, _data, item, _icon, _active_data, _active_propname, index):
        mat = item.material

        if mat:
            row = layout.row(align=True)
            sub = row.row()
            sub.label(text=f"{index + 1}")
            sub.scale_x = 0.3
            row.label(text=mat.name, icon='MATERIAL')
        else:
            row = layout.row()
            row.label(text="(Empty)")


def get_selected_axis_dimension(scene):
    """

    :param scene:
    :return:
    """
    is_x = 1 if scene.randomize_x else 0
    is_y = 1 if scene.randomize_y else 0
    is_z = 1 if scene.randomize_z else 0
    return is_x + is_y + is_z

def force_axis_dimension(scene, dim):
    if dim == 0:
        scene.randomize_x = False
        scene.randomize_y = False
        scene.randomize_z = False
    elif dim == 1:
        scene.randomize_x = True
        scene.randomize_y = False
        scene.randomize_z = False
    elif dim == 2:
        scene.randomize_x = True
        scene.randomize_y = True
        scene.randomize_z = False
    else:
        scene.randomize_x = True
        scene.randomize_y = True
        scene.randomize_z = True


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


class EditorWidget(ABC):

    @staticmethod
    @abstractmethod
    def draw(layout, context) -> None:
        """

        :param layout:
        :param context:
        :return:
        """
        pass

    @staticmethod
    @abstractmethod
    def extract_data(context) -> dict:
        """

        :return:
        """
        pass

#

class AxisTarget(EditorWidget):

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
        row.label(text=f"({get_selected_axis_dimension(scene)} Dims.)")

    @staticmethod
    def extract_data(context) -> dict:
        scene = context.scene
        return {
            "do_x": scene.randomize_x,
            "do_y": scene.randomize_y,
            "do_z": scene.randomize_z,
            "dims": get_selected_axis_dimension(context.scene),
        }

#

def get_distribution_by_dims(scene, _context) -> list[Tuple]:
    """Get distributions matching selected axes"""

    num_dims = get_selected_axis_dimension(scene)

    if num_dims == 1:
        return [(dist.name, dist.value.title(), "") for dist in ONE_D_DISTRIBUTIONS]
    elif num_dims >= 2:
        return [(dist.name, dist.value.title(), "") for dist in UPPER_D_DISTRIBUTIONS]
    else:
        return [('NONE', "None", "")]

#

class ObjectTargeter(EditorWidget):

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
        box.operator(Labels.CAPTURE_OBJECTS.value, text="Capture Selected", icon='EYEDROPPER')

    @staticmethod
    def extract_data(context) -> dict:
        pass

#

class ImageTextureTargeter(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

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
        box.operator(Labels.CAPTURE_TEXTURE_NODE.value, text="Capture Selected", icon='EYEDROPPER')

#

class PathListSelector(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

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
            col.operator(Labels.ADD_IMAGE_PATH_POOL.value, icon='ADD', text='')
            col.operator(Labels.REMOVE_IMAGE_PATH_POOL.value, icon='REMOVE', text='')


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

#

class NodeDistributionSelector(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

    @staticmethod
    def draw(layout, context, dim = None):
        """

        :param dim:
        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        layout.prop(scene, "use_distribution_tree")

        if dim is not None:
            force_axis_dimension(layout, dim)
        dimension = dim if dim is not None else get_selected_axis_dimension(scene)
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
            col.operator(Labels.ADD_DISTRIBUTION.value, icon='ADD', text='')
            col.operator(Labels.REMOVE_DISTRIBUTION.value, icon='REMOVE', text='')

            if len(scene.available_distributions) == 0:
                return
            # Error message space
            if scene.distribution_dimension_error:
                box.label(text="Dimension mismatch", icon='ERROR')
                box.label(text=scene.distribution_dimension_error)
            else:
                box.label(text="Valid distribution", icon='CHECKMARK')
        else:
            SimplifiedDistributionSelector.draw(layout, context, dim=dimension)

#

class SimplifiedDistributionSelector(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

    _distribution_map = {
        Distribution.UNIFORM.name: ['min', 'max'],
        Distribution.MULTIVARIATE_UNIFORM.name: ['min_vec', 'max_vec'],
        Distribution.BETA.name: ['alpha', 'beta', 'min', 'max'],
        Distribution.GEOMETRIC.name: ['p'],
        Distribution.BERNOULLI.name: ['p'],
        Distribution.BINOMIAL.name: ['n', 'p'],
        Distribution.GAUSSIAN.name: ['mean', 'std'],
        Distribution.MULTIVARIATE_GAUSSIAN.name: ['mean_vec', 'cov_matrix'],
        Distribution.MULTIVARIATE_ISOTROPIC_GAUSSIAN.name: ['mean_vec', 'variance'],
    }

    # This prefix is applied to all property names, used for clarity
    _name_prefix = "dist_"

    @staticmethod
    def draw(layout, context, dim=None):
        """

        :param dim:
        :param layout:
        :param context:
        :return:
        """
        scene = context.scene
        box = layout.box()
        box.label(text="Preset Distributions")
        box.prop(scene, "simple_distribution_enum")

        SimplifiedDistributionSelector.draw_for(
            box, context,
            dist_name=(scene.simple_distribution_enum or "").upper(),
            num_dims= dim if dim is not None else get_selected_axis_dimension(scene),
            show_cmds=True
        )

    @staticmethod
    def draw_for(layout, context, dist_name: str, label: str = None, num_dims: int = 1, show_cmds: bool = False):
        """

        :param label:
        :param layout:
        :param context:
        :param num_dims:
        :param dist_name:
        :param show_cmds:
        :return:
        """

        scene = context.scene

        if dist_name == "NONE":
            layout.label(text="No distribution.")
            return

        box = layout.box()
        if label and label != "":
            box.label(text=label)

        interested_properties = SimplifiedDistributionSelector._distribution_map[dist_name]

        # Vector properties need to change with dimension.
        for property_name in interested_properties:
            extended_name = SimplifiedDistributionSelector._name_prefix + property_name
            if "vec" in property_name:
                row = box.row(align=True)

                # These are used to visualize the distribution names properly
                vector_names = {
                    "dist_mean_vec": "Mean Vector",
                    "dist_min_vec": "Minimum Vector",
                    "dist_max_vec": "Maximum Vector"
                }

                row.label(text=vector_names[extended_name])
                row.prop(scene, extended_name, index=0, text="X")
                if num_dims >= 2:
                    row.prop(scene, extended_name, index=1, text="Y")
                if num_dims >= 3:
                    row.prop(scene, extended_name, index=2, text="Z")
            else:
                box.prop(context.scene, extended_name)
        if show_cmds:
            SimplifiedDistributionSelector._draw_options(box, context)

    @staticmethod
    def _draw_options(layout, context):
        """

        :param layout:
        :param context:
        :return:
        """
        row = layout.row(align=True)
        row.prop(context.scene, "do_offset")
        row.prop(context.scene, "do_discretize")

        row = layout.row(align=True)
        row.prop(context.scene, "do_clamp")
        row.prop(context.scene, "clamping_factors")

#

class PositionListSelector(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

    @staticmethod
    def draw(layout, context):
        scene = context.scene

        box = layout.box()
        box.label(text="Saved Positions")
        row = box.row()
        row.template_list(
            PositionsUIList.__name__,
            "selected_positions",
            scene, "position_collection",  # Will populate this
            scene, "selected_position_index"
        )

        # Add/Remove buttons
        col = row.column()
        col.operator(Labels.ADD_POSITION_POOL.value, icon='ADD', text='')
        col.operator(Labels.REMOVE_POSITION_POOL.value, icon='REMOVE', text='')
        col.operator(Labels.CAPTURE_OBJ_POSITION.value, icon='EYEDROPPER', text='')

#

class MaterialSelector(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

    @staticmethod
    def draw(layout, context):
        scene = context.scene

        # List
        layout.label(text="Select target materials:")
        row = layout.row()
        row.template_list(
            MaterialUIList.__name__,
            "material_list",
            scene, "material_list",
            scene, "material_list_index"
        )

        # +/- buttons
        col = row.column()
        col.operator(Labels.ADD_MATERIAL_POOL.value, icon='ADD', text='')
        col.operator(Labels.REMOVE_MATERIAL_POOL.value, icon='REMOVE', text='')

#

class PropertyTargeter(EditorWidget):

    @staticmethod
    def extract_data(context) -> dict:
        pass

    @staticmethod
    def draw(layout, context):
        scene = context.scene
        box = layout.box().row()
        box.label(text="Target:")
        box.label(text=scene.targeted_objects_display, icon='OBJECT_DATA')
        box.operator(Labels.CAPTURE_GENERAL_NODE.value, text="Capture Selected", icon='EYEDROPPER')

        selected_node_property = True
        if selected_node_property:
            pass

class ValueTargeter(EditorWidget):


    @staticmethod
    def draw(layout, context):
        scene = context.scene
        box = layout.box().row()
        box.label(text="Value Node:")
        box.label(text=scene.targeted_material_display, icon='OBJECT_DATA')
        box.operator(Labels.CAPTURE_VALUE_NODE, text="Capture Selected", icon='EYEDROPPER')

    @staticmethod
    def extract_data(context) -> dict:
        return { }
