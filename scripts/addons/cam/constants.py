
# Package to store all constants of BlenderCAM

# PRECISION is used in most operations
PRECISION = 5

CHIPLOAD_PRECISION = 10

MAX_OPERATION_TIME = 3200000000  # seconds

G64_INCOMPATIBLE_MACHINES = ['GRBL']

BULLET_SCALE = 10000
# this is a constant for scaling the rigidbody collision world for higher precision from bullet library
CUTTER_OFFSET = (-5 * BULLET_SCALE, -5 * BULLET_SCALE, -5 * BULLET_SCALE)
# the cutter object has to be present in the scene , so we need to put it aside for sweep collisions,
# otherwise it collides itself.
