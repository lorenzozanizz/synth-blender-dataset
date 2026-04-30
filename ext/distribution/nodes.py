"""




"""

from ..constants import DISTRO_EDITOR_NAME

from bpy.types import Node, NodeTree, NodeSocket
from nodeitems_utils import NodeCategory

from bpy.props import StringProperty, EnumProperty, FloatProperty, IntProperty


class DistributionSocket(NodeSocket):
    bl_idname = 'DistributionSocket'
    bl_label = 'Distribution'

    # Socket carries dimension info
    dimension: IntProperty(default=1, min=1, max=3)  # type: ignore

    def draw_color(self, context, node):
        if self.dimension == 1:
            return 1.0, 0.8, 0.0, 1.0  # Yellow for 1D
        elif self.dimension == 2:
            return 0.8, 1.0, 0.5, 1.0  # Light green for 2D
        else:
            return 0.5, 1.0, 0.8, 1.0  # Cyan for 3D

    def draw(self, context, layout, node, text):
        layout.label(text=f"{self.dimension}D")


class DistributionNodeTree(NodeTree):
    bl_idname = "DistributionNodeTree"
    bl_label = 'Distribution Editor'
    bl_icon = 'NODETREE'

class DistributionRootNode(Node):
    bl_idname = "DistributionRootNode"
    bl_label = "Root"
    bl_icon = "NODETREE"

    dimension: IntProperty(         # type: ignore
        name="Dimension",
        default=1,
        min=1,
        max=3,
        update=lambda self, context: self._update_socket_dimension()
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.inputs.new("DistributionSocket", "Out")
        self._update_socket_dimension()

    def _update_socket_dimension(self):
        if self.inputs:
            self.inputs[0].dimension = self.dimension

    def draw_buttons(self, context, layout):
        layout.prop(self, 'dimension', text='Dim')


class DistributionConstantNode(Node):
    bl_idname = "DistributionConstantNode"
    bl_label = "Constant"
    bl_icon = "NODETREE"

    value: FloatProperty(name="Value", default=1)  # type: ignore

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.outputs.new("DistributionSocket", "Out")
        # self.use_custom_color = True
        # self.color = (0.2, 0.5, 0.8)  # Blue RGB

    def draw_buttons(self, context, layout):
        layout.prop(self, 'value', text='Value')


class DistributionSelectorNode(Node):
    bl_idname = 'DistributionSelectorNode'
    bl_label = 'Selector'

    num_inputs: IntProperty(default=2, min=2, max=8)  # type: ignore
    weights_str: StringProperty(default='1.0, 1.0')  # type: ignore

    def init(self, context):
        self.outputs.new('DistributionSocket', 'Out')
        for i in range(self.num_inputs):
            self.inputs.new('DistributionSocket', f'In {i + 1}')

    def update(self):
        # Sync input count
        while len(self.inputs) < self.num_inputs:
            self.inputs.new('DistributionSocket', f'In {len(self.inputs) + 1}')
        while len(self.inputs) > self.num_inputs:
            self.inputs.remove(self.inputs[-1])

        # Output dimension = first input dimension
        if self.inputs and self.outputs:
            self.outputs[0].dimension = self.inputs[0].dimension

    def draw_buttons(self, context, layout):
        layout.prop(self, 'num_inputs', text='N. of inputs')
        layout.prop(self, 'weights_str', text='Weights')

class DistributionContinuousNode(Node):
    bl_idname = 'DistributionContinuousNode'
    bl_label = 'Continuous'
    bl_icon = 'NODETREE'

    dist_type: EnumProperty(                                            # type: ignore
        items=[('NORMAL', 'Normal', ''), ('UNIFORM', 'Uniform', '')])   # type: ignore
    mean: FloatProperty(default=0.5)                                    # type: ignore
    sigma: FloatProperty(default=0.2)                                   # type: ignore

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.outputs.new('DistributionSocket', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'dist_type', text='')


class DistributionDiscreteNode(Node):
    bl_idname = 'DistributionDiscreteNode'
    bl_label = 'Discrete'
    bl_icon = 'NODETREE'

    values: StringProperty(default='1,2,3')                     # type: ignore

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.outputs.new('DistributionSocket', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'values', text='')



class DistributionNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'DistributionNodeTree'


def get_tree_dimensionality(tree):
    return 1


class NodeDistributionSerializer:

    @staticmethod
    def serialize(node) -> dict:
        return {}