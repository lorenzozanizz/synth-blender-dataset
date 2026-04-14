from typing import Tuple, Dict, List, Union
import math

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
    return size*8


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

    def to_index(p, w):
        return (p[0] + p[1] * w) * 4

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


def convex_hull(points):
    """Graham scan algorithm for convex hull"""
    points = sorted(set(points))
    if len(points) <= 1:
        return points

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def draw_line(img, p0: tuple[int, int], p1: tuple[int, int],
              color: tuple[float, float, float, float],
              line_width: int = 1, channels: int = 4) -> None:
    """
    Draw a line from p0 to p1 on an image using Bresenham's algorithm.

    :param channels:
    :param img: Blender image object
    :param p0: Starting point (x, y)
    :param p1: Ending point (x, y)
    :param color: RGBA color tuple (0.0 to 1.0)
    :param line_width: Line thickness in pixels
    """
    width, height = img.size
    pixels = list(img.pixels)


    def draw_thick_pixel(x: int, y: int) -> None:
        """Draw a pixel with thickness"""
        for l_dx in range(-line_width // 2, (line_width + 1) // 2):
            for l_dy in range(-line_width // 2, (line_width + 1) // 2):
                if 0 < x + l_dx < width and 0< y + l_dy < height:
                    idx = to_index((x + l_dx, y + l_dy), width, channels=channels)
                    draw_color(pixels, color, idx)

    # Bresenham's line algorithm
    x0, y0 = int(p0[0]), int(p0[1])
    x1, y1 = int(p1[0]), int(p1[1])

    # Safety checks
    if x0 == x1 and y0 == y1:
        # Single point
        draw_thick_pixel(x0, y0)
        img.pixels[:] = pixels
        img.update()
        return

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x1 > x0 else -1
    sy = 1 if y1 > y0 else -1
    err = dx - dy

    x, y = x0, y0

    while True:
        draw_thick_pixel(x, y)

        if x == x1 and y == y1:
            break

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy

    img.pixels[:] = pixels
    img.update()


def simplify_by_angle(points, min_angle=10.0):
    """Remove points where the angle change is small"""

    if len(points) < 3:
        return points

    def angle_between(p1, p2, p3):
        """Calculate angle at p2"""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3

        v1 = (x1 - x2, y1 - y2)
        v2 = (x3 - x2, y3 - y2)

        dot = v1[0] * v2[0] + v1[1] * v2[1]
        det = v1[0] * v2[1] - v1[1] * v2[0]
        angle = abs(math.degrees(math.atan2(det, dot)))

        return min(angle, 180 - angle)

    simplified = [points[0]]
    for i in range(1, len(points) - 1):
        angle = angle_between(points[i - 1], points[i], points[i + 1])
        if angle > min_angle:
            simplified.append(points[i])
    simplified.append(points[-1])

    return simplified


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

#
BITMAP_FONT = {

    'A': ["01110", "10001", "11111", "10001", "10001"],
    'B': ["11110", "10001", "11100", "10001", "11110"],
    'C': ["01110", "10000", "10000", "10000", "01110"],
    'D': ["11100", "10010", "10001", "10010", "11100"],
    'E': ["11111", "10000", "11110", "10000", "11111"],
    'F': ["11111", "10000", "11110", "10000", "10000"],
    'G': ["01110", "10000", "10011", "10001", "01110"],
    'H': ["10001", "10001", "11111", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "01110"],
    'L': ["10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001"],
    'O': ["01110", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "11110", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10010", "01101"],
    'R': ["11110", "10001", "11110", "10010", "10001"],
    'S': ["01110", "10000", "01110", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "01010", "00100"],
    'Z': ["11111", "00010", "00100", "01000", "11111"],

    'a': ["00000", "01110", "10001", "10001", "01111"],
    'b': ["10000", "11110", "10001", "10001", "11110"],
    'c': ["00000", "01110", "10000", "10000", "01110"],
    'd': ["00001", "01111", "10001", "10001", "01111"],
    'e': ["00000", "01110", "11111", "10000", "01110"],
    'f': ["00110", "01000", "11110", "01000", "01000"],
    # Make the "g" bottom leg longer
    'g': ["00000", "01111", "10001", "01111", "00001", "00011", "01111"],
    'h': ["10000", "11110", "10001", "10001", "10001"],
    'i': ["00100", "00000", "00100", "00100", "00110"],
    # Make the l longer
    'l': ["00100", "00100", "00100", "00100", "00100"],
    'm': ["00000", "11010", "10101", "10101", "10101"],
    'n': ["00000", "11110", "10001", "10001", "10001"],
    'o': ["00000", "01110", "10001", "10001", "01110"],
    # Make the p "leg" longer
    'p': ["00000", "11110", "10001", "11110", "10000", "10000", "10000"],
    'q': ["00000", "01111", "10001", "01111", "00001"],
    'r': ["00000", "11110", "10000", "10000", "10000"],
    's': ["00000", "01110", "10000", "01110", "11110"],
    't': ["01000", "11110", "01000", "01000", "00110"],
    'u': ["00000", "10001", "10001", "10001", "01110"],
    'v': ["00000", "10001", "10001", "01010", "00100"],
    'z': ["00000", "11111", "00100", "01000", "11111"],

    '0': ["01110", "10001", "10001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "01110"],
    '2': ["01110", "00001", "00110", "01000", "11111"],
    '3': ["01110", "00001", "00110", "00001", "01110"],
    '4': ["10010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "11110"],
    '6': ["01110", "10000", "11110", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000"],
    '8': ["01110", "10001", "01110", "10001", "01110"],
    '9': ["01110", "10001", "01111", "00001", "01110"],

    '_': ["00000", "00000", "00000", "00000", "11111"],
    '.': ["00000", "00000", "00000", "00000", "00100"],
    '-': ["00000", "00000", "11111", "00000", "00000"],
    ' ': ["00000", "00000", "00000", "00000", "00000"],
}

EIGHT_BIT_BITMAP_FONT: Dict[str, List] = {

    'A': ["00111000", "01000100", "10000010", "11111110", "10000010", "10000010", "10000010"],
    'B': ["11111000", "10000100", "10000010", "11111000", "10000100", "10000010", "11111000"],
    'C': ["00111100", "01000010", "10000000", "10000000", "10000000", "01000010", "00111100"],
    'D': ["11110000", "10001000", "10000100", "10000010", "10000100", "10001000", "11110000"],
    'E': ["11111110", "10000000", "10000000", "11111100", "10000000", "10000000", "11111110"],
    'F': ["11111110", "10000000", "10000000", "11111100", "10000000", "10000000", "10000000"],
    'G': ["00111100", "01000010", "10000000", "10001110", "10000010", "01000010", "00111100"],
    'H': ["10000010", "10000010", "10000010", "11111110", "10000010", "10000010", "10000010"],
    'I': ["0111110", "0001000", "0001000", "0001000", "0001000", "0001000", "0111110"],
    'L': ["10000000", "10000000", "10000000", "10000000", "10000000", "10000000", "11111110"],
    'M': ["10000010", "11000110", "10101010", "10010010", "10000010", "10000010", "10000010"],
    'N': ["10000010", "11000010", "10100010", "10010010", "10001010", "10000110", "10000010"],
    'O': ["00111100", "01000010", "10000001", "10000001", "10000001", "01000010", "00111100"],
    'P': ["11111000", "10000100", "10000010", "11111000", "10000000", "10000000", "10000000"],
    'Q': ["00111100", "01000010", "10000001", "10000001", "10000101", "01000010", "00111101"],
    'R': ["11111000", "10000100", "10000010", "11111000", "10001000", "10000100", "10000010"],
    'S': ["00111100", "01000010", "10000000", "00111100", "00000001", "01000010", "00111100"],
    'T': ["11111110", "00010000", "00010000", "00010000", "00010000", "00010000", "00010000"],
    'U': ["10000010", "10000010", "10000010", "10000010", "10000010", "01000010", "00111100"],
    'V': ["10000010", "10000010", "10000010", "01000100", "01000100", "00101000", "00010000"],
    'Z': ["11111110", "00000010", "00000100", "00001000", "00010000", "00100000", "11111110"],

    'a': ["000000", "011100", "100010", "000010", "011110", "100010", "011100"],
    'b': ["10000000", "10000000", "10111000", "11000100", "10000010", "11000100", "10111000"],
    'c': ["00000000", "00111000", "01000100", "10000000", "10000000", "01000100", "00111000"],
    'd': ["00000010", "00000010", "00111010", "01000110", "10000010", "01000110", "00111010"],
    'e': ["0000000", "0011100", "0100010", "1111110", "1000000", "0100010", "0011100"],
    'f': ["00001100", "00010010", "00010000", "01111000", "00010000", "00010000", "00010000"],
    'g': ["00000000", "00111010", "01000110", "10000010", "01000110", "00111010", "00000010", "01111100"],
    'h': ["10000000", "10000000", "10111000", "11000100", "10000100", "10000100", "10000100"],
    'i': ["10", "00", "10", "10", "10", "10", "11"],
    'l': ["0100", "0100", "0100", "0100", "0100", "0110", "0011"],
    'm': ["00000000", "11010100", "10101010", "10101010", "10101010", "10101010", "10101010"],
    'n': ["0000000", "1011100", "1100010", "1000010", "1000010", "1000010", "1000010"],
    'o': ["00000000", "00111000", "01000100", "10000010", "10000010", "01000100", "00111000"],
    'p': ["00000000", "10111000", "11000100", "10000010", "11000100", "10111000", "10000000", "10000000", "10000000"],
    'q': ["00000000", "00111010", "01000110", "10000010", "01000110", "00111010", "00000010", "00000010", "00000010"],
    'r': ["00000000", "10111000", "11000100", "10000000", "10000000", "10000000", "10000000"],
    's': ["00000000", "00111000", "01000100", "01000000", "00111000", "00000100", "00111000"],
    't': ["001000", "111100", "001000", "001000", "001000", "001001", "000110"],
    'u': ["00000000", "10000100", "10000100", "10000100", "10000100", "10000110", "01111010"],
    'v': ["00000000", "10000100", "10000100", "10000100", "01001000", "01001000", "00110000"],
    'z': ["00000000", "11111110", "00000100", "00001000", "00010000", "00100000", "11111110"],

    '0': ["00111000", "01000100", "10000010", "10000010", "10000010", "01000100", "00111000"],
    '1': ["0100", "1100", "0100", "0100", "0100", "0100", "1110"],
    '2': ["00111000", "01000100", "00000010", "00000100", "00001000", "00010000", "01111110"],
    '3': ["00111000", "01000100", "00000010", "00011110", "00000010", "01000100", "00111000"],
    '4': ["01000100", "01000100", "01000100", "01111110", "00000100", "00000100", "00000100"],
    '5': ["01111110", "01000000", "01000000", "00111100", "00000010", "01000010", "00111100"],
    '6': ["00111000", "01000100", "10000000", "11111000", "10000100", "01000100", "00111000"],
    '7': ["11111110", "00000010", "00000100", "00001000", "00010000", "00100000", "01000000"],
    '8': ["00111000", "01000100", "10000010", "01111100", "10000010", "01000100", "00111000"],
    '9': ["00111000", "01000100", "10000010", "01111110", "00000010", "01000100", "00111000"],

    '_': ["0000000", "0000000", "0000000", "0000000", "0000000", "0000000", "1111111"],
    '.': ["000", "000", "000", "000", "000", "110", "100"],
    ',': ["000", "000", "000", "000", "000", "110", "010", "010", "100"],
    '-': ["00000000", "00000000", "00000000", "11111110", "00000000", "00000000", "00000000"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '%': ["10000010", "10000100", "00001000", "00010000", "00100000", "01000010", "10000010"],
}