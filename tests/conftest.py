import sys
from unittest.mock import MagicMock

# Mock bpy submodules
sys.modules['bpy'] = MagicMock()
sys.modules['bpy.types'] = MagicMock()
sys.modules['bpy.props'] = MagicMock()
sys.modules['mathutils'] = MagicMock()