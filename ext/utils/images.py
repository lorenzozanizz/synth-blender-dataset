from .fonts import EIGHT_BIT_BITMAP_FONT_HEIGHT, EIGHT_BIT_BITMAP_FONT
from typing import Tuple, Union

class DrawableCanvas:
    """

    """

    def __init__(self, image, height, width, major_offset_x, major_offset_y):
        self.image = image
        self.height = height
        self.width = width

    def reserve_section(self) -> None:
        pass


def draw_color(pixel, color: Tuple[float, float, float, float], index: int) -> None:
    """

    :param pixel:
    :param color:
    :param index:
    :return:
    """
    if color:
        pixel[index]     = color[0]
        pixel[index + 1] = color[1]
        pixel[index + 2] = color[2]
        pixel[index + 3] = color[3]
    else:
        # Invert the pixel for visibility.
        pixel[index]     = 1 - pixel[index]
        pixel[index + 1] = 1 - pixel[index + 1]
        pixel[index + 2] = 1 - pixel[index + 2]
    return

def to_index(p, w, channels: int = 4) -> int:
    return (p[0] + p[1]*w)*channels


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

    (613.1937172774869, 908.4112149532709, 1306.8062827225133, 191.77570093457945)
    compute_bounding_boxes
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

    max_idx = to_index((width-1, height-1), width, channels=channels)

    def horizontal_line(point: tuple[int, int], line_length: int) -> None:
        nonlocal line_width, width
        for width_idx in range(line_width):
            idx0 = to_index( (point[0], point[1] + width_idx) , width, channels=channels)
            idx1 = to_index( (point[0] + line_length,  point[1] + width_idx) , width, channels=channels)
            for i in range(idx0, idx1 + 1*channels, channels):
                if i <= max_idx:
                    draw_color(pixels, color, i)

    def vertical_line(point: tuple[int, int], line_height: int) -> None:
        """Draw a vertical line starting at point, extending line_height pixels down"""
        for width_idx in range(line_width):
            start_x = point[0] + width_idx
            if start_x >= width:
                continue
            for y in range(point[1], point[1] + line_height):
                if y >= height:
                    continue
                idx = to_index((start_x, y), width, channels=channels)
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


def font_size_fit_box_perc(text: str, max_width: int, ratio: float = 1.0) -> int:
    """

    :return:
    """
    # A generic reference size, assuming the text width is pretty much linear in the width.
    base_size = 3
    base_width = estimate_text_pixel_width(text, base_size)

    scale = max_width / base_width
    font_size = max(2, int(base_size * scale * ratio))
    return font_size

def estimate_text_pixel_width(text: str, size: int) -> int:

    width = 0
    for char in text:
        if char not in EIGHT_BIT_BITMAP_FONT:
            char = '_'
        char_bitmap = EIGHT_BIT_BITMAP_FONT[char]
        char_width_pixels = len(char_bitmap[0])
        width += char_width_pixels * size + min(2, 1 * size // 2)
    return width


def estimate_text_pixel_height(_text: str, size: int) -> int:
    return size*EIGHT_BIT_BITMAP_FONT_HEIGHT


def draw_bitmap_text(img, text: str, position: tuple[int, int] = (0, 0),
                     color: Union[None, tuple[float, float, float, float]] = (1.0, 1.0, 1.0, 1.0),
                     size: int = 1,
                     channels: int = 4,
                     crop_width=None) -> None:
    """

    :param img:
    :param text:
    :param position:
    :param color:
    :param size:
    :param channels:
    """

    width, height = img.size
    pixels = list(img.pixels)

    x_offset, y_offset = position
    x_offset = int(x_offset)
    y_offset = int(y_offset)

    max_idx = to_index((width-1, height-1), width, channels=channels)

    current_x = x_offset

    for char_idx, char in enumerate(text):
        if char not in EIGHT_BIT_BITMAP_FONT:
            char = '_'

        # Extract the character
        char_bitmap = EIGHT_BIT_BITMAP_FONT[char]
        char_width_pixels = len(char_bitmap[0])

        for y, row in enumerate(char_bitmap):
            for x, pixel in enumerate(row):
                if pixel == '1':
                    # Scale up the character
                    for sy in range(size):
                        for sx in range(size):

                            pixel_x = current_x + x * size + sx
                            pixel_y = y_offset - y * size - sy
                            if not (0 <= pixel_x < width and 0 <= pixel_y < height):
                                continue
                            idx = int(to_index((pixel_x, pixel_y), width, channels=channels))
                            if idx <= max_idx:
                                draw_color(pixels, color,idx)

        current_x += char_width_pixels * size + min(2, 1*size // 2)

    img.pixels[:] = pixels
    img.update()


def fill_polygon(img, polygon, color):
    """Fill a polygon using scanline algorithm"""
    width, height = img.size
    pixels = list(img.pixels)

    def draw_pixel(x, y):
        if 0 <= x < width and 0 <= y < height:
            idx = to_index((x, y), width)
            pixels[idx] = color[0]
            pixels[idx + 1] = color[1]
            pixels[idx + 2] = color[2]
            pixels[idx + 3] = color[3]

    # For each scanline
    min_y = min(p[1] for p in polygon)
    max_y = max(p[1] for p in polygon)

    for y in range(int(min_y), int(max_y) + 1):
        # Find intersections with polygon edges
        intersections = []

        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]

            # Check if edge crosses scanline y
            if (p1[1] <= y < p2[1]) or (p2[1] <= y < p1[1]):
                # Calculate x intersection
                if p2[1] != p1[1]:
                    x = p1[0] + (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1])
                    intersections.append(x)

        # Sort and fill between pairs
        intersections.sort()
        for i in range(0, len(intersections), 2):
            if i + 1 < len(intersections):
                x_start = int(intersections[i])
                x_end = int(intersections[i + 1])
                for x in range(x_start, x_end):
                    draw_pixel(x, y)

    img.pixels[:] = pixels
    img.update()


