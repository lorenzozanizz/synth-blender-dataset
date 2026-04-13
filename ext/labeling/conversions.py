"""


"""


def one_minus_one_centered_into_absolute_pixels_0y_top_invert(
        ximn_ymin_xmax_ymax: tuple[float, float, float, float], width: int, height: int
) -> tuple[int, int, int, int]:
    """ The resulting values are given so that the y values GROW as the point goes
    DOWN on the picture, e.g. the y value is 0 AT THE TOP.
    This is unlike blender image pixel system, where y value decreases as the point goes
    DOWN on the picture.

    :param ximn_ymin_xmax_ymax:
    :param width:
    :param height:
    :return:
    """
    # Unpack the values
    x_min, y_min, x_max, y_max = ximn_ymin_xmax_ymax

    x_min_px = int((x_min + 1) * width / 2)
    x_max_px = int((x_max + 1) * width / 2)
    y_min_px = int((y_max + 1) * height / 2)
    y_max_px = int((y_min + 1) * height / 2)

    return x_min_px, y_min_px, x_max_px, y_max_px

def one_minus_one_centered_into_absolute_pixels_0y_top(
        ximn_ymin_xmax_ymax: tuple[float, float, float, float], width: int, height: int
) -> tuple[int, int, int, int]:
    """ The resulting values are given so that the y values GROW as the point goes
    DOWN on the picture, e.g. the y value is 0 AT THE TOP.
    This is unlike blender image pixel system, where y value decreases as the point goes
    DOWN on the picture.

    :param ximn_ymin_xmax_ymax:
    :param width:
    :param height:
    :return:
    """
    # Unpack the values
    x_min, y_min, x_max, y_max = ximn_ymin_xmax_ymax

    x_min_px = int((x_min + 1) * width / 2)
    x_max_px = int((x_max + 1) * width / 2)
    y_min_px = int((y_min + 1) * height / 2)
    y_max_px = int((y_max + 1) * height / 2)

    return x_min_px, y_min_px, x_max_px, y_max_px