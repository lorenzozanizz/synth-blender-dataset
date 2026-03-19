from ..constants import DISTRO_EDITOR_NAME

from bpy.types import Node, NodeTree, NodeSocket
from nodeitems_utils import NodeCategory

from bpy.props import StringProperty, EnumProperty, FloatProperty, IntProperty


class DistributionSocket(NodeSocket):
    bl_idname = 'DistributionSocket'
    bl_label = 'Distribution'

    def draw_color(self, context, node):
        return (1.0, 0.8, 0.0, 1.0)

    def  draw(self, context, layout, node, text):
        pass


class DistributionNodeTree(NodeTree):
    bl_idname = "DistributionNodeTree"
    bl_label = 'Distribution Editor'
    bl_icon = 'NODETREE'


class DistributionRootNode(Node):
    bl_idname = "DistributionRootNode"
    bl_label = "Root"
    bl_icon = "NODETREE"

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.inputs.new("DistributionSocket", "Out")


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


class DistributionSelectorNode(Node):
    bl_idname = 'DistributionSelectorNode'
    bl_label = 'Selector'
    bl_icon = 'NODETREE'

    num_inputs: IntProperty(name="Fan in", default=2) # type: ignore

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'DistributionNodeTree'

    def init(self, context):
        self.outputs.new('DistributionSocket', 'Out')
        self.inputs.new('DistributionSocket', 'One')
        self.inputs.new('DistributionSocket', 'Two')

    def draw_buttons(self, context, layout):
        pass


class DistributionContinuousNode(Node):
    bl_idname = 'DistributionContinuousNode'
    bl_label = 'Continuous'
    bl_icon = 'NODETREE'

    dist_type: EnumProperty(
        items=[('NORMAL', 'Normal', ''), ('UNIFORM', 'Uniform', '')])
    mean: FloatProperty(default=0.5)
    sigma: FloatProperty(default=0.2)

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

    values: StringProperty(default='1,2,3')

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