def draw_thick_pixel(pixels, color, x: int, y: int, line_width: int, width:int, height: int, channels: int=4) -> None:
    """Draw a pixel with thickness"""
    for l_dx in range(-line_width // 2, (line_width + 1) // 2):
        for l_dy in range(-line_width // 2, (line_width + 1) // 2):
            if 0 < x + l_dx < width and 0< y + l_dy < height:
                idx = to_index((x + l_dx, y + l_dy), width, channels=channels)
                draw_color(pixels, color, idx)


def draw_line(pixels, p0: tuple[int, int], p1: tuple[int, int],
              color: tuple[float, float, float, float], width, height,
              line_width: int = 1, channels: int = 4, ) -> None:
    """
    Draw a line from p0 to p1 on an image using Bresenham's algorithm.

    :param height:
    :param width:
    :param pixels:
    :param channels:
    :param p0: Starting point (x, y)
    :param p1: Ending point (x, y)
    :param color: RGBA color tuple (0.0 to 1.0)
    :param line_width: Line thickness in pixels
    """

    # Bresenham's line algorithm
    # https://github.com/encukou/bresenham/blob/master/bresenham.py
    x0, y0 = int(p0[0]), int(p0[1])
    x1, y1 = int(p1[0]), int(p1[1])

    # Safety checks
    if x0 == x1 and y0 == y1:
        # Single point
        draw_thick_pixel(pixels, color, x0, y0, line_width, width, height, channels)
        return

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1
    err = dx - dy

    x, y = x0, y0

    # Prevent lock in from some strange error... who knows
    safety_idx = 0
    while True and safety_idx < max(2*width, 2*height):

        draw_thick_pixel(pixels, color, x, y, line_width, width, height, channels)

        if x == x1 and y == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

        safety_idx += 1


def draw_polygon(img, vertices: list[tuple[int, int]],
                 color: tuple[float, float, float, float],
                 line_width: int = 1, channels: int = 4, draw_wireframe:bool = True) -> None:
    """
    Draw a polygon from a list of vertices on an image.

    :param img: Blender image object
    :param vertices: List of (x, y) tuples defining polygon vertices in order
    :param color: RGBA color tuple (0.0 to 1.0)
    :param line_width: Line thickness in pixels
    :param channels: Number of color channels (default 4 for RGBA)
    """
    if len(vertices) < 2:
        return

    width, height = img.size
    pixels = list(img.pixels)
    # Draw lines between consecutive vertices, wrapping around to the first vertex.
    # NOTE that like all other such functions, it is assumed that the points follow blender convention
    # (e.g. the y=0 is at the bottom of the image)
    for i in range(len(vertices)):
        p0 = vertices[i]
        if draw_wireframe:
            draw_thick_pixel(pixels, color, p0[0], p0[1], line_width + 4, width, height, channels)

        p1 = vertices[(i + 1) % len(vertices)]  # Wraps to first vertex, if list has only one
        # point then this draws a point correctly (its handled inside draw_line)
        draw_line(pixels, p0, p1, color, width, height, line_width, channels)

    img.pixels[:] = pixels
    img.update()
