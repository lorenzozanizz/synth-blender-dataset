import sys
from math import sqrt
from unittest.mock import MagicMock


# Create a real Vector class since mathutils is mocked
class Vector:
    def __init__(self, values):
        self.values = list(values)

    def __getitem__(self, index):
        return self.values[index]

    def __setitem__(self, index, value):
        self.values[index] = value

    def __iter__(self):
        return iter(self.values)

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.values, other.values)])

    def __add__(self, other):
        return Vector([a + b for a, b in zip(self.values, other.values)])

    def __mul__(self, scalar):
        return Vector([v * scalar for v in self.values])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    @property
    def length(self):
        return sqrt(sum(v ** 2 for v in self.values))

    def __repr__(self):
        return f"Vector({self.values})"

    def __eq__(self, other):
        return self.values == other.values

# Mock bpy submodules
sys.modules['bpy'] = MagicMock()
sys.modules['bpy.types'] = MagicMock()
sys.modules['bpy.props'] = MagicMock()
sys.modules['nodeitems_utils'] = MagicMock()

# Mock mathutils with our real Vector
mathutils_mock = MagicMock()
mathutils_mock.Vector = Vector
sys.modules['mathutils'] = mathutils_mock