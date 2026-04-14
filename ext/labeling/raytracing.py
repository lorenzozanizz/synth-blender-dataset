"""


[ References ]
https://github.com/DLR-RM/BlenderProc/blob/main/blenderproc/python/camera/CameraValidation.py
https://blender.stackexchange.com/questions/269014/list-all-occluded-objects-from-camera

"""
from ..utils.logger import UniqueLogger
from ..utils.images import convex_hull


try:
    from numpy import linspace
except ImportError:
    def linspace(start, stop, num):
        """Simple fallback for np.linspace, using a generator expression to avoid
        constructing a useless large array."""
        step = (stop - start) / (num - 1) if num > 1 else 0
        return (start + step * i for i in range(num))

from collections import defaultdict
from math import sqrt, tan
from mathutils import Vector, Matrix
from typing import Any, Set, Dict, Tuple, List, Union

import bpy


def get_visible_objects_from_camera(scene, depsgraph,
                                    camera,
                                    resolution_x: int = 4, resolution_y: int = 4,
                                    num_ray: int = 0,
                                    compute_bounding_boxes: bool = False,
                                    compute_convex_hull: bool = False
    ) -> Union[Set[Any], Dict[Any, Tuple[int, int, int, int]]]:
    """

    :param scene:
    :param depsgraph:
    :param camera:
    :param resolution_x:
    :param resolution_y:
    :param num_ray:
    :param compute_convex_hull:
    :param compute_bounding_boxes:
    :return:
    """
    # Get vectors which define view frustum of camera
    top_right, _, bottom_left, top_left = camera.data.view_frame(scene=scene)

    camera_quaternion = camera.matrix_world.to_quaternion()
    camera_translation = camera.matrix_world.translation

    if num_ray:
        # We know that the numbers of ray shot is len(x_range)*len(y_range) so we must have
        # assuming resolution_x = resolution_y
        # ( top_right[0]-top_left[0] / resolution_x ) * (bottom_left[1]-top_left[1]) / resolution_x) = num_rays
        # hence we have
        resolution_x = resolution_y = min(30, int(sqrt(
            (top_right[0] - top_left[0]) * (bottom_left[1] - top_left[1]) / num_ray)))

    # Get iteration range for both the x and y axes, sampled based on the resolution
    UniqueLogger.quick_log(f"resolution_x: {resolution_x}")
    UniqueLogger.quick_log(f"resolution_y: {resolution_y}")

    UniqueLogger.quick_log(f"{top_left[0]}- {top_right[0]}, {top_left[1]}-{bottom_left[1]}, ")
    x_range = linspace(top_left[0], top_right[0], resolution_x)
    y_range = linspace(top_left[1], bottom_left[1], resolution_y)

    z_dir = top_left[2]

    hit_data = set()
    bounding_boxes_mappings: Dict[Any, List[Tuple[int, int]]] = defaultdict(list)
    # iterate over all X/Y coordinates
    for x in x_range:
        for y in y_range:
            # get current pixel vector from camera center to pixel
            pixel_vector = Vector((x, y, z_dir))
            # rotate that vector according to camera rotation
            pixel_vector.rotate(camera_quaternion)
            pixel_vector.normalized()

            is_hit, _, _, _, hit_obj, _ = scene.ray_cast(depsgraph, camera_translation, pixel_vector)

            if is_hit:
                hit_data.add(hit_obj)
                # Keep track of all hits
                if compute_bounding_boxes or compute_convex_hull:
                    x_normalized = (x - top_left[0]) / (top_right[0] - top_left[0]) * 2 - 1
                    y_normalized = (y - top_left[1]) / (bottom_left[1] - top_left[1]) * 2 - 1
                    bounding_boxes_mappings[hit_obj].append((x_normalized, y_normalized))


    if compute_bounding_boxes:
        return { obj: get_minimal_bounding_box_fast(points) for obj, points in bounding_boxes_mappings.items() }
    elif compute_convex_hull:
        return { obj: convex_hull(points) for obj, points in bounding_boxes_mappings.items() }
    else:
        return hit_data


