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
