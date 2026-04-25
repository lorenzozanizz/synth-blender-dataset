from abc import abstractmethod, ABCMeta
from typing import Any, Dict, Callable
from collections.abc import Iterable

from .data_structure import *

class Extractor(metaclass=ABCMeta):

    @abstractmethod
    def extract(self,             visible_objects,
            classifier,
            entity_data,
            camera,
                estimate_visibility: bool = True, **kwargs) -> LabelData:
        """

        :return:
        """
        pass

    @abstractmethod
    def get_estimated_visibility(self) -> dict[ str | Any, float]:
        """ Get the estimated visibility for entities and objects """
        pass

    @abstractmethod
    def get_visible_entities(self):
        pass

    def get_labeling_time(self) -> float:
        """ Get the time it took to compute the boxes and the visible objects """
        pass

    def get_visible_objects(self) -> Iterable[Any]:
        """ Get the visible objects """
        pass

    def map_boxes(self, conv_func: Callable = None) -> Iterable[Any]:
        """ Get the camera centered bounding boxes """
        pass

    def get_bbox_objects(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        pass

    def get_bbox_entities(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        pass

