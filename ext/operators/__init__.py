from .graphical_ops import (OpenDistributionOperator,
                           PipeUpOperator, PipeDownOperator, ChangePipelineViewerTabOperator)
from .io_ops import (ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator)
from .pipeline_ops import (EditPipeOperator, PipeAddOperator, MenuOperator, PipeRemoveOperator,
                           CaptureObjectsOperator, CaptureTextureOperator, CaptureObjectPositionOperator,
                           PositionRemoveOperator, PositionAddOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator,
                           CaptureDistributionValueNode, CaptureAndModifyNodeProperties)
from .distribution_ops import (AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator,
                               RemoveImagePathOperator)

operators = (

    #
    OpenDistributionOperator, PipeUpOperator, PipeDownOperator,
    ChangePipelineViewerTabOperator,

    #
    ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator,

    #
    EditPipeOperator, MenuOperator, PipeAddOperator, PipeRemoveOperator, CaptureObjectsOperator, CaptureTextureOperator,
    PositionRemoveOperator, PositionAddOperator, CaptureObjectPositionOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator,
    CaptureAndModifyNodeProperties, CaptureDistributionValueNode,
    #
    AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator, RemoveImagePathOperator

)
