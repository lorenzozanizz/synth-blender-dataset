from .graphical_ops import (OpenDistributionOperator,
                           PipeUpOperator, PipeDownOperator, ChangePipelineViewerTabOperator)
from .io_ops import (ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator)
from .pipeline_ops import (EditPipeOperator, PipeAddOperator, MenuOperator, PipeRemoveOperator, CaptureObjectsOperator, CaptureMaterialOperator)
from .distribution_ops import AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator, RemoveImagePathOperator

operators = (

    #
    OpenDistributionOperator, PipeUpOperator, PipeDownOperator,
    ChangePipelineViewerTabOperator,

    #
    ApplyLogPathOperator, OpenLogsOperator, SavePipelineAsOperator, LoadPipelineOperator,

    #
    EditPipeOperator, MenuOperator, PipeAddOperator, PipeRemoveOperator, CaptureObjectsOperator, CaptureMaterialOperator,

    #
    AddDistributionOperator, RemoveDistributionOperator, AddImagePathOperator, RemoveImagePathOperator

)
