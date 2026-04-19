from dataclasses import dataclass
from typing import Literal


@dataclass
class GenerationConfig:
    """

    """

    seed: int
    amount: int


@dataclass
class LabelExtractionConfig:
    """ """

    format: str
    write_labels: bool

    ray_casting_ratio: float = 0.1
    estimate_visibility: bool = True


@dataclass
class WritingConfig:

    from_last: bool
    save_path: str
    prefix: str
    folder_structure: Literal["yolo"] = "yolo"
    image_extension: str = ".png"
    split: str = "train"

@dataclass
class PreviewRenderConfig:
    """ A separate set of configurations options which only targe the rendered
    preview window and not the execution of the orchestrator pipeline (i.e. this
    only influences the way the preview is rendered) """

    show_visibility: bool = True
    show_obj_name: bool = True

    show_class_name_or_id: Literal["id", "none", "name"] = "id"

    show_timings: bool = True
    # If the default class is applied to a large number of objects, the user may
    # wish to disable it.
    ignore_default_class: bool = True

