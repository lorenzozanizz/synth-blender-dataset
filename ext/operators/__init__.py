from .graphical_ops import (OpenDistributionOperator,
                           PipeUpOperator, PipeDownOperator, ChangePipelineViewerTabOperator, AddFolderOperator)
from .io_ops import (ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator)
from .pipeline_ops import (EditPipeOperator, PipeAddOperator, MenuOperator, PipeRemoveOperator,
                           CaptureObjectsOperator, CaptureTextureOperator, CaptureObjectPositionOperator,
                           PositionRemoveOperator, PositionAddOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator,
                           CaptureValueNode, CaptureAndModifyNodeProperties, SavePipeOperator, ScanPipelineOperator,
                           IntoFolderOperator)
from .distribution_ops import (AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator,
                               RemoveImagePathOperator)
from .core_ops import GenerateOperator
from .labeling_ops import (AddLabelRuleOperator, RemoveLabelRuleOperator, AddLabelClassOperator, RemoveObjectLabelOperator,
                           AddObjectLabelOperator, RemoveLabelClassOperator)

operators = (

    #
    OpenDistributionOperator, PipeUpOperator, PipeDownOperator,
    ChangePipelineViewerTabOperator, AddFolderOperator,

    #
    ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator,

    #
    EditPipeOperator, MenuOperator, PipeAddOperator, PipeRemoveOperator, CaptureObjectsOperator, CaptureTextureOperator,
    PositionRemoveOperator, PositionAddOperator, CaptureObjectPositionOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator,
    CaptureAndModifyNodeProperties, CaptureValueNode, SavePipeOperator,  ScanPipelineOperator, IntoFolderOperator,
    #
    AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator, RemoveImagePathOperator,

    GenerateOperator,

    AddLabelRuleOperator, RemoveLabelRuleOperator, AddLabelClassOperator, RemoveObjectLabelOperator,
                           AddObjectLabelOperator, RemoveLabelClassOperator

)
