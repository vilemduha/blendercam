"""Fabex 'constants.py'

Package to store all constants of Fabex.
"""

# PRECISION is used in most operations
PRECISION = 5

CHIPLOAD_PRECISION = 10

MAX_OPERATION_TIME = 3200000000  # seconds

G64_INCOMPATIBLE_MACHINES = ["GRBL"]

# Upscale factor for higher precision from Bullet library - (Rigidbody Collision World)
BULLET_SCALE = 10000

# Cutter object must be present in the scene, so we need to put it aside for sweep collisions,
# otherwise it collides with itself.
CUTTER_OFFSET = (-5 * BULLET_SCALE, -5 * BULLET_SCALE, -5 * BULLET_SCALE)

EPS = 1.0e-32

NUMPYALG = False

SHAPELY = True

# DT = Bit diameter tolerance
DT = 1.025

USE_PROFILER = False

was_hidden_dict = {}

_IS_LOADING_DEFAULTS = False

TOLERANCE = 1e-9
BIG_FLOAT = 1e38

PY3 = True

OCL_SCALE = 1000.0

PYTHON_BIN = None

_PREVIOUS_OCL_MESH = None
