from .graphical_ops import (OpenDistributionOperator,
                           PipeUpOperator, PipeDownOperator, ChangePipelineViewerTabOperator)
from .io_ops import (ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator)
from .pipeline_ops import (EditPipeOperator, PipeAddOperator, MenuOperator, PipeRemoveOperator,
                           CaptureObjectsOperator, CaptureMaterialOperator, CaptureObjectPositionOperator,
                           PositionRemoveOperator, PositionAddOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator)
from .distribution_ops import (AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator,
                               RemoveImagePathOperator)

operators = (

    #
    OpenDistributionOperator, PipeUpOperator, PipeDownOperator,
    ChangePipelineViewerTabOperator,

    #
    ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator,

    #
    EditPipeOperator, MenuOperator, PipeAddOperator, PipeRemoveOperator, CaptureObjectsOperator, CaptureMaterialOperator,
    PositionRemoveOperator, PositionAddOperator, CaptureObjectPositionOperator, AddMaterialToListOperator, RemoveMaterialFromListOperator,
    #
    AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator, RemoveImagePathOperator

)
