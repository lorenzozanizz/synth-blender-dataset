from typing import Tuple

def draw_color(pixel, color: Tuple[float, float, float, float], index: int) -> None:
    """

    :param pixel:
    :param color:
    :param index:
    :return:
    """
    pixel[index]     = color[0]
    pixel[index + 1] = color[1]
    pixel[index + 2] = color[2]
    pixel[index + 3] = color[3]
    return

def draw_bounding_box(
        img, color: tuple[float, float, float, float],
        lower_point: Tuple[int, int], upper_point: Tuple[int, int], y_grows_up_to_down: bool = True,
        line_width: int = 1, channels: int = 4) -> None:
    """ Draw a bounding box on an image.

    Usages:
    POINTS =  (1000, 0, 1800, 50)
    POINTS_2 =  (1000, 50, 1800, 0)
    draw_bounding_box(img, COLOR, P0, P1, y_grows_up_to_down=True, line_width=5)
    draw_bounding_box(img, COLOR_2, P0_2, P1_2, y_grows_up_to_down=False, line_width=5)

    The above commands have the same effect, so that the y_grows_up_to_down parameters allows to switch
    between cv2 repr into blender pixel repr where a higher pixel has a greater y.

    :param img: Blender image object
    :param color: RGBA color tuple
    :param lower_point: (x_min, y_min)
    :param upper_point: (x_max, y_max)
    :param y_grows_up_to_down: If True, y increases downward (image coords). If False, y increases upward (math coords).
    :param line_width: Thickness of box lines
    :param channels: Number of color channels (usually 4 for RGBA)
    """
    width, height = img.size
    pixels = list(img.pixels)

    def to_index(p, w) -> int:
        return (p[0] + p[1]*w)*channels

    max_idx = to_index((width-1, height-1), width)

    def horizontal_line(point: tuple[int, int], line_length: int) -> None:
        nonlocal line_width, width
        for width_idx in range(line_width):
            idx0 = to_index( (point[0], point[1] + width_idx) , width)
            idx1 = to_index( (point[0] + line_length,  point[1] + width_idx) , width)
            for i in range(idx0, idx1, 4):
                if i <= max_idx:
                    draw_color(pixels, color, i)

    def vertical_line(point: tuple[int, int], line_height: int) -> None:
        """Draw a vertical line starting at point, extending line_height pixels down"""
        for width_idx in range(line_width):
            start_x = point[0] + width_idx
            for y in range(point[1], point[1] + line_height):
                idx = to_index((start_x, y), width)
                if idx <= max_idx:
                    draw_color(pixels, color, idx)

    # Handle coordinate system
    if y_grows_up_to_down:
        # Image coordinates: y increases downward
        p0 = lower_point
        p1 = upper_point
    else:
        # Math coordinates: y increases upward
        # Swap y coordinates
        p0 = (lower_point[0], upper_point[1])
        p1 = (upper_point[0], lower_point[1])

    box_width  = p1[0] - p0[0]
    box_height = p1[1] - p0[1]

    # Draw the two box horizontal lines
    horizontal_line((p0[0], p0[1]), box_width)
    horizontal_line((p0[0], p1[1]), box_width)

    # Draw the two box vertical lines
    vertical_line((p0[0], p0[1]), box_height)
    vertical_line((p1[0], p0[1]), box_height)

    img.pixels[:] = pixels
    # Should probably update image
    img.update()