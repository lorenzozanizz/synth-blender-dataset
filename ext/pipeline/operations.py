"""



"""

from .data import PipeNames
from .registry import OperationRegistry
from ..utils.logger import UniqueLogger
from ..distribution.computation import ONE_D_DISTRIBUTIONS, UPPER_D_DISTRIBUTIONS, Distribution

from abc import ABC, abstractmethod
from typing import Tuple

from bpy.props import BoolProperty, IntProperty, StringProperty, EnumProperty, FloatVectorProperty, FloatProperty
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

def get_saved_distributions_names(_context):
    items = []
    for tree in bpy.data.node_groups:
        if tree.bl_idname == "DistributionNodeTree":
            items.append((tree.name, tree.name, ""))
    return items if items else [("NONE", "None", "")]


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
                    box.label(text=vector_names[extended_name])
                    box.prop(scene, extended_name, index=0, text="X")
                    box.prop(scene, extended_name, index=1, text="Y")

                    if num_dims == 3:
                        box.prop(scene, extended_name, index=2, text="Z")
                else:
                    box.prop(context.scene, extended_name)


        # SimplifiedDistributionSelector.dispatch_draw(str_value, box, context)

        row = box.row(align=True)
        row.prop(context.scene, "do_offset")
        row.prop(context.scene, "do_discretize")

        row = box.row(align=True)
        row.prop(context.scene, "do_clamp")
        row.prop(context.scene, "clamping_factors")


class MultiplePathList:

    @staticmethod
    def draw(layout, context):
        pass


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
            SimplifiedDistributionSelector.draw(layout, context)

@OperationRegistry.register
class RandomizeScaleOperation(PipelineOperation):

    operation_type = PipeNames.SCALE.value

    def get_default_config(self):
        return { }

    def draw_editor(self, layout, context):
        ObjectTargeter.draw(layout, context)
        layout.separator()
        AxisTarget.draw(layout, context)
        layout.separator()
        NodeDistributionSelector.draw(layout, context)

    def execute(self, scene, objects):
        # Your logic
        pass


def get_selected_axis_dimension(scene):
    """

    :param scene:
    :return:
    """
    is_x = 1 if scene.randomize_x else 0
    is_y = 1 if scene.randomize_y else 0
    is_z = 1 if scene.randomize_z else 0
    return is_x + is_y + is_z


operation_properties = {
    "use_distribution_tree": BoolProperty(
        name="Use advanced Distribution Editor nodes",
        default=False
    ),
    "selected_distribution_index": IntProperty(default=0),
    "distribution_dimension_error": StringProperty(default=""),
    "randomize_x": BoolProperty(default=True),
    "randomize_y": BoolProperty(default=True),
    "randomize_z": BoolProperty(default=True),
    "do_clamp": BoolProperty(
        name="Clamp",
        default=False,
        description="Start numbering at the last identified number in the destination folder"
    ),
    "clamping_factors": FloatVectorProperty(
        name="",
        size=2,
        default=(0.0, 0.0)
    ),
    "do_discretize": BoolProperty(
        name="Discretize values",
        default=False,
        description="Start numbering at the last identified number in the destination folder"
    ),
    "do_offset": BoolProperty(
        name="Offset mode",
        default=False,
        description="Consider the extracted values as offset to the current value."
    ),
    "simple_distribution_enum": EnumProperty(
        items=get_distribution_by_dims,
        name="Type"
    ),
    "targeted_objects_display": StringProperty(
        name="Targeted Objects",
        default="None"
    )
}


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

#
distribution_settings = {

    # Scalars
    'dist_min': FloatProperty(name="Minimum", default=0.0),
    'dist_max': FloatProperty(name="Maximum", default=1.0),
    'dist_mean': FloatProperty(name="Mean", default=0.5),
    'dist_std': FloatProperty(name="Standard Dev.", default=0.1),
    'dist_alpha': FloatProperty(name="Alpha", default=2.0),
    'dist_beta': FloatProperty(name="Beta", default=2.0),
    'dist_p': FloatProperty(name="P", default=0.5),
    'dist_n': IntProperty(name="N", default=10),
    'dist_variance': FloatProperty(name="Variance", default=1.0),

    # Vectors
    # ( we will use the first two entries of the vector for 2d distributions
    'dist_mean_vec': FloatVectorProperty(name="Mean", size=3, default=(0, 0, 0)),
    'dist_min_vec': FloatVectorProperty(name="Minimum Vector", size=3, default=(0, 0, 0)),
    'dist_max_vec': FloatVectorProperty(name="Maximum Vector", size=3, default=(1, 1, 1)),

    # To implement a matrix we may use 2d/3 float vector properties... i dont know
    # if its worth the hassle, for now keep that feature incomplete in this version!
    # 'dist_cov_matrix': ...

}

vector_names = {
    "dist_mean_vec": "Mean Vector",
    "dist_min_vec": "Minimum Vector",
    "dist_max_vec": "Maximum Vector"
}