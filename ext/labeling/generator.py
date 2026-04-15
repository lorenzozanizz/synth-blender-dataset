from ..utils.logger import UniqueLogger
from ..utils.timer import TimingContext
from .raytracing import (get_visible_objects_from_camera, get_minimal_bounding_box_fast, estimate_visibility_3d,
                         union_bounding_boxes, compute_camera_space_boxes, compute_area_ratio)

from typing import Iterable, Any, Dict, Callable, List, Union


class LabelingManager:

    def __init__(self, folder, fmt: str):
        self.format = fmt
        self.folder = folder

    def create_label_directory(self) -> None:
        pass


class BoundingBoxExtractor:
    """Encapsulates bbox extraction logic"""

    def __init__(self, context):
        self.ctx = context

        self.timings: Dict[str, float] = dict()
        self.visible_objects = dict()
        self.visible_entities = dict()
        self.estimated_visibility = dict()

    def extract(self, camera, entity_data: Dict[str, List[str]] = None, ray_casting_ratio: float = 0.5,
                estimate_visibility: bool = True):
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
                    UniqueLogger.quick_log("Examining" + obj.name)
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

                visible_components = (v for k in components if (v := visible_named_objects.get(k)) is not None)
                # If no subcomponent is visible, leave early.
                if not visible_components:
                    continue
                bboxes = (self.visible_objects[name] for name in visible_components)
                total_visible_bbox = union_bounding_boxes(bboxes)
                # Note: we are not deleting sub objects, the user may want to differentiate them! e.g. hands in a body
                self.visible_entities[entity_name] = total_visible_bbox

                # The estimation of visibility is a bit more delicate, we have to unify also camera space 3d boxes.
                # (which are not the ones obtained empirically with raytracing, but are obtained with .bound_box instead)

                if estimate_visibility:
                    # We are only using visible objects (there may be more in the entity declaration)
                    camera_space_sub_boxes = compute_camera_space_boxes(visible_components,
                         camera, deps, self.ctx, self.ctx.scene.render)
                    total_camera_bbox = union_bounding_boxes(camera_space_sub_boxes)
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

    def get_bounding_boxes_objects(self, conv_func: Callable = None) -> Iterable[Any]:
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
