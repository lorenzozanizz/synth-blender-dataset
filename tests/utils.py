from typing import Sequence

def equality_with_tolerance(vec_1: Sequence, vec_2: Sequence, dims: int = 3, tol=1e-5) -> bool:
    """ Check for equality between two vectors of dimension dims of numeric type
    withing a certain tolerance. (e.g. to compare positions, rotations...)

    :param vec_1: The first vector
    :param vec_2: The second vector
    :param dims: The number of dimensions to check
    :param tol: The tolerance
    :return: True if the two vectors are equal, False otherwise
    """
    mae = 0
    for i in range(dims):
        mae += abs(vec_1[i]-vec_2[i])
    return mae < tol