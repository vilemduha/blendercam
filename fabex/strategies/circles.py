from math import (
    pi,
    radians,
    sqrt,
    tan,
)
import sys

from shapely import affinity
from shapely.geometry import (
    LineString,
    MultiPolygon,
    Point,
    Polygon,
)
from shapely.ops import linemerge

import bpy
from mathutils import Euler, Vector

from ..bridges import use_bridges
from ..exception import CamException

from ..operators.curve_create_ops import generate_crosshatch

from ..utilities.chunk_builder import CamPathChunk
from ..utilities.chunk_utils import (
    chunks_to_mesh,
    chunks_refine,
    chunks_refine_threshold,
    set_chunks_z,
    curve_to_chunks,
    limit_chunks,
    shapely_to_chunks,
    sample_chunks_n_axis,
    sort_chunks,
)
from ..utilities.compare_utils import check_equal, unique
from ..utilities.geom_utils import circle, helix
from ..utilities.logging_utils import log
from ..utilities.operation_utils import get_operation_sources, check_min_z, get_layers
from ..utilities.parent_utils import (
    parent_child_distance,
    parent_child_poly,
)
from ..utilities.shapely_utils import shapely_to_curve
from ..utilities.silhouette_utils import (
    get_object_outline,
    get_operation_silhouette,
)
from ..utilities.simple_utils import (
    activate,
    delete_object,
    join_multiple,
    progress,
    remove_multiple,
    subdivide_short_lines,
)
from ..utilities.strategy_utils import add_pocket
from ..voronoi import compute_voronoi_diagram
