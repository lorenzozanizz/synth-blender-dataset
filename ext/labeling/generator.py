
from .bpy_properties import LabelClass
from .ray_casting import (compute_polygon_area, compute_bbox_area, get_minimal_bounding_box_fast,
                          estimate_visibility_3d, simplify_by_angle,
                          union_bounding_boxes, compute_camera_space_boxes, compute_area_ratio, compute_convex_hull)
from .class_engine import ClassificationEngine

from ..utils.timer import TimingContext

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Any, Dict, Callable, List, Union, Literal

@dataclass
class Label:
    """ Single entity annotation """

    obj_or_entity_name: str
    cls: Union[None, LabelClass]

    # The annotation data — could be any shape
    geometry: Union[
        tuple,  # bbox: (x, y, w, h)
        list[tuple],  # polygon: [(x1,y1), (x2,y2), ...]
        dict  # flexible structure
    ]

    annotation_type: Literal["bbox", "polygon"]  # "bbox", "polygon", "depth"

    # Whether a label belongs to a single object or to a composite multi-mesh entity
    is_entity: bool
    visibility: float = 0.0


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

        with (TimingContext(self.timings, 'labeling')):

            deps = self.ctx.evaluated_depsgraph_get()
            # Compute raw point clouds corresponding to each computed object.
            # now convert those point clouds into bound boxes.  (in-place)
            self.visible_objects = {obj:
                 get_minimal_bounding_box_fast(points) for obj, points in visible_objects.items()
            }
            # There are simple objects visibility, not entities.
            for obj, bbox in self.visible_objects.items():
                cls = classifier.map_obj(obj)
                if not cls:
                    continue

                if estimate_visibility:
                    self.estimated_visibility[obj] = float(
                        estimate_visibility_3d(
                            obj, camera, deps, self.ctx, self.ctx.scene.render, bbox, area_func=compute_bbox_area)
                    )
                ret_data.add(
                    Label(obj.name, cls,
                          geometry=bbox, visibility=self.estimated_visibility.get(obj), annotation_type="bbox",
                          is_entity=False)
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

                cls = classifier.map_entity(entity_name)
                if not cls:
                    continue

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
                    self.estimated_visibility[entity_name] = compute_area_ratio(
                            total_visible_bbox, total_camera_bbox,
                           area_func_1=compute_bbox_area, area_func_2=compute_bbox_area)

                ret_data.add(
                    Label(entity_name, cls,
                          geometry=bbox, visibility=self.estimated_visibility.get(entity_name), annotation_type="bbox",
                          is_entity=True)
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


class PolygonExtractor:

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
        estimate_visibility: bool = True, merge_angle: float = 3.0
    ) -> LabelData:
        """

        :param merge_angle:
        :param visible_objects:
        :param classifier:
        :param entity_data:
        :param camera:
        :param estimate_visibility:
        :param kwargs:
        :return:
        """
        ret_data = LabelData()

        with (TimingContext(self.timings, 'labeling')):

            deps = self.ctx.evaluated_depsgraph_get()
            # Compute raw point clouds corresponding to each computed object.
            # We cannot convert them into bounding boxes because computing the
            # union of polygons is non-trivial
            self.visible_objects = visible_objects

            for obj, point_cloud in self.visible_objects.items():
                cls = classifier.map_obj(obj)
                if not cls:
                    continue
                # If required, estimate visibility (No entity mode)
                convex_hull = compute_convex_hull(point_cloud, merge=False)
                if merge_angle:
                    convex_hull = simplify_by_angle(convex_hull, merge_angle)
                if estimate_visibility:
                    self.estimated_visibility[obj] = float(
                        estimate_visibility_3d(
                            obj, camera, deps, self.ctx, self.ctx.scene.render, convex_hull, area_func=compute_polygon_area)
                    )
                ret_data.add(
                    Label(obj.name, cls,
                          geometry=convex_hull, visibility=self.estimated_visibility.get(obj), annotation_type="polygon",
                          is_entity=False)
                )
            if not entity_data:
                return ret_data

            # Now we have to reconcile multi-object entities. As said before, we cannot just compute the unions
            # of convex hulls because that is not trivial to do. Instead, we provide "Joint" iterators over
            # cloud points ( to avoid computing the union of the sets ) to compute the resulting convex hull
            visible_named_objects = {obj.name: (obj, cloud) for obj, cloud in self.visible_objects.items()}

            for entity_name, components in entity_data.items():

                cls = classifier.map_entity(entity_name)
                if not cls:
                    continue

                visible_components = [k for k in components if visible_named_objects.get(k) is not None]
                # If no subcomponent is visible, leave early.
                if not visible_components:
                    continue
                point_clouds = [visible_named_objects[name][1] for name in visible_components]
                if not point_clouds:
                    continue

                total_convex_hull = compute_convex_hull(point_clouds, merge=True)
                if merge_angle:
                    convex_hull = simplify_by_angle(convex_hull, merge_angle)
                # Note: we are not deleting sub objects, the user may want to differentiate them! e.g. hands in a body
                self.visible_entities[entity_name] = total_convex_hull

                # The estimation of visibility is a bit more delicate, we have to unify also camera space 3d boxes.
                # NOTE that this is intrinsically ill-defined: we are comparing visible polygons with the bounding box.
                # If a more accurate estimate is required, a 3d convex hull would need to be projected etc... not easy!

                if estimate_visibility:
                    # We are only using visible objects (there may be more in the entity declaration)

                    camera_space_sub_boxes = compute_camera_space_boxes(
                        (visible_named_objects[name][0] for name in visible_components),
                         camera, deps, self.ctx, self.ctx.scene.render)

                    total_camera_bbox = union_bounding_boxes(camera_space_sub_boxes.values())
                    self.estimated_visibility[entity_name] = compute_area_ratio(
                        total_convex_hull, total_camera_bbox,
                        area_func_1=compute_polygon_area, area_func_2=compute_bbox_area)

                ret_data.add(
                    Label(entity_name, cls,
                          geometry=total_convex_hull,
                          visibility=self.estimated_visibility.get(entity_name), annotation_type="polygon",
                          is_entity=True)
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
