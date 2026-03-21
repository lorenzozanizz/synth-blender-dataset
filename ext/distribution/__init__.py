from nodeitems_utils import NodeItem

from .nodes import *

node_categories = [
    #
    DistributionNodeCategory(
        "DISTRIBUTION_NODES", "Distribution Nodes", items=[
        NodeItem("DistributionSelectorNode"),
        NodeItem("DistributionDiscreteNode"),
        NodeItem("DistributionContinuousNode"),
        NodeItem("DistributionConstantNode"),
        NodeItem("DistributionRootNode"),

    ]),
]

#
classes = (
    DistributionRootNode, DistributionNodeTree, DistributionSelectorNode, DistributionContinuousNode,
    DistributionConstantNode, DistributionDiscreteNode, DistributionSocket
)