def get_minimal_bounding_box_fast(points: List[Tuple[int, int]]):
    """

    :param points:
    :return:
    """
    if not points:
        return None
    x_min = x_max = points[0][0]
    y_min = y_max = points[0][1]

    for x, y in points[1:]:
        if x < x_min:
            x_min = x
        elif x > x_max:
            x_max = x

        if y < y_min:
            y_min = y
        elif y > y_max:
            y_max = y

    return x_min, y_min, x_max, y_max


def normalized_center_coordinate_to_pixel(x, y, width, height):
    pixel_x = (x + 1) * width / 2
    pixel_y = (1 - y) * height / 2  # The (1 - y) flips
    return pixel_x, pixel_y


def estimate_occlusion_3d(obj, camera, context, render, visible_bbox):
    """Compare 3D bbox projected area vs actual visible bbox"""

    points = list()
    bounding_box = obj.bound_box
    for threed_p in bounding_box:
        local_point = Vector((threed_p[0], threed_p[1], threed_p[2]))
        transform = obj.matrix_world
        point = transform @ local_point
        proj = project_3d_point(camera, point, context, render)
        points.append(proj)

    min_x = float(min(p[0] for p in points))
    max_x = float(max(p[0] for p in points))
    min_y = float(min(p[1] for p in points))
    max_y = float(max(p[1] for p in points))

    bbox_3d_area = compute_bbox_area((min_x, min_y, max_x, max_y))
    UniqueLogger.quick_log("3d before" + (min_x, min_y, max_x, max_y).__str__())
    UniqueLogger.quick_log("3d projected" + bbox_3d_area.__str__())

    # Compute the actually visible area
    bbox_visible_area = float(compute_bbox_area(visible_bbox))

    UniqueLogger.quick_log(f"3d visible{bbox_visible_area}")
    UniqueLogger.quick_log(f"3d projected{bbox_3d_area}")
    UniqueLogger.quick_log(f" pixls hee {visible_bbox}")

    occlusion = bbox_visible_area / bbox_3d_area if bbox_3d_area > 0 else 1.0
    return occlusion


def compute_bbox_area(bbox):
    """Compute area from (x_min, y_min, x_max, y_max)"""
    x_min, y_min, x_max, y_max = bbox
    return abs(x_max - x_min) * abs(y_max - y_min)

    return None


def project_3d_point(camera: bpy.types.Object,
                     p: Vector,
                     context,
                     render) -> Vector:

    # https://blender.stackexchange.com/questions/16472/how-can-i-get-the-cameras-projection-matrix
    """
    Given a camera and its projection matrix M;
    given p, a 3d point to project:

    Compute P’ = M * P
    P’= (x’, y’, z’, w')

    Ignore z'
    Normalize in:
    x’’ = x’ / w’
    y’’ = y’ / w’

    x’’ is the screen coordinate in normalised range -1 (left) +1 (right)
    y’’ is the screen coordinate in  normalised range -1 (bottom) +1 (top)

    :param context:
    :param camera: The camera for which we want the projection
    :param p: The 3D point to project
    :param render: The render settings associated to the scene.
    :return: The 2D projected point in normalized range [-1, 1] (left to right, bottom to top)
    """

    # Get the two components to calculate M
    modelview_matrix = camera.matrix_world.inverted()
    projection_matrix = camera.calc_matrix_camera(
        context.evaluated_depsgraph_get(),
        x = render.resolution_x,
        y = render.resolution_y,
        scale_x = render.pixel_aspect_x,
        scale_y = render.pixel_aspect_y,
    )

    # print(projection_matrix * modelview_matrix)
    # Compute P’ = M * P
    p1 = projection_matrix @ modelview_matrix @ Vector((p[0], p[1], p[2], 1))

    # Normalize in: x’’ = x’ / w’, y’’ = y’ / w’
    p2 = Vector((p1.x / p1.w, p1.y / p1.w))

    return p2