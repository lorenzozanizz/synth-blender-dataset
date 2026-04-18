from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Any, Dict, Callable, List, Union

from .raytracing import (get_visible_objects_from_camera, get_minimal_bounding_box_fast, estimate_visibility_3d,
                         union_bounding_boxes, compute_camera_space_boxes, compute_area_ratio)
from ..utils.timer import TimingContext
from .class_engine import ClassificationEngine


@dataclass
class Label:
    """Single entity annotation"""
    obj_or_entity_name: str
    class_id: int
    class_name: str

    bbox: tuple
    visibility: float


class LabelData:
    """Container for all annotations in a frame"""

    def __init__(self):
        self.data: Dict[str, Label] = dict()

    def __iter__(self):
        """ """
        return iter(self.data.values())

    def items(self):
        return self.data.items()

    def __getitem__(self, item: str):
        """ """
        return self.data.get(item)

    def add(self, new_lab: Label):
        """ """
        self.data[new_lab.obj_or_entity_name] = new_lab


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


class BoundingBoxExtractor(Extractor):
    """Encapsulates bbox extraction logic"""

    def __init__(self, context):
        self.ctx = context

        self.timings: Dict[str, float] = dict()
        self.visible_objects = dict()
        self.visible_entities = dict()
        self.estimated_visibility = dict()


    def extract(self,
        visible_objects: Dict[Any, List],
        classifier: ClassificationEngine,
        entity_data,
        camera,
        estimate_visibility: bool = True, **kwargs
    ) -> LabelData:
        """

        :param visible_objects:
        :param classifier:
        :param entity_data:
        :param camera:
        :param estimate_visibility:
        :param kwargs:
        :return:
        """
        ret_data = LabelData()

        with TimingContext(self.timings, 'labeling'):

            deps = self.ctx.evaluated_depsgraph_get()
            # Compute raw point clouds corresponding to each computed object.
            # now convert those point clouds into bound boxes.  (in-place)
            self.visible_objects = {obj:
                 get_minimal_bounding_box_fast(points) for obj, points in visible_objects.items()
            }
            # There are simple objects visibility, not entities.
            for obj, bbox in self.visible_objects.items():
                if estimate_visibility:
                    self.estimated_visibility[obj] = float(
                        estimate_visibility_3d(obj, camera, deps, self.ctx, self.ctx.scene.render, bbox)
                    )
                cls = classifier.map_obj(obj)
                ret_data.add(
                    Label(obj.name, cls.class_id, cls.name, bbox, visibility=self.estimated_visibility.get(obj))
                )
            # If required, estimate visibility (No entity mode)
            if not entity_data:
                return ret_data

            # Now we have to reconcile multi-object entities. Note the following thing: we have computed
            # bounding boxes for each smaller point cloud, so now we must join them together.
            # The operation of joining the clouds before computing the bboxes and computing the total
            # box is equivalent mathematically!
            visible_named_objects = {obj.name: (obj, bbox) for obj, bbox in self.visible_objects.items()}

            for entity_name, components in entity_data.items():

                visible_components = [k for k in components if visible_named_objects.get(k) is not None]
                # If no subcomponent is visible, leave early.
                if not visible_components:
                    continue
                bboxes = [visible_named_objects[name][1] for name in visible_components]
                if not bboxes:
                    continue
                total_visible_bbox = union_bounding_boxes(bboxes)
                # Note: we are not deleting sub objects, the user may want to differentiate them! e.g. hands in a body
                self.visible_entities[entity_name] = total_visible_bbox

                # The estimation of visibility is a bit more delicate, we have to unify also camera space 3d boxes.
                # (which are not the ones obtained empirically with raytracing, but are obtained with .bound_box instead)

                if estimate_visibility:
                    # We are only using visible objects (there may be more in the entity declaration)

                    camera_space_sub_boxes = compute_camera_space_boxes(
                        (visible_named_objects[name][0] for name in visible_components),
                         camera, deps, self.ctx, self.ctx.scene.render)

                    total_camera_bbox = union_bounding_boxes(camera_space_sub_boxes.values())
                    self.estimated_visibility[entity_name] = compute_area_ratio(total_visible_bbox, total_camera_bbox)

                cls = classifier.map_obj(obj)
                ret_data.add(
                    Label(entity_name, cls.class_id, cls.name, bbox, visibility=self.estimated_visibility.get(entity_name))
                )

        return ret_data

    def get_estimated_visibility(self) -> Dict[Union[str, Any], float]:
        """ Get the estimated visibility for entities and objects """
        return self.estimated_visibility

    def get_visible_entities(self):
        return self.visible_entities.keys()

    def get_labeling_time(self) -> float:
        """ Get the time it took to compute the boxes and the visible objects """
        return self.timings['labeling']

    def get_visible_objects(self) -> Iterable[Any]:
        """ Get the visible objects """
        return self.visible_objects.keys()

    def map_boxes(self, conv_func: Callable = None) -> Iterable[Any]:
        """ Get the camera centered bounding boxes """
        if not conv_func:
            return self.visible_objects.values()
        else:
            return (conv_func(bbox) for bbox in self.visible_objects.values())

    def get_bbox_objects(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        return self.visible_objects

    def get_bbox_entities(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        return self.visible_entities


class BoundingBoxExtractor2:
    """Encapsulates bbox extraction logic"""

    def __init__(self, context):
        self.ctx = context

        self.timings: Dict[str, float] = dict()
        self.visible_objects = dict()
        self.visible_entities = dict()
        self.estimated_visibility = dict()

    def extract(self, camera, entity_data: Dict[str, List[str]] = None, estimate_visibility: bool = True, ray_casting_ratio: float = 0.5):
        """

        :return:
        """
        res_x = int(self.ctx.scene.render.resolution_x * ray_casting_ratio)
        res_y = int(self.ctx.scene.render.resolution_y * ray_casting_ratio)

        with TimingContext(self.timings, 'labeling'):

            deps = self.ctx.evaluated_depsgraph_get()
            # Compute raw point clouds corresponding to each computed object.
            self.visible_objects = get_visible_objects_from_camera(
                self.ctx.scene, deps, camera,
                resolution_x=res_x, resolution_y=res_y, compute_mapping=True)
            # now convert those point clouds into bound boxes.  (in-place)
            self.visible_objects = {obj:
                 get_minimal_bounding_box_fast(points) for obj, points in self.visible_objects.items()
            }
            # There are simple objects visibility, not entities.
            if estimate_visibility:
                for obj, bbox in self.visible_objects.items():
                    self.estimated_visibility[obj] = float(
                        estimate_visibility_3d(obj, camera, deps, self.ctx, self.ctx.scene.render, bbox)
                    )
            # If required, estimate visibility (No entity mode)
            if not entity_data:
                return

            # Now we have to reconcile multi-object entities. Note the following thing: we have computed
            # bounding boxes for each smaller point cloud, so now we must join them together.
            # The operation of joining the clouds before computing the bboxes and computing the total
            # box is equivalent mathematically!
            visible_named_objects = {obj.name: (obj, bbox) for obj, bbox in self.visible_objects.items()}

            for entity_name, components in entity_data.items():

                visible_components = [k for k in components if visible_named_objects.get(k) is not None]
                # If no subcomponent is visible, leave early.
                if not visible_components:
                    continue
                bboxes = [visible_named_objects[name][1] for name in visible_components]
                if not bboxes:
                    continue
                total_visible_bbox = union_bounding_boxes(bboxes)
                # Note: we are not deleting sub objects, the user may want to differentiate them! e.g. hands in a body
                self.visible_entities[entity_name] = total_visible_bbox

                # The estimation of visibility is a bit more delicate, we have to unify also camera space 3d boxes.
                # (which are not the ones obtained empirically with raytracing, but are obtained with .bound_box instead)

                if estimate_visibility:
                    # We are only using visible objects (there may be more in the entity declaration)

                    camera_space_sub_boxes = compute_camera_space_boxes(
                        (visible_named_objects[name][0] for name in visible_components),
                         camera, deps, self.ctx, self.ctx.scene.render)

                    total_camera_bbox = union_bounding_boxes(camera_space_sub_boxes.values())
                    self.estimated_visibility[entity_name] = compute_area_ratio(total_visible_bbox, total_camera_bbox)

    def get_estimated_visibility(self) -> Dict[Union[str, Any], float]:
        """ Get the estimated visibility for entities and objects """
        return self.estimated_visibility

    def get_labeling_time(self) -> float:
        """ Get the time it took to compute the boxes and the visible objects """
        return self.timings['labeling']

    def get_visible_objects(self) -> Iterable[Any]:
        """ Get the visible objects """
        return self.visible_objects.keys()

    def map_boxes(self, conv_func: Callable = None) -> Iterable[Any]:
        """ Get the camera centered bounding boxes """
        if not conv_func:
            return self.visible_objects.values()
        else:
            return (conv_func(bbox) for bbox in self.visible_objects.values())

    def get_polygon_objects(self) -> Dict:
        pass

    def get_polygon_entity(self) -> Dict:
        pass

    def get_bbox_objects(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        return self.visible_objects

    def get_bbox_entities(self) -> Dict:
        """ Get the mappings from object to bounding boxes """
        return self.visible_entities


class PolygonExtractor:

    pass
